"""Tab Gaji & Premi. python3 gaji_load.py WORKDIR  (butuh WORKDIR/gaji.txt dan pan.txt) -> WORKDIR/r_gaji.json
gaji.txt = hasil q_gaji.sql: baris 'ba coa act[n bulan] bud[n bulan]' (ribu Rp).
Ton per bulan per BA = jumlah baris afd di pan.txt (ESTATE_COST TON_ACTUAL/TON_BUDGET).
Output {ba:{coa:[act12,bud12]}, '_ton':{ba:[[ton akt12],[ton bud12]]}}"""
import json,sys
W=sys.argv[1]
D={}
lines=[l for l in open(W+'/gaji.txt').read().splitlines() if l.strip()]
for ln in lines:
    ba,coa,a,b=ln.split()
    a=[int(x) for x in a.split(',')];b=[int(x) for x in b.split(',')]
    D.setdefault(ba,{})[coa]=[a+[0]*(12-len(a)),b+[0]*(12-len(b))]
TA={};TB={}
for l in open(W+'/pan.txt').read().splitlines():
    k,s=l.split('|');ba=k[:4]
    for r in s.split(';'):
        p=r.split(',');m=int(p[0])-1
        TA.setdefault(ba,[0]*12)[m]+=float(p[1]);TB.setdefault(ba,[0]*12)[m]+=float(p[2])
D['_ton']={b:[[round(x,1) for x in TA[b]],[round(x,1) for x in TB[b]]] for b in TA}
json.dump(D,open(W+'/r_gaji.json','w'),separators=(',',':'))
print(len(lines),'baris',{b:round(sum(v[0][:10]),1) for b,v in D['_ton'].items()})
