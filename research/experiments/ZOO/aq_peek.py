import sys, numpy as np, subprocess
from aquarium import *
from zoofilm import write_mp4
mode=sys.argv[1]; seed=int(sys.argv[2]); k=int(sys.argv[3]); tu=int(sys.argv[4]); out=sys.argv[5]
if mode=='bombard': r,fr,A=bombard(seed,k,tu,keep=5)
else: r,fr,A=soup(seed,tu,keep=10)
for row in r['series'][::max(1,len(r['series'])//12)]:
    print(row['t'], row['mass'], sorted([c['units'] for c in row['census']],reverse=True))
ims=[(np.clip(F.transpose(1,2,0),0,1)*255).astype(np.uint8) for F in fr]
write_mp4(ims,out,30,2 if mode=='bombard' else 1)
