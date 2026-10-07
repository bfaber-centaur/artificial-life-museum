#!/usr/bin/env python3
"""L5-002: generate the pre-registered unseen disturbance I005 (rear deletion) with Lane 4's runner.

    .venv/bin/python research/experiments/L5-002-survival-predictor/gen_i005.py

Grid s = 0, 0.025, ..., 1.0 x phases t0 = 1000..1004, ref engine, N = 128, horizon 2000,
Lane 4's classifier unchanged. Writes i005-runs.csv in Lane 4's CSV format.
"""
import os
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import measure as M  # noqa: E402  (loads Lane 4's run.py as M.l4 and registers I005)

l4 = M.l4


def job(args):
    s, t0 = args
    return l4.run("I005", s, t0, 128, "ref")


def main():
    l4.set_cond("base")
    jobs = [(round(0.025 * i, 4), t0) for i in range(41) for t0 in l4.PHASES]
    with Pool(os.cpu_count()) as p:
        rows = p.map(job, jobs, chunksize=2)
    for r in rows:
        r["template_corr"] = float("nan")
    l4.write_rows(os.path.join(HERE, "i005-runs.csv"), rows)
    from collections import Counter
    print(Counter((r["class"]) for r in rows))


if __name__ == "__main__":
    main()
