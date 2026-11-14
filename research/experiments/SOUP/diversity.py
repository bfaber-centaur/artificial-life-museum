"""Genome diversity over time for SOUP runs: mass-weighted RMS distance of the cells' genomes
(A > 0.05) from their mass-weighted mean, per snapshot. Appends one diversity.jsonl row per run
and prints spread at the start, at t = 1000 tu, and at the end.

  python diversity.py <npz> [<npz> ...]
"""
import json, sys
from pathlib import Path
import numpy as np


def spread(a, g):
    k = a > 0.05; w = a[k] / a[k].sum(); x = g[:, k]
    mu = (x * w).sum(1)
    return float(np.sqrt((((x - mu[:, None]) ** 2).sum(0) * w).sum()))


def main(paths):
    for p in paths:
        d = np.load(p)
        A, G, T = d["A"], d["G"], d["t"]
        sp = [spread(A[s].astype(np.float32), G[s].astype(np.float32) / 255) for s in range(len(T))]
        args = json.loads(str(d["args"]))
        rec = dict(name=Path(p).stem, rule=args["rule"], seed=args["seed"], inherit=args.get("inherit", "blend"),
                   t=T.tolist(), spread=[round(x, 4) for x in sp])
        with open(Path(__file__).parent / "diversity.jsonl", "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        i1000 = int(np.argmin(np.abs(T * 0.2 - 1000)))
        print(rec["name"], rec["inherit"], "spread start %.3f  t1000 %.3f  end %.3f" % (sp[0], sp[i1000], sp[-1]))


if __name__ == "__main__":
    main(sys.argv[1:])
