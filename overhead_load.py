"""Overhead Cost estate YTD (TM) dari Snowflake -> work/r_opex.json
Sumber data (lihat q_overhead.sql): aktual = PRS_COST.OPEX_BIAYA_UMUM (TM), budget = INT_COST.INT_COST_BUDGET (GROUP_LVL='OVERHEAD SITE', TM),
Jan..bln, BA 2122->2131, tanpa COA depresiasi (52010119%), 5201010598 (sewa AMP) dan 5201012001. Hasil per BA,COA disimpan di work/oh_ytd.txt (BA|COA|aktual ribu|budget ribu).
Total harus sama dgn ESTATE_COST BIAYA UMUM: Okt 2026: aktual 34416.4/14245.8/3809.4 jt, budget 33957.4/13716.1/4716.5 jt (2121/2124/2131).
python3 overhead_load.py w10/oh_ytd.txt 'YTD Jan–Okt 2026' w10/r_opex.json w10   (butuh w10/r_amp.json, r_ampb.json, coa_map.json, r_ce.json)   (grup/deskripsi COA dari map di bawah; Ha TM dari work/r_ce.json 'ha')"""
import sys,json
f,asof,out=sys.argv[1:4]
wd=sys.argv[4] if len(sys.argv)>4 else 'work'
_a=json.load(open(wd+'/r_amp.json'));_b=json.load(open(wd+'/r_ampb.json'))
AMP={k:[round(sum(_a[k])/1e3,1),round(sum(_b[k])/1e3,1)] for k in _a}  # ESTATE_COST COST SEWA AMP YTD (jt) aktual,budget, dari q_amp.sql
M=json.load(open(wd+'/coa_map.json'))   # coa -> [grup, deskripsi]
R={'2121':[],'2124':[],'2131':[]}
for l in open(f).read().split():
    b,c,a,g=l.split('|'); a=float(a);g=float(g)
    if a==0 and g==0: continue
    grp,d=M.get(c) or ['?','?']
    R[b].append([grp,int(c),d,round(g,3),round(a,3)])
ha=json.load(open(wd+'/r_ce.json'))['ha']
for b,v in R.items(): print(b,len(v),'bgt jt',round(sum(x[3] for x in v)/1e3,1),'act jt',round(sum(x[4] for x in v)/1e3,1),[x for x in v if x[0]=='?'])
json.dump({'asof':asof,'ha':ha,'amp':AMP,'rows':R},open(out,'w'),separators=(',',':'),ensure_ascii=False)
