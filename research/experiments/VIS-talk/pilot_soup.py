"""Soup amplitude pilot (VIS-talk, 2026-11-07), as run before G010; 6 seeds per setting, 100 tu.

Run twice: first with sides (26, 40) x amplitudes (0.5, 1.0) -> every run died; then, as below,
sides (40, 80) x amplitudes (0.25, 0.3, 0.35) -> side 40 all died; side 80: 0.25 all died,
0.3 two filled and one Orbium-mass survivor, 0.35 one filled. Prints (mass/R^2, components, fill).
"""
import os; os.environ["OMP_NUM_THREADS"]="1"
import sys, numpy as np
sys.path.insert(0,'research/experiments/L6-field')
from alm.lenia import Lenia, Rule
from field import components
rule = Rule(R=13,T=10,mu=0.15,sigma=0.015)
N=256
for side in (40, 80):
  for amp in (0.25, 0.3, 0.35):
    res=[]
    for seed in range(6):
        rng=np.random.default_rng(seed)
        A=np.zeros((N,N)); o=(N-side)//2
        A[o:o+side,o:o+side]=rng.random((side,side))*amp
        s=Lenia(rule,A)
        for _ in range(1000): s.step()
        m=s.A.sum()/169; res.append((round(m,2), components(s.A), round(float((s.A>0.1).mean()),3)))
    print(side, amp, res, flush=True)
