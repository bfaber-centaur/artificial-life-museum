"""HR-007 discriminating runs for the L4-001 N=192 anomaly (PR #5).

Usage: PYTHONPATH=<L4 checkout>/src python hr007.py <L4 checkout> swap|refined > swap.csv|refined.csv
 mode=swap: N=128 runs using the N=192 centroid estimate.
mode=refined: all 40 L4-001 bracket runs at N=128 and N=192 with a bias-corrected centroid."""
import sys, csv, numpy as np
from multiprocessing import Pool
L4DIR = sys.argv[1]
sys.path.insert(0, L4DIR + '/research/experiments/L4-001-disturbance-battery')
import run as L4
from alm import disturb

_orig_frame = disturb.frame_from

def refined_centroid(A, it=3):
    ny, nx = A.shape
    cx, cy = disturb.periodic_centroid(A)
    m = A.sum(); px, py = A.sum(0), A.sum(1)
    for _ in range(it):
        cx = (cx + (px * disturb.wrap(np.arange(nx) - cx, nx)).sum() / m) % nx
        cy = (cy + (py * disturb.wrap(np.arange(ny) - cy, ny)).sum() / m) % ny
    return cx, cy

def refined_frame(A, prev):
    ny, nx = A.shape
    cx, cy = refined_centroid(A)
    f = _orig_frame(A, prev)       # heading as before (10-step displacement)
    return disturb.Frame(cx, cy, f.hx, f.hy)

def job(args):
    mode, iv, s, t0, N, delta = args
    disturb.frame_from = _orig_frame
    if mode == 'refined':
        disturb.frame_from = refined_frame
    elif mode == 'swap':
        def shifted(A, prev):
            f = _orig_frame(A, prev)
            return disturb.Frame(f.cx + delta[0], f.cy + delta[1], f.hx, f.hy)
        disturb.frame_from = shifted
    r = L4.run(iv, s, t0, N, 'ref')
    return mode, iv, s, t0, N, r['achieved_dmass_frac'], r['class']

if __name__ == '__main__':
    mode = sys.argv[2]
    if mode == 'swap':
        # deltas = centroid(N=192) - centroid(N=128), aligned, measured in n192.py
        jobs = [('swap','I002',0.059375,1000,128,(0.4248-0.4287,0.5133-0.5201)),
                ('swap','I002',0.078125,1004,128,(0.3926-0.3965,0.8112-0.8178)),
                ('swap','I003',0.315625,1003,128,(0.1559-0.1598,0.2472-0.2537)),
                ('none','I002',0.059375,1000,128,(0,0)),
                ('none','I002',0.078125,1004,128,(0,0)),
                ('none','I003',0.315625,1003,128,(0,0))]
    else:
        rows = list(csv.DictReader(open(L4DIR + '/research/experiments/L4-001-disturbance-battery/results/check-ref-N192.csv')))
        jobs = [('refined', r['intervention'], float(r['strength']), int(r['t0']), N, None)
                for r in rows for N in (128, 192)]
    with Pool() as p:
        res = p.map(job, jobs, chunksize=1)
    print('mode,intervention,strength,t0,N,achieved_dmass_frac,class')
    for r in res:
        print('%s,%s,%.6f,%d,%d,%.5f,%s' % r, flush=True)
