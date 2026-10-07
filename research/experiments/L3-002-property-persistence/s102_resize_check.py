"""Exploratory (not preregistered): does S102 survive refinement from differently resized seeds?

Usage: .venv/bin/python research/experiments/L3-002-property-persistence/s102_resize_check.py
"""
import numpy as np, sys
from scipy import ndimage
from multiprocessing import Pool
import alm_check.persistence as p
from alm_check.lenia import World, Rule, place
def go(job):
    R, method, horizon = job
    c = p.seed_cells('S102'); k = R//13
    if method=='block': c=np.kron(c,np.ones((k,k)))
    else: c=np.clip(ndimage.zoom(c, R/13, order={'nearest':0,'bilinear':1,'cubic':3}[method]),0,1)
    w=World(place(c,128*k),Rule(R=R,mu=0.155,sigma=0.020)); m=[]
    for s in range(int(horizon*10)):
        w.step()
        if s%10==9: m.append(w.A.sum()/R**2)
    m=np.array(m); dead=np.argmax(m<0.01) if (m<0.01).any() else None
    return R,method,'died at t=%d'%(dead+1) if dead is not None else 'alive, mass %.4f'%m[-100:].mean()
with Pool(4) as pool:
    for r in pool.map(go,[(R,mth,1000) for R in (26,39) for mth in ('block','nearest','bilinear','cubic')]): print(r)
