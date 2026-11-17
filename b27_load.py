"""Budget 2027 (tab B7): python3 b27_load.py work/kk_ol.xlsx work/r_b27.json
Sumber: file KK_OL.xlsx, sheet SKR/SBR/PMY (struktur kolom: YTD Sept = E,G,H; Taksasi Okt-Des = J,K,L,N; OL 2026 = O,Q,R; Budget 2026 = S,U,V; ton = baris 9 kolom F,J,K,L,N,P,T; Ha TM = H9,R9,V9).
Final Budget 2027 = AA,AC,AD (Rp, Rp/Kg, Rp/Ha), ton AB9, Ha AD9; baris: idx15=nomor baris, 16-18 = Final Budget 2027. Rupiah dalam ribu. Ref: aktual YTD dan budget setahun dari r_sd.json (ESTATE_COST) untuk cek silang."""
import sys,json,os
from openpyxl import load_workbook
src,out=sys.argv[1],sys.argv[2]
wb=load_workbook(src,data_only=True)
MAP={'SKR':'2121','SBR':'2124','PMY':'2131'}
def num(v):
    return float(v) if isinstance(v,(int,float)) and not isinstance(v,bool) else None
COLS=['E','G','H','J','K','L','N','O','Q','R','S','U','V']
CF=['AA','AC','AD']  # Final Budget 2027: Rp, Rp/Kg, Rp/Ha
KEY={'BIAYA PENYUSUTAN','MAINTENANCE VRA','BIAYA UMUM','EXCL PUPUK','RAWAT + INFRA','RAWAT ONLY','INFRA','EC EXCL BIAYA UMUM'}
res={}
sd=json.load(open(os.path.join(os.path.dirname(src),'r_sd.json')))['ba'] if os.path.exists(os.path.join(os.path.dirname(src),'r_sd.json')) else {}
for sh,ba in MAP.items():
    ws=wb[sh];g=lambda c,r:ws[f'{c}{r}'].value
    ton={'ytd':num(g('F',9)),'tak':[num(g(c,9)) for c in 'JKLN'],'ol':num(g('P',9)),'bud':num(g('T',9)),'b27':num(g('AB',9))}
    ha={'ytd':num(g('H',9)),'ol':num(g('R',9)),'bud':num(g('V',9)),'b27':num(g('AD',9))}
    rows=[];sec=None
    for r in range(11,177):
        C=g('C',r);D=g('D',r)
        C=str(C).strip() if C is not None else '';Draw=str(D) if D is not None else '';D=Draw.strip()
        vals=[num(g(c,r)) for c in COLS]
        fv=[num(g(c,r)) for c in CF]
        has=any(v not in (None,0.0) for v in vals+fv)
        if C and C!='-' and not C.startswith('Total'):
            rows.append(['H',C]+[None]*13+[r]+[None]*3);continue
        if not (C or D):continue
        if C.startswith('Total'):typ='T';lab=C
        elif C=='-':typ='1';lab=D
        elif D in KEY:typ='K';lab=D
        else:
            if D.startswith('Jumlah bulan'):continue
            typ='2';lab=D
        if not has:continue
        rows.append([typ,lab]+vals+[r]+fv)
    # total biaya kebun
    tk=[x for x in rows if x[1]=='Total Biaya Kebun'][0]
    d=sd.get(ba)
    ref=None
    if d:ref={'ytd_jt':sum(d['a']),'bud_jt':sum(d['b9'])+sum(d['bq4']),'ol_ton':d['ton9']+d['q4ol'],'ton9':d['ton9'],'tgt':d['tgt'],'ovh_bud_jt':d['b9'][5]+d['bq4'][5]}
    res[ba]={'sheet':sh,'ton':ton,'ha':ha,'rows':rows,'ref':ref}
    print(ba,sh,'rows',len(rows),'Total Biaya Kebun YTD jt',round(tk[2]/1e3,1),'OL jt',round(tk[9]/1e3,1),'Bud jt',round(tk[12]/1e3,1),'| ref',ref and (round(ref['ytd_jt'],1),round(ref['bud_jt'],1)))
lab={ba:{r[15]:(r[0],r[1]) for r in v['rows']} for ba,v in res.items()}
bad=0
for rn in set().union(*[set(x) for x in lab.values()]):
    s={x[rn][1].strip() for x in lab.values() if rn in x}
    if len(s)>1:bad+=1;print('LABEL BEDA baris',rn,s)
print('label beda antar sheet:',bad)
json.dump({'src':'KK_OL.xlsx (sheet SKR, SBR, PMY)','ba':res},open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
