"""SPECIES-scout: a quick, cheap pass over candidate regions of classic Lenia rule space.

Goal: decide where a deeper species hunt should dig. For each sampled rule we run a batch
of random seeds side by side (batched FFT, same update as alm.lenia), and classify each
world at the horizon:

  DIED      total mass < 1 cell
  FILLED    more than 25 % of cells above 0.1 (world-filling lattice / reef-like state)
  CHAOS     alive, not filled, but not a compact body (too many or too big components)
  BODY      1..3 compact components, each smaller than 6R across: a species candidate
            subclassified by the shift-correlation between t_end - 20 tu and t_end:
              GLIDER  corr > 0.9 and peak shift > 0.5 R
              STATIC  corr > 0.9 and shift <= 0.5 R
              OSC     corr <= 0.9 (rotating, breathing, morphing)

Regions:
  R1  poly/poly single ring, R13 T10, mu-sigma band around the Orbium niche;
      seeds = random soups and mutated S001 Orbia
  R2  poly/poly multi-ring kernels (2 or 3 shells), R18 T10, random shell heights
  R5  exp/exp multi-ring kernels (2-3 shells), R18 T10, sigma = mu x 0.07-0.13 (added after R2)
  R4  exp kernel families (exp/exp and mixed exp/poly), single and double ring, R13 T10;
      the pinned catalogue has only 5 exp-kernel entries
(R3, reef / fractal debris, is not simulated here: see SCOUT.md.)

Usage: python scout.py run REGION NRULES [--seed S] [--jobs J]  -> scout-REGION.jsonl
       python scout.py summary
This is a scouting instrument only: nothing here supports a claim on its own.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import ndimage

from alm.lenia import Rule, growth, kernel
from alm.specimens import load

HERE = Path(__file__).resolve().parent
N = 256
BATCH = 8
HORIZON_TU = 200
LAG_TU = 20
SHELLS = [1.0, 11 / 12, 5 / 6, 3 / 4, 2 / 3, 1 / 2, 1 / 3, 1 / 4, 1 / 6, 0.0]


def sample_rule(region: str, rng: np.random.Generator) -> Rule:
    if region == "R1":
        mu = rng.uniform(0.11, 0.30)
        sigma = mu * rng.uniform(0.07, 0.20)
        return Rule(R=13, T=10, mu=round(mu, 4), sigma=round(sigma, 4))
    if region == "R2":
        nb = int(rng.integers(2, 4))
        beta = [1.0] + [float(rng.choice(SHELLS)) for _ in range(nb - 1)]
        rng.shuffle(beta)
        if beta[-1] == 0.0:  # an outer empty shell just shrinks R
            beta[-1] = 1 / 2
        mu = rng.uniform(0.12, 0.42)
        sigma = mu * rng.uniform(0.07, 0.20)
        return Rule(R=18, T=10, mu=round(mu, 4), sigma=round(sigma, 4), beta=tuple(beta))
    if region == "R4":
        kn, gn = [("exp", "exp"), ("exp", "poly"), ("poly", "exp")][int(rng.integers(3))]
        beta = (1.0,) if rng.random() < 0.6 else tuple(rng.permutation([1.0, float(rng.choice(SHELLS[1:-1]))]))
        mu = rng.uniform(0.10, 0.40)
        sigma = mu * rng.uniform(0.07, 0.20)
        return Rule(R=13, T=10, mu=round(mu, 4), sigma=round(sigma, 4), beta=beta, kernel=kn, growth=gn)
    if region == "R5":  # exp/exp multi-ring, tighter sigma band (lesson from R2)
        nb = int(rng.integers(2, 4))
        beta = [1.0] + [float(rng.choice(SHELLS[1:-1])) for _ in range(nb - 1)]
        rng.shuffle(beta)
        mu = rng.uniform(0.10, 0.40)
        sigma = mu * rng.uniform(0.07, 0.13)
        return Rule(R=18, T=10, mu=round(mu, 4), sigma=round(sigma, 4), beta=tuple(beta), kernel="exp", growth="exp")
    raise ValueError(region)


def seeds(region: str, rule: Rule, rng: np.random.Generator) -> np.ndarray:
    A = np.zeros((BATCH, N, N))
    yy, xx = np.mgrid[:N, :N] - N // 2
    orb = load("S001").cells / 255.0
    for b in range(BATCH):
        if region == "R1" and b % 2 == 1:  # mutated Orbium: noise + random rescale of levels
            h, w = orb.shape
            patch = np.clip(orb * rng.uniform(0.8, 1.2) + rng.normal(0, 0.15, orb.shape) * (orb > 0), 0, 1)
            A[b, N // 2 - h // 2:N // 2 - h // 2 + h, N // 2 - w // 2:N // 2 - w // 2 + w] = patch
        else:  # random soup in a disk of radius 1..2 R
            rad = rule.R * rng.uniform(1.0, 2.0)
            disk = (yy**2 + xx**2) < rad**2
            A[b][disk] = rng.uniform(0, 1, disk.sum()) * rng.uniform(0.5, 1.0)
    return A


def classify(A_lag: np.ndarray, A: np.ndarray, R: int) -> dict:
    mass = float(A.sum())
    if mass < 1:
        return {"cls": "DIED", "mass": mass}
    occ = float((A > 0.1).mean())
    if occ > 0.25:
        return {"cls": "FILLED", "mass": mass, "occ": occ}
    lab, n = ndimage.label(A > 0.1, structure=np.ones((3, 3)))
    # merge labels across periodic edges
    for i in range(N):
        for a, b in ((lab[i, 0], lab[i, -1]), (lab[0, i], lab[-1, i])):
            if a and b and a != b:
                lab[lab == b] = a
    ids = [i for i in np.unique(lab) if i]
    comp_mass = ndimage.sum(A, lab, ids) if ids else []
    big = [i for i, m in zip(ids, comp_mass) if m > 0.05 * mass]
    sizes = []
    for i in big:
        ys, xs = np.nonzero(lab == i)
        ext = max(np.ptp(ys), np.ptp(xs)) + 1
        sizes.append(int(ext))
    if not (1 <= len(big) <= 3) or max(sizes) > 6 * R:
        return {"cls": "CHAOS", "mass": mass, "occ": occ, "ncomp": len(big), "maxext_R": max(sizes or [0]) / R}
    # shift-correlation between lagged and final state
    F = np.fft.irfft2(np.fft.rfft2(A) * np.conj(np.fft.rfft2(A_lag)), s=A.shape)
    corr = float(F.max() / np.sqrt((A**2).sum() * (A_lag**2).sum() + 1e-12))
    dy, dx = np.unravel_index(F.argmax(), F.shape)
    dy, dx = (dy + N // 2) % N - N // 2, (dx + N // 2) % N - N // 2
    shift = float(np.hypot(dy, dx)) / R
    sub = "OSC" if corr <= 0.9 else ("GLIDER" if shift > 0.5 else "STATIC")
    return {"cls": "BODY", "sub": sub, "mass": mass, "occ": occ, "ncomp": len(big),
            "maxext_R": max(sizes) / R, "corr": corr, "shift_R": shift}


def run_rule(args) -> dict:
    region, k, seed = args
    rng = np.random.default_rng([seed, k])
    rule = sample_rule(region, rng)
    A = seeds(region, rule, rng)
    khat = np.fft.rfft2(kernel((N, N), rule))
    steps, lag = int(HORIZON_TU * rule.T), int(LAG_TU * rule.T)
    A_lag = None
    for t in range(steps):
        U = np.fft.irfft2(np.fft.rfft2(A) * khat, s=(N, N))
        A = np.clip(A + growth(rule.growth, U, rule.mu, rule.sigma) * rule.dt, 0.0, 1.0)
        if t == steps - lag - 1:
            A_lag = A.copy()
        if t % 200 == 199 and all(m < 1 or o > 0.25 for m, o in zip(A.sum(axis=(1, 2)), (A > 0.1).mean(axis=(1, 2)))):
            A_lag = A.copy()
            break
    out = [classify(A_lag[b], A[b], rule.R) for b in range(BATCH)]
    snap_dir = HERE / "snaps" / region
    snap_dir.mkdir(parents=True, exist_ok=True)
    keep = [b for b, o in enumerate(out) if o["cls"] == "BODY"]
    if keep:
        np.savez_compressed(snap_dir / f"{seed}-{k}.npz", A=A[keep].astype(np.float32), idx=np.array(keep))
    return {"region": region, "seed": seed, "k": k, "rule": rule.to_dict(), "worlds": out}


def main(argv):
    if argv[0] == "run":
        region, n = argv[1], int(argv[2])
        seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 0
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 4
        with open(HERE / f"scout-{region}.jsonl", "a") as f, ProcessPoolExecutor(jobs) as ex:
            for r in ex.map(run_rule, [(region, k, seed) for k in range(n)]):
                f.write(json.dumps(r) + "\n")
                f.flush()
        return 0
    if argv[0] == "summary":
        for p in sorted(HERE.glob("scout-*.jsonl")):
            rows = [json.loads(l) for l in p.read_text().splitlines()]
            from collections import Counter
            c = Counter()
            rules_with = Counter()
            for r in rows:
                kinds = set()
                for w in r["worlds"]:
                    key = w["cls"] + ("/" + w["sub"] if "sub" in w else "")
                    c[key] += 1
                    kinds.add(key)
                for kk in kinds:
                    rules_with[kk] += 1
            nw = sum(c.values())
            print(f"{p.stem}: {len(rows)} rules, {nw} worlds")
            for kk, v in sorted(c.items()):
                print(f"   {kk:14s} worlds {v:4d} ({100*v/nw:4.1f}%)  rules {rules_with[kk]:3d}")
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
