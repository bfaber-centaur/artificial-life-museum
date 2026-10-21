"""REEF-M0 audit: independent timing of existing ALM engines on the auditor's session.

Timing inputs only (not an encounter): coexistence rule mu=.155 sigma=.020, poly/poly,
float64, Euler+clip, periodic. S001 cells and S103 cells are placed in *separate* worlds.
Engines are used as-is: alm.lenia.Lenia, L6-field field.Batch, alm_check.lenia.World.

Usage: python audit_bench.py OUT_DIR [case ...]
"""
from __future__ import annotations

import hashlib, json, os, resource, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/experiments/L6-field"))
import field  # noqa: E402
from alm.lenia import Lenia, Rule  # noqa: E402
from alm.specimens import load  # noqa: E402
import alm_check.lenia as ck  # noqa: E402

MU, SIGMA = 0.155, 0.020
TARGET_S, CEIL_S, SAMPLES = 3.0, 30.0, 3


def sha(A):
    return hashlib.sha256(np.ascontiguousarray(A, dtype="<f8").tobytes()).hexdigest()


def seed(sid, N, scale=1):
    cells = load(sid).cells
    if scale > 1:  # explicit block resize: same physical extent at R*scale
        cells = np.kron(cells, np.ones((scale, scale), dtype=cells.dtype))
    A = np.zeros((N, N))
    h, w = cells.shape
    y0, x0 = (N - h) // 2, (N - w) // 2
    A[y0:y0 + h, x0:x0 + w] = cells / 255.0
    return A


def stack(W, N, scale=1):
    ids = ["S001", "S103"]
    return np.stack([seed(ids[i % 2], N, scale) for i in range(W)])


def timed(fn_steps, est_steps=5):
    """fn_steps(n) runs n steps. Warm up, estimate, then adaptive samples."""
    fn_steps(2)
    t0 = time.perf_counter(); fn_steps(est_steps); per = (time.perf_counter() - t0) / est_steps
    n = max(1, int(TARGET_S / per))
    trunc = False
    if per * n * SAMPLES > CEIL_S:
        n = max(1, int(CEIL_S / SAMPLES / per)); trunc = True
    out = []
    for _ in range(SAMPLES):
        c0 = time.process_time(); w0 = time.perf_counter()
        fn_steps(n)
        out.append((time.perf_counter() - w0, time.process_time() - c0))
    return n, out, trunc


def case(name, N, R, T, W, engine):
    rule = Rule(R=R, T=T, mu=MU, sigma=SIGMA)
    scale = R // 13
    A0 = stack(W, N, scale)
    t_setup = time.perf_counter()
    if engine == "alm":
        sims = [Lenia(rule, A0[i]) for i in range(W)]
        def run(n):
            for s in sims:
                for _ in range(n):
                    s.step()
        final = lambda: np.stack([s.A for s in sims])
    elif engine in ("field", "field_noinst"):
        b = field.Batch(R=R, T=T, mu=np.full(W, MU), sigma=np.full(W, SIGMA))
        state = {"B": A0.copy()}
        if engine == "field":
            def run(n):
                r = b.run(state["B"], n, snap_every=100)
                state["B"] = r["final"]
        else:  # same arithmetic as Batch.run's update line, no per-step measurements
            from alm.lenia import kernel, growth
            khat = np.fft.rfft2(kernel((N, N), b.rule(0)))
            def run(n):
                B = state["B"]
                for _ in range(n):
                    U = np.fft.irfft2(np.fft.rfft2(B) * khat, s=(N, N))
                    B = np.clip(B + growth("poly", U, MU, SIGMA) * (1.0 / T), 0.0, 1.0)
                state["B"] = B
        final = lambda: state["B"]
    elif engine in ("check_fft", "check_direct"):
        cr = ck.Rule(R=R, T=T, mu=MU, sigma=SIGMA)
        ws = [ck.World(A0[i].copy(), cr, path=engine.split("_")[1]) for i in range(W)]
        def run(n):
            for w in ws:
                for _ in range(n):
                    w.step()
        final = lambda: np.stack([w.A for w in ws])
    else:
        raise ValueError(engine)
    t_setup = time.perf_counter() - t_setup
    n, samples, trunc = timed(run)
    walls = sorted(s[0] for s in samples)
    med = walls[len(walls) // 2]
    cpus = [s[1] for s in samples]
    return dict(case=name, engine=engine, N=N, R=R, T=T, worlds=W, steps_per_sample=n,
                setup_s=round(t_setup, 4), wall_min=round(walls[0], 4), wall_med=round(med, 4),
                wall_max=round(walls[-1], 4), cpu_med=round(sorted(cpus)[1], 4),
                world_steps_per_s=round(W * n / med, 2), tu_per_s_per_world=round(n / T / med, 3),
                truncated=trunc, input_sha256=sha(A0), final_sha256=sha(final()),
                peak_rss_mb_self=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1))


CASES = {
    "alm_N256_R13_T10_W1": (256, 13, 10, 1, "alm"),
    "field_N256_R13_T10_W1": (256, 13, 10, 1, "field"),
    "fieldnoinst_N256_R13_T10_W1": (256, 13, 10, 1, "field_noinst"),
    "field_N256_R13_T10_W2": (256, 13, 10, 2, "field"),
    "field_N256_R13_T10_W4": (256, 13, 10, 4, "field"),
    "fieldnoinst_N256_R13_T10_W4": (256, 13, 10, 4, "field_noinst"),
    "field_N512_R13_T10_W1": (512, 13, 10, 1, "field"),
    "field_N512_R26_T10_W1": (512, 26, 10, 1, "field"),
    "field_N256_R13_T20_W1": (256, 13, 20, 1, "field"),
    "checkfft_N256_R13_T10_W1": (256, 13, 10, 1, "check_fft"),
    "checkdirect_N256_R13_T10_W1": (256, 13, 10, 1, "check_direct"),
}

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    names = sys.argv[2:] or list(CASES)
    path = out / "timings.jsonl"
    for nm in names:
        try:
            row = case(nm, *CASES[nm])
        except Exception as e:  # preserve failures
            row = dict(case=nm, error=repr(e))
        print(json.dumps(row), flush=True)
        with path.open("a") as f:  # checkpoint after each case
            f.write(json.dumps(row) + "\n")
