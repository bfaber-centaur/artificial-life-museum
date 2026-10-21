"""Allowlisted environment/resource inventory for the REEF-M0 audit session (no env dump)."""
import json, os, platform, shutil, subprocess, sys, time
from pathlib import Path
import numpy, scipy

def rd(p):
    try: return Path(p).read_text().strip()
    except Exception as e: return f"unavailable ({type(e).__name__})"

cg = rd("/proc/self/cgroup")
mem_path = next((l.split(":", 2)[2] for l in cg.splitlines() if ":memory:" in l), "")
v1 = Path("/sys/fs/cgroup/memory").is_dir()
inv = {
    "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "repo_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    "os": platform.platform(), "arch": platform.machine(), "python": sys.version.split()[0],
    "numpy": numpy.__version__, "scipy": scipy.__version__,
    "fft_backend": "numpy.fft (pocketfft, single-threaded); scipy.ndimage.correlate for direct",
    "blas": "scipy-openblas 0.3.34 (numpy); not on the stepping path",
    "thread_env": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
    "cpu_model": next((l.split(":")[1].strip() for l in rd("/proc/cpuinfo").splitlines() if l.startswith("model name")), None),
    "os_cpu_count": os.cpu_count(), "sched_affinity": len(os.sched_getaffinity(0)),
    "cgroup_version": "v1 (hybrid; unified mounted but empty 0::/)" if v1 else "v2",
    "proc_self_cgroup": cg.splitlines(),
    "cpu_cfs_quota_us": rd("/sys/fs/cgroup/cpu/cpu.cfs_quota_us"),
    "cpu_cfs_period_us": rd("/sys/fs/cgroup/cpu/cpu.cfs_period_us"),
    "cpu_stat": rd("/sys/fs/cgroup/cpu/cpu.stat"),
    "cpuset_cpus": rd("/sys/fs/cgroup/cpuset/cpuset.cpus"),
    "mem_root_limit_bytes": rd("/sys/fs/cgroup/memory/memory.limit_in_bytes"),
    "mem_process_cgroup": mem_path,
    "mem_process_limit_bytes": rd(f"/sys/fs/cgroup/memory{mem_path}/memory.limit_in_bytes"),
    "mem_process_usage_bytes": rd(f"/sys/fs/cgroup/memory{mem_path}/memory.usage_in_bytes"),
    "mem_process_max_usage_bytes": rd(f"/sys/fs/cgroup/memory{mem_path}/memory.max_usage_in_bytes"),
    "mem_process_failcnt": rd(f"/sys/fs/cgroup/memory{mem_path}/memory.failcnt"),
    "mem_parent_limit_bytes": rd(f"/sys/fs/cgroup/memory{str(Path(mem_path).parent)}/memory.limit_in_bytes"),
    "meminfo_total_kb": next(l.split()[1] for l in rd("/proc/meminfo").splitlines() if l.startswith("MemTotal")),
    "swap_total_kb": next(l.split()[1] for l in rd("/proc/meminfo").splitlines() if l.startswith("SwapTotal")),
    "pids_max": rd(f"/sys/fs/cgroup/pids/pids.max"),
}
for m in ("/", "/home/user", "/tmp"):
    u = shutil.disk_usage(m); inv[f"disk_{m}"] = {"total_gb": round(u.total/1e9,1), "free_gb": round(u.free/1e9,1)}
inv["disk_note"] = "df shows 252G device but Avail ~30G: per-session writable allowance, not device size"
print(json.dumps(inv, indent=1))
