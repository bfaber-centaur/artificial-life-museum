"""HR-007: how fast do just-past-the-edge L4-001 runs die? (t0=1000, N=128, ref engine)

Prints the first step after the edit at which mass leaves the +-20% band and drops below 0.01.
Usage: PYTHONPATH=<L4 checkout>/src python deathtime.py <L4 checkout> > deathtime.txt
"""
import sys, numpy as np
L4DIR=sys.argv[1]
sys.path.insert(0, L4DIR + '/research/experiments/L4-001-disturbance-battery')
import run as L4
from alm import disturb
step = L4.engine('ref', 128, 13, 10)
A0, prev = L4.warm('ref', 128, 1000)
fr = disturb.frame_from(A0, prev)
for iv, ss in (('I001', (0.1031, 0.105, 0.11, 0.15, 0.3)), ('I003', (0.3094, 0.32, 0.4)), ('I004', (0.0844, 0.1, 0.2))):
    for s in ss:
        A = disturb.INTERVENTIONS[iv](A0, fr, s, 13); m = []
        for k in range(1, 2001):
            A = step(A); m.append(A.sum() / 169)
        m = np.array(m); dead = np.argmax(m < 0.01) + 1 if (m < 0.01).any() else None
        lo = np.argmax(m < 0.8 * 0.4358) + 1 if (m < 0.8*0.4358).any() else None
        hi = np.argmax(m > 1.2 * 0.4358) + 1 if (m > 1.2*0.4358).any() else None
        print(f"{iv} s={s}: first <0.8m at step {lo}, first >1.2m at {hi}, mass<0.01 at step {dead}, min/max mass {m.min():.3f}/{m.max():.3f}", flush=True)
