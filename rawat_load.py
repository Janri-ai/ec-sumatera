# Memuat hasil q_rawat.sql (baris 'BAafd|ty,tby,tm,tbm,ha,hab|80 angka (20 level 1 x [ya,yb,ma,mb])') dari WORKDIR/rawat.txt -> WORKDIR/r_rawat.json
# urutan 20 level 1: 11 perawatan + 9 infra
import json,sys
W=sys.argv[1] if len(sys.argv)>1 else 'work'
D={}
for l in open(W+'/rawat.txt').read().splitlines():
    if not l.strip(): continue
    k,h,c=l.split('|');h=[float(x) for x in h.split(',')];c=[int(x) for x in c.split(',')]
    assert len(c)==80,k
    D[k]={"ha":h[4:6],"ton":h[0:4],"c":[c[i:i+4] for i in range(0,80,4)]}
json.dump(D,open(W+'/r_rawat.json','w'),separators=(',',':'))
for ba in ('2121','2124','2131'):
    ks=[k for k in D if k.startswith(ba)]
    for nm,rng in (('RAWAT',range(0,11)),('INFRA',range(11,20))):
        print(ba,nm,[sum(D[k]['c'][i][j] for k in ks for i in rng) for j in range(4)])
