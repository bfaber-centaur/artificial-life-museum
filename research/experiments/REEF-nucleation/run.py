"""Focused empty-world control; see PROTOCOL.md before running."""
from __future__ import annotations
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import csv
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / 'src'), str(HERE.parent / 'REEF-behavior')]
from alm.lenia import Lenia, Rule
from alm.provenance import state_sha256, environment
from track import components

FIELD = HERE.parent / 'REEF-field'
R = 13
BASE = '190b2b9dbb056105db714f9eef88c3de1a8935cd'

def filehash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def write_json(p, obj):
    p.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + '\n')

def seed(name):
    p = FIELD / 'seeds' / (name + '.npy')
    a = np.load(p, allow_pickle=False)
    m = json.loads(Path(str(p) + '.json').read_text())
    if state_sha256(a) != m['state_sha256'] or filehash(p) != m['file_sha256']:
        raise ValueError('source seed hash mismatch: ' + name)
    return a, m

def conditions():
    return ([f'A{d:g}' for d in (.25,.5,.75,1,1.25,1.45)] +
            [f'B{d:g}' for d in (1.5,2,3,4,6,8,12,16)] +
            ['blank','ring','contact0.5','contact0.75','contact1'])

def initial(name, n=256):
    if n not in (256,512):
        raise ValueError('N must be 256 or 512')
    b, meta = seed('BLOB-X9')
    center = np.array(meta['construction']['centre_yx'])
    shift = 128 - np.rint(center).astype(int)
    center += shift
    ring, _ = seed('S103')
    ring = np.roll(ring, (64,20), (0,1))
    if name.startswith('A'):
        d = float(name[1:])
        # Preserve original floating-point construction for historical controls.
        b = seed({.5:'BLOB-X11',.75:'BLOB-X12',1.:'BLOB-X9'}[d])[0] if d in (.5,.75,1.) else b*d
        a = np.roll(b, shift, (0,1))
    elif name.startswith('B'):
        d = float(name[1:]); s = meta['construction']['s_cells'] * np.sqrt(d)
        y,x = np.mgrid[:256,:256]
        rr = (y-center[0])**2 + (x-center[1])**2
        a = np.where(rr <= (4*s)**2, meta['construction']['a']*np.exp(-rr/(2*s*s)), 0.)
    elif name == 'blank':
        a = np.zeros_like(b)
    elif name == 'ring':
        a = np.roll(ring, shift, (0,1))
    elif name.startswith('contact'):
        d = float(name[7:]); b = seed({.5:'BLOB-X11',.75:'BLOB-X12',1.:'BLOB-X9'}[d])[0]
        a = np.roll(b+ring, shift, (0,1))
    else:
        raise ValueError(name)
    if not np.isfinite(a).all() or a.min()<0 or a.max()>1:
        raise ValueError('invalid input; clipping forbidden')
    pad = (n-256)//2
    return np.pad(a, pad), center+pad

def guarded(a):
    return bool(np.any(a[:R]>1e-12) or np.any(a[-R:]>1e-12) or
                np.any(a[:,:R]>1e-12) or np.any(a[:,-R:]>1e-12))

def measure(a, center):
    y,x = np.nonzero(a >= .01)
    radius = float(np.hypot(y-center[0], x-center[1]).max()/R) if len(y) else 0.
    return dict(mass=float(a.sum()/R**2), radius=radius,
                bodies=sum(c.mass/R**2 >= .005 for c in components(a,.01)))

def classify(rows):
    if not rows or rows[-1]['time'] < 10:
        return 'UNRESOLVED'
    tail = [r for r in rows if r['time'] >= rows[-1]['time']-5-1e-9]
    if len(tail)<6:
        return 'UNRESOLVED'
    m=np.array([r['mass'] for r in tail]); rad=np.array([r['radius'] for r in tail])
    if np.all(m<1e-10): return 'EVAPORATION'
    grow = np.all(m>=max(2,4*rows[0]['mass'])) and m[-1]-m[0]>=.5
    if grow and all(r['bodies']>=4 for r in tail) and rad[-1]-rad[0]>=.5 and rad[-1]>=rows[0]['radius']+2:
        return 'EXPANDING_COLONY'
    if grow: return 'SUSTAINED_GROWTH'
    if np.all(m>=.01) and np.all(rad<=3) and np.ptp(m)<=.01*m.mean() and np.ptp(rad)<=.1:
        return 'STABLE_LOCALIZED'
    return 'UNRESOLVED'

def run_one(name, out, n, T, engine, horizon):
    out.mkdir()
    a, center = initial(name,n)
    np.save(out/'initial.npy', a)
    rule=Rule(R=R,T=T,mu=.155,sigma=.020)
    if engine=='alm': sim=Lenia(rule,a)
    else:
        from alm_check.lenia import World, Rule as CheckRule
        sim=World(a.copy(), CheckRule(R=R,T=T,mu=.155,sigma=.020), path='direct')
    rows=[]; steps=[]; states={}; previous=a.copy(); censor=None
    for step in range(int(horizon*T)+1):
        boundary=guarded(sim.A)
        steps.append(dict(step=step,time=step/T,mass=float(sim.A.sum()/R**2),guard=boundary))
        if boundary:
            censor=step/T
            break
        if step % T == 0:
            rows.append(dict(time=step/T, **measure(sim.A,center),
                             max_change=float(np.max(np.abs(sim.A-previous)))))
            states[f'step_{step:05d}']=sim.A.copy(); previous=sim.A.copy()
        if step<int(horizon*T): sim.step()
    np.save(out/'final.npy',sim.A)
    np.savez_compressed(out/'snapshots.npz',**states)
    for filename, data in [('series.csv',rows),('steps.csv',steps)]:
        with (out/filename).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    result=dict(condition=name, outcome=classify(rows), censored_at=censor,
                scored_through=rows[-1]['time'], final=rows[-1], initial=rows[0],
                center_yx=center.tolist(), peak=float(a.max()),
                initial_sha256=state_sha256(a),final_sha256=state_sha256(sim.A),
                final_time=steps[-1]['time'],rule=rule.to_dict(),N=n,engine=engine,
                horizon=horizon,files={p.name:filehash(p) for p in out.iterdir() if p.is_file()})
    write_json(out/'result.json',result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--N',type=int,choices=[256,512],default=256)
    p.add_argument('--T',type=int,choices=[10,20,40,80],default=10)
    p.add_argument('--engine',choices=['alm','direct'],default='alm')
    p.add_argument('--horizon',type=int,choices=range(10,51),default=25)
    p.add_argument('--cases',nargs='+',choices=conditions())
    p.add_argument('--plan-only',action='store_true')
    args=p.parse_args()
    jobs=list(args.cases or conditions()); random.Random(20261021).shuffle(jobs)
    args.out.mkdir(parents=True,exist_ok=False)
    plan=dict(base=BASE,seed=20261021,order=jobs,N=args.N,T=args.T,engine=args.engine,
              horizon=args.horizon,environment=environment(),
              git_sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              git_status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),
              sources={str(p.relative_to(ROOT)):filehash(p) for p in
                       [Path(__file__), HERE/'PROTOCOL.md',ROOT/'src/alm/lenia.py',
                        ROOT/'src/alm_check/lenia.py',HERE.parent/'REEF-behavior/track.py']},
              inputs={name:state_sha256(initial(name,args.N)[0]) for name in jobs})
    write_json(args.out/'plan.json',plan)
    if args.plan_only:return
    results=[]
    for name in jobs:
        r=run_one(name,args.out/name,args.N,args.T,args.engine,args.horizon)
        results.append(r); write_json(args.out/'summary.json',results)
        print(name,r['outcome'],'through',r['scored_through'],'M',round(r['final']['mass'],5),
              'radius',round(r['final']['radius'],3),'censor',r['censored_at'],flush=True)

if __name__=='__main__': main()
