#!/usr/bin/env python3
"""Parse 'BUDGET 2026 per AFD' (HTML disguised as .xls) into tidy afd x month x category budget (Rp).
usage: python3 parse_budget.py DIR OUT.json
Category map (GROUP02 -> report category):
 up   : HPT, PEMBERANTASAN LALANG, PENJARANGAN, PIRINGAN..., SELEKTIF WEEDING / SPOT SPRAY, SENSUS TANAMAN, SISIP TANAMAN,
        SUPERVISI PEMELIHARAAN, TRANSPORT RAWAT, TUNASAN / PRUNING / SLASHING
 inf  : PEMELIHARAAN PRASARANA DAN INFRASTRUKTUR
 fert : PEMUPUKAN, TRANSPORTASI PEMUPUKAN
 harv : ALAT PANEN, GAJI PANEN & PREMI, SUPERVISI (krani buah + supervisi pemanen), TRANSPORT AJK PANEN (as Snowflake: Harvesting - Transports)
 trans: LOADING (MUAT) TBS - INTERNAL, TRANSPOR TBS - EXTERNAL
 depr : BIAYA UMUM rows whose AKTIVITAS contains PENYUSUTAN or starts with 'Depr'
 ovh  : other BIAYA UMUM rows
"""
import pandas as pd, glob, json, sys, warnings
warnings.filterwarnings('ignore')
D, OUT = sys.argv[1], sys.argv[2]
MAP = {'HPT': 'up', 'PEMBERANTASAN LALANG': 'up', 'PENJARANGAN': 'up', 'PIRINGAN, PASAR PIKUL, TPH': 'up',
       'SELEKTIF WEEDING / SPOT SPRAY': 'up', 'SENSUS TANAMAN': 'up', 'SISIP TANAMAN': 'up', 'SUPERVISI PEMELIHARAAN': 'up',
       'TRANSPORT RAWAT': 'up', 'TUNASAN / PRUNING / SLASHING': 'up',
       'PEMELIHARAAN PRASARANA DAN INFRASTRUKTUR': 'inf', 'PEMUPUKAN': 'fert', 'TRANSPORTASI PEMUPUKAN': 'fert',
       'ALAT PANEN': 'harv', 'GAJI PANEN & PREMI': 'harv', 'SUPERVISI': 'harv', 'TRANSPORT AJK PANEN': 'harv',
       'LOADING (MUAT) TBS - INTERNAL': 'trans', 'TRANSPOR TBS - EXTERNAL': 'trans'}
cols = ['ba', 'baname', 'afd', 'g1', 'g2', 'kode', 'akt', 'ce', 'ket', 'y'] + [f'm{i}' for i in range(1, 13)] + ['sat', 'qy'] + [f'q{i}' for i in range(1, 13)]
rows = []
for f in sorted(glob.glob(D + '/*.xls')):
    t = pd.read_html(f, header=None)[0].iloc[2:].reset_index(drop=True)
    t.columns = cols
    for c in ['ba', 'afd', 'g1', 'g2', 'akt']:
        t[c] = t[c].ffill()
    for c in ['y'] + [f'm{i}' for i in range(1, 13)]:
        t[c] = pd.to_numeric(t[c], errors='coerce').fillna(0)
    sub = t[t.ba.isin(['SUB TOTAL', 'TOTAL'])]
    d = t[~t.ba.isin(['SUB TOTAL', 'TOTAL'])].copy()
    unk = set(d.g2) - set(MAP) - {'BIAYA UMUM'}
    assert not unk, f'unmapped GROUP02: {unk}'
    def cat(r):
        if r.g2 == 'BIAYA UMUM':
            a = str(r.akt).upper()
            return 'depr' if ('PENYUSUTAN' in a or a.startswith('DEPR')) else 'ovh'
        return MAP[r.g2]
    d['cat'] = d.apply(cat, axis=1)
    # tie-out with the file's own SUB TOTAL rows
    tot = d.groupby(['ba', 'afd']).y.sum()
    print(f.split('/')[-1], 'rows', len(d), 'sum', f'{d.y.sum():,.0f}', 'file TOTAL', f'{sub[sub.ba == "TOTAL"].y.sum():,.0f}')
    rows.append(d)
a = pd.concat(rows)
a['ba'] = a.ba.astype(str).str.replace(r'\.0$', '', regex=True).replace({'2122': '2131'})
g = a.groupby(['ba', 'afd', 'cat'])[[f'm{i}' for i in range(1, 13)]].sum()
res = {}
for (ba, afd, c), r in g.iterrows():
    res.setdefault(ba, {}).setdefault(afd, {})[c] = [round(float(x)) for x in r.values]   # Rp per month
json.dump(res, open(OUT, 'w'))
for ba in res:
    print(ba, {c: round(sum(sum(res[ba][afd].get(c, [0] * 12)) for afd in res[ba]) / 1000) for c in ['up', 'inf', 'fert', 'harv', 'trans', 'ovh', 'depr']})
