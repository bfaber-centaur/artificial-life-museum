"""Build the §9 refinement variants of one encounter and its matched controls.

    python research/experiments/REEF-numerics/make_variants.py \
        --manifest E.json --state E.npy --state-g G.npy --state-s S.npy --out OUT_DIR [--big-n 512]

Takes the t = 0 states of an encounter (E) and its two isolated controls
(G-alone, S-alone), all on the same N x N torus, and writes three variants of
each, so every altered setting has its own matched controls:

- ``T20``   same states, T = 20 (dt halved), same horizon in tu.
- ``R26``   every cell replicated as a 2 x 2 block (np.kron), R = 26, N doubled:
            the same world in R units; the physical seed is not resampled.
- ``N<big>`` same R and seed size; the three states get one common roll that
            puts an all-zero row and column band on the seam, then are embedded
            at the centre of a big-N zero world, so separation, phase and
            relative placement are unchanged.

The transform is identical for E, G and S, and E == G + S is checked before and
after when it held for the input (it holds when supports are disjoint and no
cell clips). Output: OUT_DIR/<variant>/{E,G,S}.npy and {E,G,S}.json manifests in
the REEF schema shape (status "prepared"; commit and sha256 filled; nothing is
simulated here). Note for T20: the glider was settled at T10, so its first tu
at T20 is a fresh transient; the T20 controls measure that and the encounter is
compared against them, not against the T10 controls.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np

from replay import REPO, file_sha256, git_state, load_state, sha256


def zero_band(occupied: np.ndarray) -> tuple[int, int]:
    """(start, width) of the longest cyclic run of empty lines."""
    n = len(occupied)
    if occupied.all():
        raise ValueError("no all-zero row/column: bodies span the whole torus on one axis")
    best, best_start, run, start = 0, 0, 0, 0
    for k in range(2 * n):
        if occupied[k % n]:
            run = 0
        else:
            if run == 0:
                start = k
            run += 1
            if run > best:
                best, best_start = min(run, n), start % n
    return best_start, best


def embed_shift(E: np.ndarray) -> tuple[int, int, dict]:
    """Roll (dy, dx) that moves the middle of the widest empty band onto index 0."""
    out, info = [], {}
    for axis, name in ((0, "rows"), (1, "cols")):
        occ = (E != 0).any(axis=1 - axis)
        s, w = zero_band(occ)
        mid = (s + w // 2) % len(occ)
        out.append(-mid)
        info[f"empty_{name}"] = int(w)
    return out[0], out[1], info


def variant_states(kind: str, states: dict, big_n: int) -> tuple[dict, dict]:
    N = states["E"].shape[0]
    if kind == "T20":
        return {k: v.copy() for k, v in states.items()}, {"transform": "identity", "T": 20}
    if kind == "R26":
        block = np.ones((2, 2))
        return ({k: np.kron(v, block) for k, v in states.items()},
                {"transform": "np.kron(A, ones((2, 2)))", "R": 26, "N": 2 * N})
    if kind == f"N{big_n}":
        if big_n <= N:
            raise ValueError("big world must be larger")
        dy, dx, info = embed_shift(states["E"])
        o = (big_n - N) // 2
        out = {}
        for k, v in states.items():
            big = np.zeros((big_n, big_n))
            big[o:o + N, o:o + N] = np.roll(v, (dy, dx), (0, 1))
            out[k] = big
        return out, {"transform": f"np.roll(A, ({dy}, {dx}), (0, 1)) then embed at offset ({o}, {o})",
                     "N": big_n, "roll": [dy, dx], "offset": [o, o], **info}
    raise ValueError(kind)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, help="encounter manifest (REEF schema)")
    ap.add_argument("--state", required=True, help="encounter t=0 state")
    ap.add_argument("--state-g", required=True, help="G-alone t=0 state")
    ap.add_argument("--state-s", required=True, help="S-alone t=0 state")
    ap.add_argument("--manifest-g", default=None)
    ap.add_argument("--manifest-s", default=None)
    ap.add_argument("--big-n", type=int, default=512)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    mE = json.loads(Path(a.manifest).read_text())
    srcs = {"E": Path(a.state), "G": Path(a.state_g), "S": Path(a.state_s)}
    states = {k: load_state(p) for k, p in srcs.items()}
    if len({v.shape for v in states.values()}) != 1:
        raise ValueError("E, G and S must share one shape")
    want = mE.get("inputs", {}).get("initial_state_sha256")
    if want and want != sha256(states["E"]):
        raise ValueError("encounter state sha256 does not match its manifest")
    superpose = bool(np.array_equal(states["E"], states["G"] + states["S"]))
    ids = {"E": mE["run_id"], "G": mE.get("controls", {}).get("G", mE["run_id"] + "-G"),
           "S": mE.get("controls", {}).get("S", mE["run_id"] + "-S")}
    srcman = {"E": a.manifest, "G": a.manifest_g, "S": a.manifest_s}
    gs = git_state()
    report = {"commit": gs["commit"], "commit_dirty": gs["dirty"], "E_equals_G_plus_S_input": superpose,
              "inputs": {k: {"path": str(p), "sha256": sha256(states[k])} for k, p in srcs.items()}, "variants": {}}

    for kind in ("T20", "R26", f"N{a.big_n}"):
        vs, info = variant_states(kind, states, a.big_n)
        d = Path(a.out) / kind
        d.mkdir(parents=True, exist_ok=True)
        rep = {**info, "E_equals_G_plus_S": bool(np.array_equal(vs["E"], vs["G"] + vs["S"])),
               "mass_ratio": {k: float(vs[k].sum() / states[k].sum()) for k in vs if states[k].sum()}}
        for k, A in vs.items():
            np.save(d / f"{k}.npy", A)
            m = copy.deepcopy(json.loads(Path(srcman[k]).read_text())) if srcman[k] else copy.deepcopy(mE)
            m["run_id"] = f"{ids[k]}-{kind}"
            m["kind"] = "check" if k == "E" else {"G": "control_G", "S": "control_S"}[k]
            m["lane"] = "numerics"
            m["commit"] = gs["commit"]
            if "T" in info:
                m["rule"]["T"] = info["T"]
            if "R" in info:
                m["rule"]["R"] = info["R"]
            if "N" in info:
                m["world"]["N"] = info["N"]
            m["inputs"] = {"source_run_id": ids[k], "source_state_sha256": sha256(states[k]),
                           "transform": info["transform"], "initial_state_sha256": sha256(A),
                           "path": str((d / f"{k}.npy").relative_to(REPO)) if d.resolve().is_relative_to(REPO) else str(d / f"{k}.npy"),
                           "geometry": mE.get("inputs", {}).get("geometry")}
            if k == "E":
                m["controls"] = {"G": f"{ids['G']}-{kind}", "S": f"{ids['S']}-{kind}"}
            for key in ("final_state_sha256", "wall_s", "result", "outputs"):
                m.pop(key, None)
            m["status"] = "prepared"
            m["command"] = None
            (d / f"{k}.json").write_text(json.dumps(m, indent=1) + "\n")
            rep.setdefault("files", {})[k] = {"state_sha256": sha256(A), "npy_file_sha256": file_sha256(d / f"{k}.npy")}
        report["variants"][kind] = rep
    (Path(a.out) / "variants.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
