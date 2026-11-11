"""Continue scout bodies from their snapshot for TU time units; frame strip + per-100-tu class.
Usage: python filmstrip.py REGION KEY:B[,KEY:B...] [TU]"""
import json, sys
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from alm.lenia import Lenia, Rule
from scout import HERE, classify
from sheet import crop

def one(args):
    region, key, b, tu = args
    r = [json.loads(l) for l in (HERE / f"scout-{region}.jsonl").read_text().splitlines() if json.loads(l)["k"] == int(key.split("-")[1])][0]
    ru = r["rule"]; rule = Rule(R=ru["R"], T=ru["T"], mu=ru["mu"], sigma=ru["sigma"], beta=tuple(ru["beta"]), kernel=ru["kernel"], growth=ru["growth"])
    z = np.load(HERE / "snaps" / region / f"{key}.npz"); A = z["A"][list(z["idx"]).index(b)].astype(np.float64)
    L = Lenia(rule, A); frames, cls = [], []
    for seg in range(tu // 100):
        for t in range(1000):
            L.step()
            if t == 799: lag = L.A.copy()
        c = classify(lag, L.A, rule.R); cls.append(c["cls"][0] + c.get("sub", "")[:1])
    for t in range(80):  # 8 tu fine strip at the end
        if t % 10 == 0: frames.append(L.A.copy())
        L.step()
    np.save(HERE / "snaps" / f"long-{region}-{key}-{b}.npy", L.A.astype(np.float32))
    return key, b, ru, cls, c, frames

if __name__ == "__main__":
    region, picks = sys.argv[1], [p.split(":") for p in sys.argv[2].split(",")]
    tu = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(one, [(region, k, int(b), tu) for k, b in picks]))
    fig, axs = plt.subplots(len(res), 8, figsize=(12, 1.7 * len(res)), squeeze=False)
    for row, (key, b, ru, cls, c, frames) in zip(axs, res):
        print(key, b, ru["mu"], ru["sigma"], ru["beta"], "".join(cls), {k: round(v, 2) for k, v in c.items() if isinstance(v, float)})
        for j, (ax, F) in enumerate(zip(row, frames)):
            ax.imshow(crop(F, 2 * ru["R"]), cmap="inferno", vmin=0, vmax=1); ax.axis("off")
            if j == 0: ax.set_title(f"{key}.{b} m{ru['mu']} s{ru['sigma']} b{[round(x,2) for x in ru['beta']]} {''.join(cls)}", fontsize=6, loc="left")
    fig.tight_layout(); fig.savefig(HERE / f"film-{region}.png", dpi=110)
