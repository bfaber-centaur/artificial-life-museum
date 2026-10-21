"""Small correctness smoke: engine agreement (alm vs field vs alm_check fft vs direct) and S103 fixed point.
Short survival is not attractor evidence; this checks arithmetic only."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/experiments/L6-field"))
import field
from alm.lenia import Lenia, Rule
from alm.specimens import load
import alm_check.lenia as ck
sha = lambda A: hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()
out = {}
for sid in ("S001", "S103"):
    A0 = load(sid).place(256); n = 200
    rule = Rule(R=13, T=10, mu=.155, sigma=.020)
    s = Lenia(rule, A0)
    for _ in range(n): s.step()
    b = field.Batch(R=13, T=10, mu=np.array([.155]), sigma=np.array([.020])).run(A0[None], n, snap_every=100)["final"][0]
    cr = ck.Rule(R=13, T=10, mu=.155, sigma=.020)
    wf = ck.World(A0.copy(), cr, path="fft"); wd = ck.World(A0.copy(), cr, path="direct")
    for _ in range(n): wf.step(); wd.step()
    out[sid] = dict(steps=n, alm_sha=sha(s.A), field_sha=sha(b), alm_eq_field_bitwise=bool(np.array_equal(s.A, b)),
                    alm_vs_check_fft_maxabs=float(abs(s.A - wf.A).max()), check_fft_vs_direct_maxabs=float(abs(wf.A - wd.A).max()),
                    mass_alm=float(s.A.sum()))
A = load("S103").place(256); s = Lenia(Rule(R=13, T=10, mu=.155, sigma=.020), A)
for _ in range(500): s.step()
prev = s.A.copy(); s.step()
out["S103_fixed_point"] = dict(steps=501, max_abs_dA_last_step=float(abs(s.A - prev).max()), max_abs_vs_initial=float(abs(s.A - A).max()))
print(json.dumps(out, indent=1))
