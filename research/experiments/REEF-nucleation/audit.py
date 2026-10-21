"""Verify saved bytes and compare registered numerical checks, without simulations."""
import csv
import json
from pathlib import Path
import numpy as np
from run import HERE, R, filehash, write_json, state_sha256


def audit(root):
    groups={}
    for group in ('primary','N512','T20','direct','replay'):
        folder=root/group
        groups[group]={r['condition']:r for r in json.loads((folder/'summary.json').read_text())}
        plan=json.loads((folder/'plan.json').read_text())
        assert set(plan['order'])==set(groups[group])
        for name,r in groups[group].items():
            for filename,h in r['files'].items():
                assert filehash(folder/name/filename)==h,(group,name,filename)
            assert state_sha256(np.load(folder/name/'initial.npy'))==plan['inputs'][name]
    inputs=[]
    for name,r in groups['primary'].items():
        a=np.load(root/'primary'/name/'initial.npy'); y,x=np.mgrid[:a.shape[0],:a.shape[1]]
        cy,cx=r['center_yx']; mass=a.sum()
        gyr=float(np.sqrt((a*((y-cy)**2+(x-cx)**2)).sum()/mass)/R) if mass else None
        steps=list(csv.DictReader((root/'primary'/name/'steps.csv').open()))
        inputs.append(dict(condition=name,mass_R2=r['initial']['mass'],peak=r['peak'],
                           rms_radius_about_seed_R=gyr,support_radius_R=r['initial']['radius'],
                           extinct_by_tu=next((float(x['time']) for x in steps if float(x['mass'])==0),None)))
    checks=[]
    for group in ('N512','T20','direct','replay'):
        for name,r in groups[group].items():
            base=groups['primary'][name]
            def rows(g):return {float(x['time']):x for x in csv.DictReader((root/g/name/'series.csv').open())}
            a,b=rows('primary'),rows(group); times=sorted(a.keys()&b.keys())
            rel=[abs(float(a[t]['mass'])-float(b[t]['mass']))/float(a[t]['mass']) for t in times if float(a[t]['mass'])>=.01]
            rad=[abs(float(a[t]['radius'])-float(b[t]['radius'])) for t in times]
            checks.append(dict(group=group,condition=name,class_agrees=r['outcome']==base['outcome'],
                               common_through=max(times),mass_rel_max_above_001=max(rel,default=0),
                               radius_abs_max_R=max(rad,default=0),
                               within_numeric_tolerance=max(rel,default=0)<=.01 and max(rad,default=0)<=.1,
                               exact_final_hash=r['final_sha256']==base['final_sha256'] if group=='replay' else None))
    # Ring negative control must recover the actual field, not merely its mass.
    ring=np.load(root/'primary/ring/final.npy')
    negatives=dict(ring_bitwise_fixed=bool(np.array_equal(ring,np.load(root/'primary/ring/initial.npy'))),
                   half_contact_returns_ring=bool(np.array_equal(ring,np.load(root/'primary/contact0.5/final.npy'))))
    out=dict(inputs=inputs,checks=checks,negative_controls=negatives,all_recorded_file_hashes_verified=True)
    write_json(root/'audit.json',out)
    for c in checks:print(c)
    print(negatives)
    return out

if __name__=='__main__':audit(HERE/'results')
