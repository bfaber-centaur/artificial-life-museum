"""Cross-check reconstruct.py against upstream LeniaND.py Board/Automaton classes (CPU path).

Run from repo root: python research/specimens/S001-orbium/xcheck_upstream.py
Extracts the two classes from .refs/Lenia/Python/LeniaND.py with ast (no tkinter/reikna
needed; the GPU compile fails and upstream falls back to numpy), steps both 2000 times
on a 128x128 torus and prints the max abs difference."""
import ast, json, itertools, numpy as np, sys
from fractions import Fraction
N=128
src=open('.refs/Lenia/Python/LeniaND.py').read(); tree=ast.parse(src)
pick=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in ('Board','Automaton')]
ns=dict(np=np,itertools=itertools,Fraction=Fraction,DIM=2,DIM_DELIM={0:'',1:'$',2:'%'},DEF_R=13,EPSILON=1e-10,Z_AXIS=-3,X_AXIS=-1,Y_AXIS=-2,
        SIZE=[N,N],MID=[N//2,N//2],MIDX=N//2,MIDY=N//2,SIZEX=N,SIZEY=N,SIZER=N//2,SIZETH=N,SIZEF=N//2,ROUND=10)
exec(compile(ast.Module(pick,[]),'up','exec'),ns)
Board,Automaton=ns['Board'],ns['Automaton']
e=[x for x in json.load(open('.refs/Lenia/Python/animals.json')) if x.get('code')=='O2u'][0]
part=Board.from_data(e)
world=Board([N,N]); world.params={**part.params}
world.add(part)
auto=Automaton(world)
sys.path.insert(0,'research/specimens/S001-orbium'); import reconstruct as rc
A=np.zeros((N,N)); c=rc.rle2int(e['cells'])/255; h,w=c.shape; A[(N-h)//2:(N-h)//2+h,(N-w)//2:(N-w)//2+w]=c
print('initial identical:',np.array_equal(A,world.cells))
kfft,_=rc.make_kernel_fft(N,13,[1.0],'poly')
print('kernel FFT max|diff|:',np.abs(kfft-auto.kernel_FFT).max())
for t in range(1,2001):
    auto.calc_once(); A,_=rc.step(A,kfft,0.15,0.015,10,'poly')
    if t in (1,10,100,500,1000,2000): print(t,'max|diff|=%.3e'%np.abs(A-world.cells).max(),'mass up %.6f mine %.6f'%(world.cells.sum()/169,A.sum()/169))
