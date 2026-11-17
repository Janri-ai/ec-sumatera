# Memuat hasil q_rawat_norma.sql dari WORKDIR/rawnorm.txt -> WORKDIR/r_rawnorm.json
# baris: 'BAafd|idx:Ha YTD,HK YTD,HK norma YTD,Ha bln,HK bln,HK norma bln;idx:...' (idx = Level 1 0..19)
import json,sys
W=sys.argv[1] if len(sys.argv)>1 else 'work'
D={}
for l in open(W+'/rawnorm.txt').read().splitlines():
    if not l.strip(): continue
    k,s=l.split('|')
    D[k]={i:[float(x) for x in v.split(',')] for i,v in (p.split(':') for p in s.split(';'))}
    for v in D[k].values(): assert len(v)==6,k
json.dump(D,open(W+'/r_rawnorm.json','w'),separators=(',',':'))
print(len(D),'afd; total Ha YTD',round(sum(v[0] for d in D.values() for v in d.values()),1),'HK',sum(v[1] for d in D.values() for v in d.values()))
