"""Write the replay-validation inputs: S001 alone and S103 alone, centred in N256,
plus a synthetic E/G/S triple (S001 + S103, disjoint) for exercising make_variants.

    python research/experiments/REEF-numerics/validation/make_inputs.py

S001 here is the raw catalog cells placed under the coexistence rule, NOT the field
lane's settled glider; it is an arithmetic test input, not a control. The triple is
a tool test, not an expedition encounter geometry.
"""
import json
from pathlib import Path

import numpy as np

from alm.specimens import load

HERE = Path(__file__).resolve().parent
RULE = {"kernel": "poly", "growth": "poly", "beta": [1.0], "mu": 0.155, "sigma": 0.020, "R": 13, "T": 10,
        "update": "euler+clip", "dtype": "float64"}
import sys
sys.path.insert(0, str(HERE.parent))
from replay import sha256  # noqa: E402

N = 256
out = HERE / "inputs"
out.mkdir(exist_ok=True)


def write(run_id, A, notes, extra=None):
    np.save(out / f"{run_id}.npy", A)
    m = {"run_id": run_id, "kind": "test", "lane": "numerics", "commit": None, "engine": "alm", "rule": RULE,
         "world": {"N": N, "boundary": "periodic"},
         "inputs": {"initial_state_sha256": sha256(A), "path": f"validation/inputs/{run_id}.npy", **(extra or {})},
         "horizon_tu": 20, "command": "python research/experiments/REEF-numerics/validation/make_inputs.py",
         "outputs": {}, "status": "ok", "notes": notes}
    (out / f"{run_id}.json").write_text(json.dumps(m, indent=1) + "\n")
    print(run_id, sha256(A))


g = load("S001").place(N)
s = load("S103").place(N)
assert load("S103").rule.mu == RULE["mu"] and load("S103").rule.sigma == RULE["sigma"]
write("REEF-NUM-VAL-S001", g, "raw S001 catalog cells centred, coexistence rule; arithmetic test input only")
write("REEF-NUM-VAL-S103", s, "S103 exact seed centred; known exact fixed point")
# Tool-test triple: ring moved 80 cells right of centre (disjoint supports).
s_shift = np.roll(s, 80, axis=1)
E = g + s_shift
assert np.array_equal(E - g, s_shift) and E.max() <= 1
write("REEF-NUM-TOY-G", g, "toy triple G (tool test only)")
write("REEF-NUM-TOY-S", s_shift, "toy triple S (tool test only)", {"ring": {"shift_cells": [0, 80]}})
write("REEF-NUM-TOY-E", E, "toy triple E = G + S (tool test only, not an expedition geometry)",
      {"ring": {"shift_cells": [0, 80]}})
m = json.loads((out / "REEF-NUM-TOY-E.json").read_text())
m["controls"] = {"G": "REEF-NUM-TOY-G", "S": "REEF-NUM-TOY-S"}
(out / "REEF-NUM-TOY-E.json").write_text(json.dumps(m, indent=1) + "\n")
