"""REEF-M0 runtime harness. See SPEC.md. Usage:
  python bench.py inventory            -> inventory.json
  python bench.py case <id>            -> appends results.jsonl
  python bench.py all | smoke | concurrent
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import hashlib, io, json, platform, resource, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(REPO / "src"), str(REPO / "research/experiments/L6-field")]
import numpy as np

MU, SIGMA = 0.155, 0.020
TARGET_S, CEIL_S, SAMPLES = 3.0, 30.0, 3

CASES = {}
def _c(id, N, R, T, W, mode):
    CASES[id] = dict(id=id, N=N, R=R, T=T, W=W, mode=mode)
_c("n256-w1-engine", 256, 13, 10, 1, "engine")
_c("n256-w1-batch", 256, 13, 10, 1, "batch")
_c("n256-w1-instr", 256, 13, 10, 1, "instr")
_c("n256-w2-batch", 256, 13, 10, 2, "batch")
_c("n256-w2-instr", 256, 13, 10, 2, "instr")
_c("n256-w4-batch", 256, 13, 10, 4, "batch")
_c("n256-w4-instr", 256, 13, 10, 4, "instr")
_c("n256-w4-engine", 256, 13, 10, 4, "engine")
_c("n512-r13-engine", 512, 13, 10, 1, "engine")
_c("n512-r13-instr", 512, 13, 10, 1, "instr")
_c("n512-r26-engine", 512, 26, 10, 1, "engine")
_c("n512-r26-instr", 512, 26, 10, 1, "instr")
_c("n256-t20-engine", 256, 13, 20, 1, "engine")
_c("n256-t20-instr", 256, 13, 20, 1, "instr")
_c("check-fft", 256, 13, 10, 1, "check-fft")
_c("check-direct", 256, 13, 10, 1, "check-direct")


def sha(a):
    return hashlib.sha256(np.ascontiguousarray(a, dtype=np.float64).tobytes()).hexdigest()


def make_input(N, R):
    from alm.specimens import load
    if R == 26:
        return np.kron(make_input(N // 2, 13), np.ones((2, 2)))
    A = np.zeros((N, N))
    for sid, (fy, fx) in (("S001", (0.25, 0.25)), ("S103", (0.75, 0.75))):
        c = load(sid).cells / 255.0
        h, w = c.shape
        y0, x0 = int(fy * N) - h // 2, int(fx * N) - w // 2
        A[y0:y0 + h, x0:x0 + w] = c
    return A


def build(case, A0):
    """Return (step_n(n) callable, final_state() callable, output_bytes() callable)."""
    N, R, T, W, mode = (case[k] for k in ("N", "R", "T", "W", "mode"))
    if mode == "engine":
        from alm.lenia import Lenia, Rule
        worlds = [Lenia(Rule(R=R, T=T, mu=MU, sigma=SIGMA), A0) for _ in range(W)]
        def step_n(n):
            for w in worlds:
                for _ in range(n):
                    w.step()
        return step_n, lambda: np.stack([w.A for w in worlds]), lambda: 0
    if mode in ("batch", "instr"):
        from field import Batch
        b = Batch(R=R, T=T, mu=[MU] * W, sigma=[SIGMA] * W)
        st = dict(B=np.stack([A0] * W), last=None)
        snap = int(T) if mode == "instr" else 10**12
        def step_n(n):
            res = b.run(st["B"], n, snap_every=snap)
            st["B"], st["last"] = res["final"], res
        def out_bytes():
            r = st["last"]
            buf = io.BytesIO()
            np.savez_compressed(buf, mass=r["mass"], pos=r["pos"], final=r["final"],
                                snaps=np.array([json.dumps([t, s]) for t, s in r["snaps"]]))
            return buf.tell()
        return step_n, lambda: st["B"], out_bytes
    from alm_check.lenia import Rule as CRule, World
    w = World(A0.copy(), CRule(R=R, T=T, mu=MU, sigma=SIGMA), path=mode.split("-")[1], boundary="wrap")
    def step_n(n):
        for _ in range(n):
            w.step()
    return step_n, lambda: w.A, lambda: 0


def timed(fn, *a):
    w0, c0 = time.perf_counter(), time.process_time()
    fn(*a)
    return time.perf_counter() - w0, time.process_time() - c0


def run_case(cid, tag=""):
    case = CASES[cid]
    t0 = time.perf_counter()
    A0 = make_input(case["N"], case["R"])
    step_n, final, out_bytes = build(case, A0)
    setup_s = time.perf_counter() - t0
    direct = case["mode"] == "check-direct"
    warm = 3 if direct else 10
    warm_s, _ = timed(step_n, warm)
    probe = 2 if direct else 20
    pw, _ = timed(step_n, probe)
    per = pw / probe
    steps = max(1, int(TARGET_S / per))
    samples, used, trunc = [], 0.0, []
    for i in range(SAMPLES):
        if used + steps * per > CEIL_S:
            trunc.append(f"stopped before sample {i+1}: ceiling {CEIL_S}s")
            break
        w, c = timed(step_n, steps)
        used += w
        ws = steps * case["W"] / w
        samples.append(dict(wall_s=w, cpu_s=c, steps=steps, world_steps_per_s=ws,
                            tu_per_s_per_world=steps / case["T"] / w))
    total_steps = warm + probe + steps * len(samples)
    rec = dict(case, tag=tag, utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               input_sha256=sha(A0), setup_s=setup_s, warmup_s=warm_s, probe_s_per_step=per,
               samples=samples, truncation=trunc, total_steps=total_steps,
               final_sha256=sha(final()), output_bytes=out_bytes(),
               peak_rss_mb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
               med_world_steps_per_s=float(np.median([s["world_steps_per_s"] for s in samples])),
               min_world_steps_per_s=float(min(s["world_steps_per_s"] for s in samples)),
               max_world_steps_per_s=float(max(s["world_steps_per_s"] for s in samples)))
    with open(HERE / "results.jsonl", "a") as f:
        f.write(json.dumps(rec) + "\n")
    print(json.dumps({k: rec[k] for k in ("id", "tag", "med_world_steps_per_s", "min_world_steps_per_s",
                                         "max_world_steps_per_s", "setup_s", "peak_rss_mb", "truncation")}))


def _read(p):
    try:
        return Path(p).read_text().strip()
    except OSError as e:
        return f"unavailable: {e.__class__.__name__}"


def inventory():
    import numpy, scipy
    cg = _read("/proc/self/cgroup")
    mem_path = next((l.split(":", 2)[2] for l in cg.splitlines() if ":memory:" in l), None)
    mroot = f"/sys/fs/cgroup/memory{mem_path}" if mem_path else None
    inv = dict(
        utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        session_prefix=os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID", "")[:12] or "unavailable",
        repo_head=subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        os=platform.platform(), arch=platform.machine(), python=platform.python_version(),
        numpy=numpy.__version__, scipy=scipy.__version__,
        fft_backend="numpy.fft (pocketfft, single-threaded)",
        blas=numpy.show_config(mode="dicts")["Build Dependencies"]["blas"],
        thread_env={v: os.environ.get(v) for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
        cpu_model=next((l.split(":", 1)[1].strip() for l in _read("/proc/cpuinfo").splitlines() if l.startswith("model name")), None),
        os_cpu_count=os.cpu_count(), sched_affinity=sorted(os.sched_getaffinity(0)),
        cgroup_raw=cg, cgroup_version="v1 (+ empty unified)" if Path("/sys/fs/cgroup/memory").exists() else "v2/unknown",
        cpu_cfs_quota_us=_read("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"), cpu_cfs_period_us=_read("/sys/fs/cgroup/cpu/cpu.cfs_period_us"),
        cpu_stat=_read("/sys/fs/cgroup/cpu/cpu.stat"), cpuset=_read("/sys/fs/cgroup/cpuset/cpuset.cpus"),
        mem_cgroup_path=mem_path,
        mem_limit_bytes=_read(f"{mroot}/memory.limit_in_bytes") if mroot else None,
        mem_parent_limit_bytes=_read(f"{Path(mroot).parent}/memory.limit_in_bytes") if mroot else None,
        mem_root_limit_bytes=_read("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
        mem_usage_bytes=_read(f"{mroot}/memory.usage_in_bytes") if mroot else None,
        mem_max_usage_bytes=_read(f"{mroot}/memory.max_usage_in_bytes") if mroot else None,
        mem_failcnt=_read(f"{mroot}/memory.failcnt") if mroot else None,
        meminfo={l.split(":")[0]: l.split(":")[1].strip() for l in _read("/proc/meminfo").splitlines()
                 if l.split(":")[0] in ("MemTotal", "MemAvailable", "SwapTotal")},
        disk={p: dict(zip(("total", "used", "free"), __import__("shutil").disk_usage(p))) for p in ("/", str(REPO), "/tmp")},
        ulimit_cpu_s=resource.getrlimit(resource.RLIMIT_CPU), ulimit_as=resource.getrlimit(resource.RLIMIT_AS),
        ulimit_nproc=resource.getrlimit(resource.RLIMIT_NPROC),
        pids_max=_read("/sys/fs/cgroup/pids/pids.max"),
        timeouts="Bash tool: foreground default 120 s, max 600 s; background default 1800 s, max 7200 s (tool documentation, not tested)",
    )
    (HERE / "inventory.json").write_text(json.dumps(inv, indent=1, default=str) + "\n")
    print(json.dumps(inv, indent=1, default=str))


def smoke():
    from alm.lenia import Lenia, Rule
    from field import Batch
    from alm_check.lenia import Rule as CRule, World
    A0 = make_input(256, 13)
    L = Lenia(Rule(R=13, T=10, mu=MU, sigma=SIGMA), A0)
    for _ in range(200):
        L.step()
    Bf = Batch(R=13, T=10, mu=[MU], sigma=[SIGMA]).run(A0[None], 200, snap_every=10**12)["final"][0]
    C = World(A0.copy(), CRule(R=13, T=10, mu=MU, sigma=SIGMA), path="fft")
    for _ in range(200):
        C.step()
    F = World(A0.copy(), CRule(R=13, T=10, mu=MU, sigma=SIGMA), path="fft")
    D = World(A0.copy(), CRule(R=13, T=10, mu=MU, sigma=SIGMA), path="direct", boundary="wrap")
    for _ in range(20):
        F.step(); D.step()
    out = dict(steps=200, lenia_vs_batch_maxabs=float(abs(L.A - Bf).max()), lenia_vs_batch_bitwise=bool((L.A == Bf).all()),
               lenia_vs_check_fft_maxabs=float(abs(L.A - C.A).max()),
               direct_vs_fft_20steps_maxabs=float(abs(F.A - D.A).max()),
               lenia_200_sha256=sha(L.A), mass_200=float(L.A.sum() / 169))
    (HERE / "smoke.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def concurrent():
    ps = [subprocess.Popen([sys.executable, __file__, "case", "n256-w1-engine", f"concurrent-{i}"]) for i in range(2)]
    for p in ps:
        p.wait()


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "case":
        run_case(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif cmd == "all":
        for cid in CASES:
            subprocess.run([sys.executable, __file__, "case", cid])
    else:
        globals()[cmd]()
