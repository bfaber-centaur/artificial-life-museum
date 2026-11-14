import json,sys,collections
w=sys.argv[1]; pa=sys.argv[2:] 
rows=[json.loads(l) for l in open(f'atlas-{w}.jsonl')]
ab={'ANNIHILATE':'x','SURVIVOR':'1','FUSE':'F','SCATTER':'S','MISS':'.','MULTIPLY':'M','EXPLODE':'E'}
for pair in sorted({(r['a'],r['b']) for r in rows}):
    rs=[r for r in rows if (r['a'],r['b'])==pair]
    th=sorted({r['theta'] for r in rs}); bs=sorted({r['b_R'] for r in rs})
    g={(r['theta'],r['b_R']):r for r in rs}
    print(pair, collections.Counter(r['class'] for r in rs))
    print('b_R  '+''.join(f'{b:>6}' for b in bs))
    for t in th:
        print(f'{t:4} ',''.join(f"{ab[g[(t,b)]['class']] if (t,b) in g else ' ':>6}" for b in bs))
