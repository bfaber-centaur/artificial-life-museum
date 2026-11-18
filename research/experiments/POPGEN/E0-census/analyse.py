"""POPGEN E0 analysis (protocol.md): K, turnover r, deaths, stationarity rule, P0a-P0c.

usage: analyse.py            reads e0.jsonl + $POPGEN_OUT/<tag>.npz, writes e0_results.json
Tracks are built with tree.link / tree.build_tree on the frames from 100 tu before W to the end
of the run; births and deaths are counted inside W only.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "REPLICATORS"))
import tree  # noqa: E402

OUT = Path(os.environ.get("POPGEN_OUT", "/tmp/claude-0/-home-user/1e73a8fc-c1a3-55c2-9798-cc47a6a901a7/scratchpad/popgen"))


def load(tag):
    z = np.load(OUT / f"{tag}.npz")
    off, P = z["offsets"], z["peaks"]
    frames = [P[off[i]:off[i + 1]].astype(float) for i in range(len(off) - 1)]
    return frames, z["counts"], z["mass"]


def analyse(rec):
    frames, n, mass = load(rec["tag"])
    TU = int(rec["tu"]); w0, w1 = TU - 1500, TU
    nw = n[w0:w1 + 1]; K = float(np.median(nw))
    slope = np.polyfit(np.arange(len(nw)), nw, 1)[0]
    trend = abs(slope * 1500) / max(K, 1)
    f0 = w0 - 100
    sub = frames[f0:]
    tracks = tree.link(sub, rec["N"])
    _, keep = tree.build_tree(tracks, len(sub))
    lo, hi = w0 - f0, w1 - f0
    births = sum(1 for k, tk in enumerate(tracks) if keep[k] and tk["parent"] is not None and lo <= tk["born"] <= hi)
    deaths = sum(1 for k, tk in enumerate(tracks) if keep[k] and lo <= tk["last"] < len(sub) - 1 - tree.GAP and tk["last"] <= hi)
    r = births / (K * 1.5) if K else 0.0
    return dict(tag=rec["tag"], N=rec["N"], g_r=rec["g_r"], seed=rec["seed"], tu=TU, K=K, trend=round(float(trend), 3),
                stationary=bool(trend <= 0.10), births=births, deaths=deaths, r_per_1000tu=round(r, 4),
                deaths_per_1000tu=round(deaths / (K * 1.5), 4) if K else 0.0,
                mass_K=round(float(np.median(mass[w0:w1 + 1])), 1), mass_per_cell=round(float(np.median(mass[w0:w1 + 1])) / K, 2) if K else None,
                K_per_area_1e4=round(K / rec["N"] ** 2 * 1e4, 3))


if __name__ == "__main__":
    recs = [json.loads(l) for l in open(HERE / "e0.jsonl")]
    latest = {}
    for rc in recs:  # longest run per (N, g_r, seed): an extended run supersedes the 5000 tu one
        key = (rc["N"], rc["g_r"], rc["seed"])
        if key not in latest or rc["tu"] > latest[key]["tu"]:
            latest[key] = rc
    rows = [analyse(rc) for rc in sorted(latest.values(), key=lambda r: (r["g_r"], r["N"], r["seed"]))]
    for r in rows:
        print(r)
    res = dict(rows=rows)
    for g in sorted({r["g_r"] for r in rows}):
        by = {}
        for r in rows:
            if r["g_r"] == g:
                by.setdefault(r["N"], []).append(r["K_per_area_1e4"])
        m = [np.mean(v) for v in by.values()]
        spread = (max(m) - min(m)) / np.mean(m)
        res[f"P0a_g{g}"] = dict(K_per_area_seed_mean={k: round(float(np.mean(v)), 3) for k, v in by.items()},
                                spread=round(float(spread), 3), pass_=bool(spread <= 0.15))
    res["P0b"] = dict(pass_=all(r["r_per_1000tu"] >= 0.05 for r in rows), r=[r["r_per_1000tu"] for r in rows])
    res["P0c"] = dict(pass_=all(abs(r["births"] - r["deaths"]) <= max(0.2 * r["births"], 3) for r in rows))
    res["need_extension"] = [r["tag"] for r in rows if not r["stationary"]]
    for k, v in res.items():
        if k != "rows":
            print(k, v)
    json.dump(res, open(HERE / "e0_results.json", "w"), indent=1)
