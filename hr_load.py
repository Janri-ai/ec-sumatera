"""Rasio Org/Ha (tab HR): python3 hr_load.py work work/r_hr.json
Input: work/r_hc.json (staff per kelompok sheet FIX), work/r_hcns.json (INT_MPE per kelas bulan 09, nik payroll, Ha planted),
work/hr_extra.txt (PMY 2131: mpe INT_MPE, nik payroll, ha TM/TBM; hasil query Snowflake manual, akhir Sep 2026).
Ha planted = KATEGORI_TANAH PLANTED = MATURITY_STATUS TM + TBM 3 (INT_HEKTAR_BLOK, akhir bulan realisasi)."""
import sys,json,os
wd,out=sys.argv[1],sys.argv[2]
hc=json.load(open(os.path.join(wd,'r_hc.json')));hn=json.load(open(os.path.join(wd,'r_hcns.json')))
staff={g['g']:sum(x['mpe'] for x in g['n']) for g in hc['g']}
mpe={b:sum(v[i] for v in hn['cls']['09'].values()) for i,b in enumerate(['2121','2124','2123'])}
nik=dict(hn['nik']);ha={b:dict(v) for b,v in hn['ha'].items()}
for l in open(os.path.join(wd,'hr_extra.txt'),encoding='utf-8'):
    if l.startswith('#') or not l.strip():continue
    k,b,v=l.strip().split('|')
    if k=='mpe':mpe[b]=int(v)
    elif k=='nik':nik[b]=int(v)
    else:ha.setdefault(b,{})[k]=float(v)
res={'asof':hn['haAsof'],'staff':staff,'mpe':mpe,'nik':nik,'ha':ha,'src_staff':hc['src']}
json.dump(res,open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(json.dumps(res,ensure_ascii=False))
