"""Jul-Sep BBC (Tbs Bulan Ke-1) per afd x tahun tanam dari file Tarikan BBC. python3 alloc_file.py FILE.xlsx REPORT_MONTH OUT.json"""
import sys,json,pandas as pd,warnings;warnings.filterwarnings('ignore')
f,m,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]
BA={'SEKERNAN ESTATE':'2121','SAWIT BRAHMA':'2124','PLASMA PEMAYUNG ESTATE':'2131'}
d=pd.read_excel(f,sheet_name='SAP');d=d[d['Nama Kebun'].isin(BA)].copy()
d['ba']=d['Nama Kebun'].map(BA);d['afd']=d['Afdeling'].astype(str).str.strip()
d['thn']=d['TAHUN TANAM'].apply(lambda x:str(int(x)) if x==x else None)
mp=d.dropna(subset=['thn']).groupby(['ba','afd','Blok']).thn.first()
d['thn']=[t if isinstance(t,str) else mp.get((b,a,k),'?') for t,b,a,k in zip(d.thn,d.ba,d.afd,d.Blok)]
g=d.groupby(['ba','afd','thn','MONTH'])['Tbs Bulan Ke-1'].sum()
r={}
for (ba,a,t,mo),v in g.items(): r.setdefault(f'{ba}|{a}|{t}',{})[str(m-3+int(mo))]=round(float(v),2)
json.dump(r,open(out,'w'));
for ba in BA.values():
    print(ba,{mo:round(sum(v.get(mo,0) for k,v in r.items() if k.startswith(ba))) for mo in ['7','8','9']})
