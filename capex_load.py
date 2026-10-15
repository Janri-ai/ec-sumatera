"""Capex estate: xlsx 'Report Summary Capex 2026 - Update <tgl>.xlsx' (sheet Estate, Ledger, Budget) -> work/r_capex.json
python3 capex_load.py work/capex.xlsx '10 Okt 2026' work/r_capex.json
Dept: S21 BBB S = Sekernan (terbukti dari teks ledger 'MINI MARKET ... BBB SEKERNAN'), S22 BBB P = Pemayung, S23 BBB K = Karet, S24 BBB SK = Sawit Brahma (dugaan: sisa eliminasi)."""
import sys,json,collections,openpyxl,warnings;warnings.filterwarnings('ignore')
f,asof,out=sys.argv[1:4]
wb=openpyxl.load_workbook(f,data_only=True)
D={'S21':'Sekernan Estate','S22':'Pemayung','S23':'Karet','S24':'Sawit Brahma'}
est=[r for r in wb['Estate'].iter_rows(min_row=5,min_col=2,max_col=13,values_only=True) if r[0] in D]
led=[r for r in wb['Ledger'].iter_rows(min_row=3,min_col=2,max_col=26,values_only=True) if r[2] and str(r[7]).strip() in D]
bud=[r for r in wb['Budget'].iter_rows(min_row=5,min_col=2,max_col=23,values_only=True) if r[0] in D]
AK={'1207010101':'CAPEX non-budgeted','1207010201':'Bangunan dan perumahan','1207010301':'Jalan, jembatan dan gorong-gorong','1207010401':'Kendaraan dan alat berat','1207010501':'Mesin dan pompa','1207010601':'Peralatan kerja, workshop dan IT','1207010701':'Inventaris dan perlengkapan','1207010801':'Instalasi listrik dan air'}
tx=collections.defaultdict(list)
for r in led: tx[r[17]].append([r[3].strftime('%Y-%m-%d'),str(r[2]),str(r[13] or '').strip(),round((r[9] or 0)/1e6,4),r[10],r[3].year,str(r[21] or '')])
bm=collections.defaultdict(lambda:[0.0]*12)
for r in bud: bm[r[0]][int(r[1])-1]+=(r[9] or 0)/1e6
tm=collections.defaultdict(lambda:[0.0]*12)
for r in led: tm[str(r[7]).strip()][int(r[10])-1]+=(r[9] or 0)/1e6
O={'asof':asof,'es':{}}
for d,nm in D.items():
    gs=collections.OrderedDict()
    for r in est:
        if r[0]!=d: continue
        g=gs.setdefault(r[2],{'a':r[2],'n':AK.get(r[2],r[2]),'p':[]})
        t=sorted(tx.get(r[3],[]),key=lambda x:x[0])
        g['p'].append({'c':r[3],'k':str(r[4]).strip(),'pl':round((r[5] or 0)/1e6,4),'tp':round((r[6] or 0)/1e6,4),'t':t})
    for g in gs.values(): g['p'].sort(key=lambda p:-p['pl'])
    O['es'][d]={'n':nm,'g':list(gs.values()),'bm':[round(x,3) for x in bm[d]],'tm':[round(x,3) for x in tm[d]]}
    pl=sum(p['pl'] for g in gs.values() for p in g['p']);tp=sum(p['tp'] for g in gs.values() for p in g['p'])
    print(d,nm,'pos',sum(len(g['p']) for g in gs.values()),'plafond',round(pl,1),'terpakai',round(tp,1),'bm',round(sum(bm[d]),1),'tm',round(sum(tm[d]),1))
json.dump(O,open(out,'w'),separators=(',',':'),ensure_ascii=False)
