"""Long-horizon check (1000 tu) of hand-picked scout bodies, restarted from their snapshot."""
import json, sys
import numpy as np
from pathlib import Path
from alm.lenia import Lenia, Rule
from scout import classify, HERE
PICKS = [("R1","1-1",3),("R1","1-7",1),("R1","1-39",1),("R4","1-56",2),("R2","1-5",6),("R2","1-11",1),("R2","1-8",5)]
def go(region, key, b, tu=1000):
    r = [json.loads(l) for l in (HERE/f"scout-{region}.jsonl").read_text().splitlines() if f"{json.loads(l)['seed']}-{json.loads(l)['k']}"==key][0]
    z = np.load(HERE/"snaps"/region/f"{key}.npz"); i = list(z["idx"]).index(b)
    ru = r["rule"]; rule = Rule(R=ru["R"],T=ru["T"],mu=ru["mu"],sigma=ru["sigma"],beta=tuple(ru["beta"]),kernel=ru["kernel"],growth=ru["growth"])
    L = Lenia(rule, z["A"][i].astype(np.float64)); out=[]
    for seg in range(tu//100):
        for _ in range(1000-200): L.step()
        lag=L.A.copy()
        for _ in range(200): L.step()
        out.append(classify(lag, L.A, rule.R))
    np.save(HERE/"snaps"/f"long-{region}-{key}-{b}.npy", L.A.astype(np.float32))
    return region,key,b,ru,[o["cls"]+"/"+o.get("sub","") for o in out], out[-1]
if __name__=="__main__":
    from concurrent.futures import ProcessPoolExecutor
    picks=[(a,b,c) for a,b,c in PICKS if b]
    with ProcessPoolExecutor(4) as ex:
        for res in ex.map(lambda p: None, []): pass
        futs=[ex.submit(go,*p) for p in picks]
        for f in futs: print(json.dumps(f.result()))
