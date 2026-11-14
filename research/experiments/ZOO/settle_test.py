import sys,time
from zoocore import *; from zoocore import _radius
from alm.specimens import from_catalog
for code,N in [('O2u',128),('P6al',256),('P7al',256),('P8al',256),('P9al',256),('P10al',256),('C0v',128)]:
    s=from_catalog(code); t=time.time()
    A=s.place(N)
    A,m,v,alive,comps=settle(s.rule,A,100)
    print(code,N,f"m0={s.cells.sum()/255:.0f} m={m:.0f} v={v} speed={math.hypot(*v):.2f} c/tu  ({math.hypot(*v)/13:.3f} R/tu) head={heading_deg(v):.1f} ncomp={len(comps)} alive={alive} r={_radius(crop(A,comps[0]['c'],60)) if comps else 0:.0f} {time.time()-t:.1f}s",flush=True)
