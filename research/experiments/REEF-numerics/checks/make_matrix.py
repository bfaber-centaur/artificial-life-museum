"""Comparison matrix for the §9 checks of P2 and P3 (D-017), from checks/*/summary.json.

    python research/experiments/REEF-numerics/checks/make_matrix.py   # writes MATRIX.md and matrix.json

Pass rules (PROTOCOL §9, frozen in v1): replay sha256 identical; alm_check FFT expected bitwise;
direct/T20/R26/N512: same class, t_c within 0.5 tu, masses within 1% (heading change is not
defined: the glider merges at t_c in every pilot). Ignition time and front speed are the lead's
D-017 outcome observables and are reported with their differences, not given a frozen tolerance.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTES = [("alm", "alm reference (this lane, fresh process)"), ("chkfft", "alm_check FFT (same arithmetic)"),
          ("direct", "alm_check direct, window 3→25 tu (different arithmetic)"), ("T20", "T20, own controls"),
          ("R26", "R26 2×2 block, N512, own controls"), ("N512", "N512, R13, same separation, own controls")]


def load(p, r):
    f = HERE / f"REEF-{p}-E-{r}" / "summary.json"
    return json.loads(f.read_text()) if f.exists() else None


def g(d, *ks):
    for k in ks:
        if d is None:
            return None
        d = d.get(k)
    return d


def rel(a, b):
    return None if a is None or b is None else (a - b) / b


def fmt(x, n=3):
    return "—" if x is None else (f"{x:.{n}f}" if isinstance(x, float) else str(x))


NOTES = """Notes. Clean-process replay (field runner.py at fe4ba1c, fresh process): E/G/S final sha256 identical and all
159 checkpoints bitwise for both runs (clean_replay.json). Only alm_check direct is different arithmetic.
R26 "FAIL (class)" is the scorer's CONTROL_FAILURE: its frozen S-control rule needs constant ring mass, which the
R26 block ring never has (README section 5); judged against its own control (D-010) the ring stays one static body
and E ignites into the same colony, earlier. See README section 7.
"""

rows, out = [], {}
for p in ("P2", "P3"):
    ref = load(p, "alm")
    for r, label in ROUTES:
        s = load(p, r)
        if s is None:
            rows.append(f"| {p} | {label} | not run | | | | | | | | |")
            continue
        sc = s["score"]
        m20, m25 = g(s, "at_t20", "mass_E"), g(s, "at_t25", "mass_E")
        fr = g(s, "front", "from_ignition_to_r95_0.7_half", "speed_R_per_tu")
        ign = g(s, "ignition", "t")
        v = {"class": sc["class"], "flags": sc["flags"], "t_c": sc["t_c"], "t_int": sc["t_int"], "ignition_t": ign,
             "mass_E_t20": m20, "mass_E_t25": m25, "front_R_per_tu": fr, "final_sha256_E": s["final_state_sha256"]["E"],
             "controls_S_bitwise_constant": s["S_bitwise_constant"], "run_id": s["run_id"], "commit": s["commit"]}
        if r != "alm":
            same_cls = sc["class"] == ref["score"]["class"]
            dtc = None if sc["t_c"] is None else sc["t_c"] - ref["score"]["t_c"]
            d20, d25 = rel(m20, g(ref, "at_t20", "mass_E")), rel(m25, g(ref, "at_t25", "mass_E"))
            if r == "chkfft":
                verdict = "PASS (bitwise)" if s["final_state_sha256"] == ref["final_state_sha256"] else "DIFFERS"
            else:
                ok = same_cls and dtc is not None and abs(dtc) <= 0.5 + 1e-9 and all(
                    x is not None and abs(x) <= 0.01 for x in (d20, d25))
                verdict = "PASS" if ok else ("same class; quantitative FAIL" if same_cls else "FAIL (class)")
            v.update(dt_c=dtc, d_mass_t20_rel=d20, d_mass_t25_rel=d25, d_ignition=None if ign is None else ign - ref["ignition"]["t"],
                     d_front_rel=rel(fr, g(ref, "front", "from_ignition_to_r95_0.7_half", "speed_R_per_tu")), verdict=verdict)
        else:
            v["verdict"] = "reference"
        out.setdefault(p, {})[r] = v
        rows.append(f"| {p} | {label} | {v['class']} | {fmt(v['t_c'], 1)} | {fmt(ign, 1)} | {fmt(m20, 2)} | {fmt(m25, 2)} "
                    f"| {fmt(fr)} | {fmt(v.get('dt_c'), 1)} / {fmt(v.get('d_mass_t20_rel'), 4)} / {fmt(v.get('d_mass_t25_rel'), 4)} "
                    f"| {v['verdict']} | `{s['final_state_sha256']['E'][:12]}` |")

hdr = ("| run | route | class | t_c (tu) | ignition (tu) | E mass t20 | E mass t25 | front R/tu | Δt_c / Δm20 / Δm25 (rel) "
       "| §9 verdict | E final sha256 |\n|---|---|---|---|---|---|---|---|---|---|---|")
(HERE / "MATRIX.md").write_text("# §9 comparison matrix: P2 and P3\n\n" + __doc__.split("\n\n", 2)[2].strip() + "\n\n"
                                + hdr + "\n" + "\n".join(rows) + "\n\n" + NOTES)
(HERE / "matrix.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
print(hdr + "\n" + "\n".join(rows))
