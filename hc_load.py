"""Head count MPE staff Sumatera, HANYA dari sheet 'FIX Region Kalteng & Sumatera' (file d0843483, layout baru khusus Sumatera).
Usage: python3 hc_load.py <xlsx> <out_json>
Blok kolom (judul baris 1-3): A = jabatan.
  B-H  'BBB - SEKERNAN & BBB - BATANG HARI': MPP 2026 B, MPE existing C, AFD D, nama existing E, MPE plan F, nama plan G, varian H(=F-B)
  I-O  'BBB - BRAHMA SAWIT & BBB - BRAHMA KARET': MPP I, MPE existing J, AFD K, nama L, MPE plan M, nama plan N
  V-AA 'RO - SUMATERA': MPP V, existing W, nama X, plan Y, nama plan Z
  AB-AG 'HPS': TIDAK dipakai (diminta dihapus).
  P-U 'RO - KALTENG' tidak dipakai.
Baris tanpa isi kolom A = lanjutan jabatan di atasnya (nama tambahan). Seksi = header 'ESTATE - ...'; baris TOTAL per seksi dan GRAND TOTAL dipakai validasi.
'plasma' -> 'KEMITRAAN'. Nama dengan '(CONCUR)' (rangkap jabatan) dibuang dari daftar nama; di sheet baris itu memang tanpa angka MPP/MPE."""
import sys,json,re,openpyxl
from openpyxl.utils import column_index_from_string as ci
f,out=sys.argv[1],sys.argv[2]
ws=openpyxl.load_workbook(f,data_only=True)['FIX Region Kalteng & Sumatera']
BL=[('BBB - SEKERNAN & BATANG HARI',dict(mpp='B',mpe='C',af='D',nm='E',pl='F',np='G')),
    ('BBB - BRAHMA SAWIT & KARET',dict(mpp='I',mpe='J',af='K',nm='L',pl='M',np='N')),
    ('RO - SUMATERA',dict(mpp='V',mpe='W',af=None,nm='X',pl='Y',np='Z'))]
kp=lambda t:re.sub(r'(?i)plasma','KEMITRAAN',t)
def num(v):return v if isinstance(v,(int,float)) else 0
def cv(r,c):return ws.cell(r,ci(c)).value
sec=None;rows=[];tot={};grand=None;cur=None
for r in range(4,200):
    a=cv(r,'A')
    a=re.sub(r'\s+',' ',str(a)).strip() if a is not None else ''
    if not a:
        if cur:rows.append((r,sec,cur))
        continue
    if a.startswith('ESTATE - '):sec=a[9:].strip().title();cur=None;continue
    if a=='TOTAL':tot[sec]=r;cur=None;continue
    if a=='GRAND TOTAL':grand=r;break
    cur=kp(a);rows.append((r,sec,cur))
res=[];bad=0
for gn,c in BL:
    order=[];D={}
    for r,s,j in rows:
        k=(s,j)
        d=D.get(k)
        if d is None:
            d=D[k]={'j':j,'s':s,'mpp':0,'mpe':0,'pl':0,'nm':[],'np':[]};order.append(k)
        for key in('mpp','mpe','pl'):d[key]+=num(cv(r,c[key]))
        af=(re.sub(r'\s+',' ',str(cv(r,c['af']))).strip() if c['af'] and cv(r,c['af']) else '')
        for kk,col in(('nm',c['nm']),('np',c['np'])):
            v=cv(r,col)
            if v:
                for ln in re.sub(r'\s*\n\s*\(\s*concur\s*\)',' (CONCUR)',str(v),flags=re.I).split('\n'):
                    ln=ln.strip()
                    if re.search(r'(?i)concur',ln):continue  # rangkap jabatan (CONCUR): dianggap tidak ada
                    if ln:D[k][kk].append(kp(((af+' · ') if af and kk=='nm' else '')+ln))
    # validasi: jumlah per seksi dan grand total terhadap baris TOTAL sheet
    for key in('mpp','mpe','pl'):
        for s,tr in tot.items():
            mine=sum(D[k][key] for k in order if k[0]==s)
            if abs(mine-num(cv(tr,c[key])))>1e-9:bad+=1;print('BEDA',gn,s,key,mine,cv(tr,c[key]))
        g=sum(D[k][key] for k in order)
        if abs(g-num(cv(grand,c[key])))>1e-9:bad+=1;print('BEDA GRAND',gn,key,g,cv(grand,c[key]))
    res.append({**({'x':1} if c.get('x') else {}),'g':gn,'n':[D[k] for k in order if D[k]['mpp'] or D[k]['mpe'] or D[k]['pl'] or D[k]['nm'] or D[k]['np']]})
src="File MPP MPE 2026 closing data (14 September, versi revisi), sheet 'FIX Region Kalteng & Sumatera', blok SUMATERA, RO Sumatera"
json.dump({'g':res,'src':src},open(out,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
for g in res:print(g['g'],len(g['n']),'jabatan | MPP',sum(x['mpp'] for x in g['n']),'MPE',sum(x['mpe'] for x in g['n']),'plan',sum(x['pl'] for x in g['n']))
print('validasi beda:',bad,'| plasma?', 'plasma' in open(out,encoding='utf-8').read().lower())
