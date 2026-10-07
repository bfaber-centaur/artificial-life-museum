#!/usr/bin/env python3
"""HR-003 check (exploratory): is Lane 5's 8.0-step anisotropy period at R=13 a lattice line?

Independent second-moment anisotropy (1 - lambda_min/lambda_max about a bias-corrected periodic
centroid), rotation 0, R in {13, 20, 26}, steps 1000-2999. Prints mean, sd, dominant period and
the nearest low-order lattice line.

Usage (repo root): .venv/bin/python research/experiments/H001-lattice-wobble/aniso_check.py
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import h001, numpy as np
def aniso(A,N,c):
    i=np.arange(N)
    dx=(i[None,:]-c[0]+N/2)%N-N/2; dy=(i[:,None]-c[1]+N/2)%N-N/2
    m=A.sum(); xx=(A*dx*dx).sum()/m; yy=(A*dy*dy).sum()/m; xy=(A*dx*dy).sum()/m
    w=np.linalg.eigvalsh([[xx,xy],[xy,yy]]); return 1-w[0]/w[1]
for R in (13,20,26):
    N=h001.grid_size(R); A=h001.initial_state(R,0,N)
    k,_=h001.rc.make_kernel_fft(N,R,[1.0],'poly'); an=[];cs=[]
    for t in range(3000):
        A,_=h001.rc.step(A,k,.15,.015,10,'poly')
        if t>=1000:
            c=h001.centroid(A,N); cs.append(c)
            # refine centroid linear about circular mean
            i=np.arange(N); m=A.sum()
            c=(c[0]+(A.sum(0)*((i-c[0]+N/2)%N-N/2)).sum()/m, c[1]+(A.sum(1)*((i-c[1]+N/2)%N-N/2)).sum()/m)
            an.append(aniso(A,N,c))
    an=np.array(an); vx,vy=h001.velocity(np.array(cs),N); f=h001.dominant_freq(an)
    x=(an-an.mean())*np.hanning(len(an)); P=np.abs(np.fft.rfft(x))**2; fr=np.fft.rfftfreq(len(an))
    top=np.argsort(P[1:])[::-1][:6]+1
    print(R, 'aniso mean %.4f sd %.2e'%(an.mean(),an.std()), 'peak period %.3f'%(1/f), h001.nearest_line(f,vx,vy), 'top periods',np.round(1/fr[top],2), flush=True)
