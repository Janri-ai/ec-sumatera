# Memuat hasil q_rawat_out.sql dari WORKDIR/rawout.txt -> WORKDIR/r_rawout.json
# baris: 'BAafd|idx:Ha YTD,HK YTD,Ha RKT YTD,Ha bln,HK bln,Ha RKT bln;idx:...' (idx = Level 1 0..19)
import json,sys
W=sys.argv[1] if len(sys.argv)>1 else 'work'
D={}
for l in open(W+'/rawout.txt').read().splitlines():
    if not l.strip(): continue
    k,s=l.split('|')
    D[k]={i:[float(x) for x in v.split(',')] for i,v in (p.split(':') for p in s.split(';'))}
    for v in D[k].values(): assert len(v)==6,k
json.dump(D,open(W+'/r_rawout.json','w'),separators=(',',':'))
print(len(D),'afd; total Ha dikerjakan YTD',round(sum(v[0] for d in D.values() for v in d.values()),1),'HK',sum(v[1] for d in D.values() for v in d.values()))
