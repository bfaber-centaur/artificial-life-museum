"""HR-007: compare the L4-001 edit at N=128 vs N=192 (same creature, aligned on the torus).

Prints the state difference at t0, both circular-mean centroids (192 shifted into the 128 frame),
and how many cells the I002/I003/I004 edit masks differ by.
Usage: PYTHONPATH=<L4 checkout>/src python n192.py <L4 checkout> > edit_placement.txt
(<L4 checkout> = a checkout of branch claude/night0-disturbance-np4adr, PR #5.)
"""
import sys, numpy as np
sys.path.insert(0, sys.argv[1] + '/research/experiments/L4-001-disturbance-battery')
import run as L4
from alm import disturb
cases=[("I002",0.059375,1000),("I002",0.078125,1004),("I003",0.315625,1003),
       ("I002",0.084375,1001),("I003",0.30625,1000),("I004",0.08125,1000)]
for iv,s,t0 in cases:
    out={}
    for N in (128,192):
        A,prev=L4.warm("ref",N,t0)
        fr=disturb.frame_from(A,prev)
        B=disturb.INTERVENTIONS[iv](A,fr,s,13)
        out[N]=(A,B,fr)
    A1,B1,f1=out[128]; A2,B2,f2=out[192]
    ox=int(round(f2.cx-f1.cx)); oy=int(round(f2.cy-f1.cy))
    # put the 128 creature into a 192 frame at the same place, compare on the 192 torus
    def emb(X):
        Z=np.zeros((192,192)); Z[:128,:128]=X
        # move a 64-cell margin: shift so creature is away from the 128 window edge first
        return Z
    sh1=(64-int(f1.cy), 64-int(f1.cx))
    A1s=np.roll(A1,sh1,(0,1)); B1s=np.roll(B1,sh1,(0,1))
    sh2=(64-int(f1.cy)-oy, 64-int(f1.cx)-ox)
    A2c=np.roll(A2,sh2,(0,1))[:128,:128]; B2c=np.roll(B2,sh2,(0,1))[:128,:128]
    A1,B1=A1s,B1s
    f2=disturb.Frame(f2.cx-ox,f2.cy-oy,f2.hx,f2.hy); o=0
    # creature region must be inside the 128 window: check mass captured
    capt=A2c.sum()/A2.sum()
    d1=(B1!=A1); d2=(B2c!=A2c)
    print(f"{iv} s={s:.4f} t0={t0}: capt={capt:.6f} max|dA|={np.abs(A1-A2c).max():.1e} "
          f"centroid128=({f1.cx:.4f},{f1.cy:.4f}) centroid192-off=({f2.cx-o:.4f},{f2.cy-o:.4f}) "
          f"heading diff={np.degrees(np.arctan2(f1.hy,f1.hx)-np.arctan2(f2.hy,f2.hx)):.4f}deg "
          f"edited cells 128/192={d1.sum()}/{d2.sum()} mask differs at {(d1!=d2).sum()} cells, "
          f"max|dB|={np.abs(B1-B2c).max():.2e}", flush=True)
