# Usage: python3 oj_load.py work/oj.txt work/r_oj.json
# Optional argv[3] = work/oj_hk.txt (JAB|TIPE|BA|HK_YTD|HK_SEP) from INT_COST_ALOKASI SUM(HK) -> adds hk,hkSep to each [jt,org,jtSep,orgSep]
# Input: JAB|TIPE|BA|JT_YTD|ORANG_YTD|JT_SEP|ORANG_SEP (hasil q_oj.sql). Output {src,asof,rows:[[jab,tipe,{ba:[jt,org,jtSep,orgSep]}]]}
import sys,json
rows={}
tot={}
for l in open(sys.argv[1],encoding='utf-8'):
    p=l.rstrip('\n').split('|')
    if len(p)<7:continue
    k=(p[0],p[1]);rows.setdefault(k,{})[p[2]]=[float(p[3]),int(p[4]),float(p[5]),int(p[6])]
    t=tot.setdefault(p[2],[0,0]);t[0]+=float(p[3]);t[1]+=float(p[5])
if len(sys.argv)>3:
    hk={}
    for l in open(sys.argv[3],encoding='utf-8'):
        p=l.rstrip('\n').split('|')
        if len(p)>=5:hk[(p[0],p[1],p[2])]=[float(p[3]),float(p[4])]
    for k,v in rows.items():
        for b,a in v.items():a.extend(hk.get((k[0],k[1],b),[0.0,0.0]))
out={'src':'Snowflake INT_COST.INT_COST_ALOKASI, COA 5201010101 (BIAYA UMUM), BULAN Jan-Okt 2026','asof':'YTD Jan-Okt 2026','rows':[[k[0],k[1],v] for k,v in sorted(rows.items())]}
json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out['rows']),'jabatan;',{b:[round(x,1) for x in v] for b,v in tot.items()})
