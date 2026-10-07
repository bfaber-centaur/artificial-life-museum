"""Print the compact phase tables used in README.md from the sweep CSVs."""
import csv
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return list(csv.DictReader(open(HERE / name)))


def code(r):
    f = r["fate"]
    if f != "localized":
        return {"died": ".", "filled": "#"}[f]
    return {"GLIDER": "G", "CIRCLER": "C", "STATIC": "S", "OTHER": "?"}[phenotype(r)]


def phenotype(r):
    """Motion class of a localized world (thresholds fixed before the T=40/R=26 reruns)."""
    net, path = float(r["speed"]), float(r["path_speed"])
    if net > 0.2:
        return "GLIDER"
    if net < 0.1 and path > 0.2:
        return "CIRCLER"
    if path < 0.02:
        return "STATIC"
    return "OTHER"


def bistab(name):
    rows = load(name)
    sg = sorted({float(r["sigma"]) for r in rows})
    print(name)
    print(f"{'seed':8s}{'mu':7s}" + "".join(f"{s * 1e4:5.0f}" for s in sg))
    for seed in dict.fromkeys(r["seed"] for r in rows):
        for m in sorted({r["mu"] for r in rows}, key=float):
            cs = {float(r["sigma"]): code(r) for r in rows if r["seed"] == seed and r["mu"] == m}
            print(f"{seed:8s}{m:7s}" + "".join(f"{cs.get(s, ''):>5s}" for s in sg))


def switch(name):
    rows = load(name)
    print(name)
    for case in dict.fromkeys(r["case"] for r in rows):
        print(" ", case)
        for iv in dict.fromkeys(r["intervention"] for r in rows):
            rs = [r for r in rows if r["case"] == case and r["intervention"] == iv]
            oc = [outcome(r) for r in rs]
            line = " ".join(f"{float(r['s']):.2f}{o[0]}" for r, o in zip(rs, oc))
            print(f"    {iv}: {dict(Counter(oc))}\n      {line}")


def outcome(r):
    return r["fate"].upper() if r["fate"] != "localized" else phenotype(r)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        (bistab if n.startswith("bistab") else switch)(n)
