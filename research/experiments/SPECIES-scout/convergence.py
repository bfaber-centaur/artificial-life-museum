"""Transplant matrix for the convergence exhibit.

Four bodies, each built deterministically (no snapshots):
  orbium    S001 cells on 256^2, settled 200 tu under its home rule (poly/poly mu .15 s .015 R13)
  crescent  scout R4 seed (1, 56) world 2, settled 200 tu under poly/exp mu .2817 s .0406 R13
  starA     scout R5 seed (1, 27) world 3, settled 200 tu under exp/exp mu .1803 s .0204 b[1,1/6,11/12] R18
  starB     scout R5 seed (1, 55) world 0, settled 200 tu under exp/exp mu .1722 s .0158 b[1,1/6,2/3] R18
Each settled body is moved, unchanged, into all four kernel/growth families (pp, pe, ep, ee) with the same
R, T, mu and shells, at sigma = home sigma x f for f in FACTORS. It runs for 200 tu and is classified with
scout.classify. Everything uses alm.lenia.Lenia.

Usage: python convergence.py check   -> confirms single-world seeds match the batched scout bitwise
       python convergence.py run     -> convergence.jsonl + conv/<body>-<fam>-<i>.npy (final states)
       python convergence.py sheet   -> convergence-matrix.png
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from alm.lenia import Lenia, Rule
from alm.provenance import state_sha256
from alm.specimens import load
from scout import HERE, N, classify, sample_rule, seeds

FAMS = {"pp": ("poly", "poly"), "pe": ("poly", "exp"), "ep": ("exp", "poly"), "ee": ("exp", "exp")}
FACTORS = [round(0.70 + 0.03 * i, 2) for i in range(21)]  # 0.70 .. 1.30
SETTLE_TU = 200
TEST_TU = 200

BODIES = {
    "orbium": dict(region=None, rule=Rule(R=13, T=10, mu=0.15, sigma=0.015)),
    "crescent": dict(region="R4", key=(1, 56), world=2),
    "starA": dict(region="R5", key=(1, 27), world=3),
    "starB": dict(region="R5", key=(1, 55), world=0),
}
CATALOGUE_COUSIN = {"orbium": "O2u Orbium unicaudatus (= S001)", "crescent": "P5cf Pentapteryx cavus furiosus / P4cf (hollow Pterifera)",
                    "starA": "3R5m Asterium metamorpha", "starB": "3R5m Asterium metamorpha"}


def home(name: str) -> tuple[Rule, np.ndarray, str]:
    """Home rule, initial state, and a description of how it was built."""
    b = BODIES[name]
    if b["region"] is None:
        return b["rule"], load("S001").place(N), "S001 cells centred on 256^2"
    rng = np.random.default_rng(list(b["key"]))
    rule = sample_rule(b["region"], rng)
    A = seeds(b["region"], rule, rng)[b["world"]]
    return rule, A, (f"SPECIES-scout {b['region']} soup: numpy default_rng({list(b['key'])}), sample_rule then seeds(), "
                     f"world {b['world']} of 8, 256^2")


def settled(name: str) -> tuple[Rule, np.ndarray]:
    rule, A, _ = home(name)
    L = Lenia(rule, A)
    for _ in range(int(SETTLE_TU * rule.T)):
        L.step()
    return rule, L.A


def check() -> int:
    bad = 0
    for name, b in BODIES.items():
        if b["region"] is None:
            continue
        rule, A = settled(name)
        z = np.load(HERE / "snaps" / b["region"] / f"{b['key'][0]}-{b['key'][1]}.npz")
        S = z["A"][list(z["idx"]).index(b["world"])]
        same = np.array_equal(A.astype(np.float32), S)
        bad += not same
        print(name, rule, "bitwise == scout snapshot" if same else "DIFFERS", state_sha256(A))
    return bad


def one(args):
    name, fam, i = args
    rule0, A = settled(name)
    k, g = FAMS[fam]
    rule = Rule(R=rule0.R, T=rule0.T, mu=rule0.mu, sigma=round(rule0.sigma * FACTORS[i], 6), beta=rule0.beta,
                kernel=k, growth=g)
    L = Lenia(rule, A)
    n, lag = int(TEST_TU * rule.T), int(20 * rule.T)
    for t in range(n):
        L.step()
        if t == n - lag - 1:
            A_lag = L.A.copy()
    c = classify(A_lag, L.A, rule.R)
    (HERE / "conv").mkdir(exist_ok=True)
    np.save(HERE / "conv" / f"{name}-{fam}-{i}.npy", L.A.astype(np.float32))
    return {"body": name, "fam": fam, "i": i, "factor": FACTORS[i], "rule": rule.to_dict(),
            "final_sha256": state_sha256(L.A), **c}


def run() -> int:
    jobs = [(b, f, i) for b in BODIES for f in FAMS for i in range(len(FACTORS))]
    with open(HERE / "convergence.jsonl", "w") as out, ProcessPoolExecutor(4) as ex:
        for r in ex.map(one, jobs, chunksize=2):
            out.write(json.dumps(r) + "\n")
            out.flush()
    return 0


def sheet() -> int:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sheet import crop

    rows = [json.loads(l) for l in (HERE / "convergence.jsonl").read_text().splitlines()]
    code = {"DIED": 0, "CHAOS": 1, "FILLED": 2, "STATIC": 3, "OSC": 4, "GLIDER": 5}
    fig, axs = plt.subplots(len(BODIES), 2, figsize=(13, 2.6 * len(BODIES)), gridspec_kw={"width_ratios": [3, 2]})
    cmap = matplotlib.colors.ListedColormap(["#222222", "#888888", "#d9d9d9", "#4daf4a", "#984ea3", "#ff7f00"])
    for (ax, ax2), name in zip(axs, BODIES):
        M = np.full((len(FAMS), len(FACTORS)), np.nan)
        for r in rows:
            if r["body"] == name:
                M[list(FAMS).index(r["fam"]), r["i"]] = code[r.get("sub", r["cls"])]
        ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=5.5, aspect="auto")
        ax.set_yticks(range(len(FAMS)), [f"{k} kernel / {g} growth" for k, g in FAMS.values()], fontsize=7)
        ax.set_xticks(range(0, len(FACTORS), 2), [f"{f:.2f}" for f in FACTORS[::2]], fontsize=7)
        ax.set_xlabel("sigma / home sigma", fontsize=7)
        ax.set_title(f"{name}  (catalogue cousin: {CATALOGUE_COUSIN[name]})", fontsize=8, loc="left")
        # one thumbnail per family: the surviving run closest to factor 1
        ax2.axis("off")
        thumbs = []
        for fam in FAMS:
            ok = [r for r in rows if r["body"] == name and r["fam"] == fam and r["cls"] == "BODY"]
            if ok:
                r = min(ok, key=lambda r: abs(r["factor"] - 1))
                thumbs.append((fam, r["factor"], np.load(HERE / "conv" / f"{name}-{fam}-{r['i']}.npy")))
            else:
                thumbs.append((fam, None, None))
        R = 18 if name.startswith("star") else 13
        for j, (fam, f, A) in enumerate(thumbs):
            sub = ax2.inset_axes([j * 0.25, 0, 0.24, 1])
            sub.axis("off")
            if A is not None:
                sub.imshow(crop(A, int(2.2 * R)), cmap="inferno", vmin=0, vmax=1)
                sub.set_title(f"{fam} x{f:.2f}", fontsize=7)
            else:
                sub.set_title(f"{fam}: none", fontsize=7)
    handles = [matplotlib.patches.Patch(color=cmap(v), label=k) for k, v in code.items()]
    fig.legend(handles=handles, loc="lower center", ncol=6, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(HERE / "convergence-matrix.png", dpi=120)
    return 0


if __name__ == "__main__":
    sys.exit({"check": check, "run": run, "sheet": sheet}[sys.argv[1]]())
