from zoocore import *
import sys
code,N,half=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
s=from_catalog(code)
A,m,v,alive,comps=settle(s.rule,s.place(N),100)
p0=crop(A,comps[0]['c'],half)
h0=heading_deg(v)
for rot in range(0,360,30):
    b=make_body('t',s.rule,code,p0,rot,N,30,half)
    print(rot, f"expect {(h0+rot)%360:.1f} got {b.heading} speed {b.speed:.2f} mass {b.mass:.1f} alive {b.alive} {b.note}",flush=True)
