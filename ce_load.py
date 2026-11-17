"""Tab Cost Element. python3 ce_load.py WORKDIR  (butuh WORKDIR/ce_h.txt, ce_v.txt, pan.txt, r_main.json) -> WORKDIR/r_ce.json
ce_h.txt  = hierarki 'id|GROUP|L1|L2|L3' (q_ce.sql query 1, id urut); ce_v.txt = 'ba|id:ya,yb,ma,mb;...' (q_ce.sql query 2, ribu Rp).
Ton: aktual dan budget per bulan = jumlah per BA dari baris afd di pan.txt (ESTATE_COST TON_ACTUAL/TON_BUDGET, PMY A+C). Ha TM = ESTATE_COST HA_ACTUAL/HA_BUDGET bulan laporan (r_main baris M)."""
import json,sys
W=sys.argv[1]
rows=[l.split('|') for l in open(W+'/ce_h.txt',encoding='utf-8').read().splitlines() if l.strip()]
assert [int(r[0]) for r in rows]==list(range(1,len(rows)+1))
vals={}
for l in open(W+'/ce_v.txt',encoding='utf-8').read().splitlines():
    if not l.strip(): continue
    ba,s=l.split('|',1)
    vals[ba]={int(x.split(':')[0]):[int(float(n)) for n in x.split(':')[1].split(',')] for x in s.split(';')}
TA={};TB={}
for l in open(W+'/pan.txt').read().splitlines():
    k,s=l.split('|');ba=k[:4]
    for r in s.split(';'):
        p=r.split(',');m=int(p[0])-1
        TA.setdefault(ba,{}).setdefault(m,0);TB.setdefault(ba,{}).setdefault(m,0)
        TA[ba][m]+=float(p[1]);TB[ba][m]+=float(p[2])
ton={}
for b in TA:
    a=[TA[b][m] for m in sorted(TA[b])];t=[TB[b][m] for m in sorted(TB[b])]
    ton[b]=[round(sum(a),1),round(sum(t),1),round(a[-1],1),round(t[-1],1)]
mm=json.load(open(W+'/r_main.json'));HA={}
for r in mm:
    if r[2]=='M':
        h=HA.setdefault(r[0],[0,0]);h[0]+=r[9];h[1]+=r[10]
HA={b:[round(v[0],2),round(v[1],2)] for b,v in HA.items()}
out={'ha':HA,'ton':ton,'h':[r[1:] for r in rows],'v':{ba:{str(k):v for k,v in d.items()} for ba,d in vals.items()}}
json.dump(out,open(W+'/r_ce.json','w'),separators=(',',':'),ensure_ascii=False)
print({ba:(round(sum(v[0] for v in d.values())/1e3),round(sum(v[1] for v in d.values())/1e3)) for ba,d in vals.items()},'juta akt,bud YTD');print(ton,HA)
