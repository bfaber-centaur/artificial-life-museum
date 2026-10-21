"""results.jsonl -> timings.csv (one row per sample) and summary table on stdout."""
import csv, json, statistics as st
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in (HERE / "results.jsonl").read_text().splitlines()]
with open(HERE / "timings.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["id", "tag", "N", "R", "T", "W", "mode", "sample", "steps", "wall_s", "cpu_s", "world_steps_per_s",
                "tu_per_s_per_world", "setup_s", "peak_rss_mb", "output_bytes", "input_sha256", "final_sha256", "total_steps"])
    for r in rows:
        for i, s in enumerate(r["samples"]):
            w.writerow([r["id"], r["tag"], r["N"], r["R"], r["T"], r["W"], r["mode"], i, s["steps"], f"{s['wall_s']:.4f}",
                        f"{s['cpu_s']:.4f}", f"{s['world_steps_per_s']:.2f}", f"{s['tu_per_s_per_world']:.3f}",
                        f"{r['setup_s']:.4f}", f"{r['peak_rss_mb']:.1f}", r["output_bytes"], r["input_sha256"],
                        r["final_sha256"], r["total_steps"]])
print("| case | tag | world-steps/s median [min–max] | tu/s/world median | cpu/wall | setup s | peak RSS MB | output bytes |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    S = r["samples"]
    tu = st.median(s["tu_per_s_per_world"] for s in S)
    cw = sum(s["cpu_s"] for s in S) / sum(s["wall_s"] for s in S)
    print(f"| {r['id']} | {r['tag'] or '-'} | {r['med_world_steps_per_s']:.1f} [{r['min_world_steps_per_s']:.1f}–{r['max_world_steps_per_s']:.1f}] "
          f"| {tu:.2f} | {cw:.2f} | {r['setup_s']:.2f} | {r['peak_rss_mb']:.0f} | {r['output_bytes']} |")
