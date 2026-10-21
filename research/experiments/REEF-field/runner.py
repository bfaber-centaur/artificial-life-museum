"""REEF encounter runner: encounter E, glider-alone G and ring-alone S stepped in lockstep.

One process steps three worlds with identical rule, numerics, world and horizon:
E = roll(G0) + roll(S0) (disjoint supports, checked), G = glider only, S = ring only. Per step it
records whole-world observables for each world and the superposition residual
max|E - (G + S)| (protocol §6.3). It stores raw arrays for the reviewed tracker; it does not
classify outcomes.

Outputs in runs/<run_id>/ (frames are not committed; see .gitignore):
  trace.npz      per-step series (mass, residual, component counts, provisional contact flag)
  checkpoints.npz float64 E/G/S every 1 tu plus t = 0, provisional contact, contact + 10 tu, final
  frames.npz     float32 E and G every step (tracker input)
  manifest.json  schema REEF/manifest.schema.json; also appended to runs.jsonl

Provisional contact (runner only, not the scored t_c): first step at which one connected
component of the E support (A > theta_s, 8-connected, torus) overlaps both the G-alone and the
S-alone supports.

Usage (repo root):
  python research/experiments/REEF-field/runner.py --run-id REEF-SHAM --snapshot GA \
      --ring-shift DY DX [--N 256] [--H 50] [--kind sham]
Encounters are refused unless --protocol-addendum names the lead's Gate A addendum SHA.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
import time

import numpy as np
from scipy import ndimage

from reefcore import HERE, RULE, load_state, provenance, sha_file
from alm.lenia import Lenia
from alm.provenance import state_sha256

THETA_S = 0.01
EIGHT = np.ones((3, 3), bool)


def torus_label(mask):
    """8-connected labels on the torus (labels merged across the wrap); returns (labels, n)."""
    lab, n = ndimage.label(mask, structure=EIGHT)
    if n == 0:
        return lab, 0
    parent = np.arange(n + 1)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for s in (-1, 0, 1):
        for a, b in zip(lab[:, -1], np.roll(lab[:, 0], s)):
            if a and b:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
        for a, b in zip(lab[-1, :], np.roll(lab[0, :], s)):
            if a and b:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
    roots = np.array([find(i) for i in range(n + 1)])
    uniq, new = np.unique(roots[1:], return_inverse=True)
    lut = np.concatenate([[0], new + 1])
    return lut[lab], len(uniq)


def embed(A, N):
    """Centre a 256 state in an N x N world (exact: the padding is zeros)."""
    n = A.shape[0]
    if N == n:
        return A.copy()
    if N < n:
        raise ValueError("cannot shrink")
    B = np.zeros((N, N))
    o = (N - n) // 2
    B[o : o + n, o : o + n] = A
    return B


def build(snapshot, ring_shift, N):
    G0, gm = load_state(HERE / "seeds" / f"{snapshot}.npy") if snapshot else (None, None)
    S0, sm = load_state(HERE / "seeds" / "S103.npy") if ring_shift is not None else (None, None)
    G = embed(G0, N) if G0 is not None else np.zeros((N, N))
    S = np.roll(embed(S0, N), tuple(ring_shift), axis=(0, 1)) if S0 is not None else np.zeros((N, N))
    overlap = bool(((G > 0) & (S > 0)).any())
    if overlap:
        raise ValueError("glider and ring supports overlap at t = 0")
    return G, S, gm, sm


def run(args):
    t_wall = time.time()
    rule = RULE
    N, steps, T = args.N, int(args.H * RULE.T), int(RULE.T)
    G0, S0, gm, sm = build(args.snapshot, args.ring_shift, N)
    E0 = G0 + S0
    out_dir = HERE / "runs" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    worlds = {"E": Lenia(rule, E0), "G": Lenia(rule, G0), "S": Lenia(rule, S0)}
    names = list(worlds)
    mass = {k: np.empty(steps + 1) for k in names}
    ncomp = {k: np.empty(steps + 1, int) for k in names}
    resid = np.empty(steps + 1)
    resid_l1 = np.empty(steps + 1)
    contact_flag = np.zeros(steps + 1, bool)
    frames = {"E": np.empty((steps + 1, N, N), np.float32), "G": np.empty((steps + 1, N, N), np.float32)}
    ckpt = {}
    t_contact = None

    def observe(t):
        nonlocal t_contact
        A = {k: worlds[k].A for k in names}
        for k in names:
            mass[k][t] = A[k].sum() / rule.R**2
            lab, n = torus_label(A[k] > THETA_S)
            ncomp[k][t] = n
            if k == "E":
                labE = lab
        d = A["E"] - (A["G"] + A["S"])
        resid[t] = np.abs(d).max()
        resid_l1[t] = np.abs(d).sum() / rule.R**2
        gs, ss = A["G"] > THETA_S, A["S"] > THETA_S
        both = np.intersect1d(np.unique(labE[gs]), np.unique(labE[ss]))
        contact_flag[t] = bool((both > 0).any())
        if contact_flag[t] and t_contact is None:
            t_contact = t
        frames["E"][t] = A["E"]
        frames["G"][t] = A["G"]
        if t % T == 0 or t == steps or t == t_contact or (t_contact is not None and t == t_contact + 10 * T):
            for k in names:
                ckpt[f"{k}_{t:05d}"] = A[k].copy()

    observe(0)
    for t in range(1, steps + 1):
        for w in worlds.values():
            w.step()
        observe(t)
    wall_sim = time.time() - t_wall

    np.savez_compressed(out_dir / "trace.npz", **{f"mass_{k}": mass[k] for k in names},
                        **{f"ncomp_{k}": ncomp[k] for k in names},
                        residual_max=resid, residual_l1=resid_l1, contact_flag=contact_flag)
    np.savez_compressed(out_dir / "checkpoints.npz", **ckpt)
    np.savez_compressed(out_dir / "frames.npz", **frames)
    wall = time.time() - t_wall

    prov = provenance()
    finals = {k: state_sha256(worlds[k].A) for k in names}
    outputs = {p.name: {"path": str(p.relative_to(HERE.parents[2])), "sha256": sha_file(p)}
               for p in sorted(out_dir.glob("*.npz"))}
    base = {
        "lane": "field",
        "commit": prov["code"]["git_commit"],
        "engine": "alm",
        "rule": {"kernel": rule.kernel, "growth": rule.growth, "beta": list(rule.beta), "mu": rule.mu,
                 "sigma": rule.sigma, "R": rule.R, "T": int(rule.T), "update": "euler+clip", "dtype": "float64"},
        "world": {"N": N, "boundary": "periodic"},
        "horizon_tu": args.H,
        "command": "python research/experiments/REEF-field/runner.py " + " ".join(map(shlex.quote, sys.argv[1:])),
        "env": {**prov["env"], "threads": "OMP/OPENBLAS/MKL=1", "git_dirty": prov["code"]["git_dirty"],
                "embedded_from_N256": N != 256},
        "outputs": outputs,
        "wall_s": wall,
        "status": "ok",
    }
    glider = None if gm is None else {"snapshot": args.snapshot, "state_sha256": gm["state_sha256"],
                                      "path": f"research/experiments/REEF-field/seeds/{args.snapshot}.npy",
                                      "shift_cells": [(N - 256) // 2] * 2}
    ring = None if sm is None else {"state_sha256": sm["state_sha256"],
                                    "path": "research/experiments/REEF-field/seeds/S103.npy",
                                    "shift_cells": [int(args.ring_shift[0]) + (N - 256) // 2,
                                                    int(args.ring_shift[1]) + (N - 256) // 2]}
    geom = json.loads(args.geometry) if args.geometry else {}
    manifest = dict(base, run_id=args.run_id, kind=args.kind,
                    inputs={"glider": glider, "ring": ring, "initial_state_sha256": state_sha256(E0),
                            "geometry": geom,
                            "component_initial_sha256": {"G": state_sha256(G0), "S": state_sha256(S0)}},
                    controls={"G": f"REEF-CTRL-{args.snapshot}" if N == 256 else f"{args.run_id}:G (lockstep)",
                              "S": (args.run_id[:-2] + "-S") if args.run_id.endswith("-E") else f"{args.run_id}:S (lockstep)",
                              "mapping": "G-alone shared per snapshot (D-004), reproduced bitwise by the lockstep G; "
                                         "S-alone = lockstep S at this realised ring position"},
                    final_state_sha256=finals["E"],
                    lockstep_final_state_sha256=finals,
                    schedule={"seed": args.schedule_seed, "position": args.schedule_position},
                    result={"provisional_contact_tu": None if t_contact is None else t_contact / T,
                            "residual_max_before_contact": float(resid[: t_contact or steps + 1].max()),
                            "residual_max_overall": float(resid.max()),
                            "ncomp_E_final": int(ncomp["E"][-1]),
                            "mass_final": {k: float(mass[k][-1]) for k in names},
                            "wall_sim_s": wall_sim, "wall_total_s": wall},
                    notes=args.notes or "")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=float) + "\n")
    with open(HERE / "runs.jsonl", "a") as f:
        f.write(json.dumps(manifest, default=float, separators=(",", ":")) + "\n")
    print(json.dumps(manifest["result"], default=float))
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--kind", default="encounter", choices=["encounter", "sham", "test"])
    p.add_argument("--snapshot", choices=["GA", "GB"], required=True)
    p.add_argument("--ring-shift", nargs=2, type=int, required=True, metavar=("DY", "DX"))
    p.add_argument("--N", type=int, default=256)
    p.add_argument("--H", type=float, default=50)
    p.add_argument("--geometry", default="", help="JSON object recorded as inputs.geometry")
    p.add_argument("--schedule-seed", type=int, default=20261020)
    p.add_argument("--schedule-position", type=int, default=-1)
    p.add_argument("--protocol-addendum", default="", help="Gate A addendum commit SHA (required for encounters)")
    p.add_argument("--notes", default="")
    args = p.parse_args(argv)
    if args.kind == "encounter" and not args.protocol_addendum:
        p.error("encounters are frozen until the Gate A addendum SHA is given (--protocol-addendum)")
    if args.protocol_addendum:
        args.notes = (args.notes + f" protocol addendum {args.protocol_addendum}").strip()
    run(args)


if __name__ == "__main__":
    main()
