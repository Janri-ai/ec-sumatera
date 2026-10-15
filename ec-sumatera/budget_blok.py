#!/usr/bin/env python3
"""Budget produksi (ton) per blok dari folder 'BUDGET 2026 per AFD/PRODUKSI PER BLOK' (ekspor sistem perencanaan produksi).
python3 budget_blok.py FOLDER OUTDIR [BULAN_LAPORAN=9]
Baca *_data_perencanaan_produksi_*.xls (HTML; kolom 'BUDGET TON.1' = budget final, DISTRIBUSI JAN..DES = sebaran bulanan, jumlah = BUDGET TON.1)
Tahun tanam per blok dari *_template_upload_perencanaan_produksi_*.csv (kolom TAHUN TANAM); blok yang tidak ada di CSV diisi manual di FIX (dari Hectare Statement), sisanya '?'.
Output: OUTDIR/r_bgtblok.json (per blok) dan OUTDIR/r_bgtthn.json ([ba,afd,thn,ton Jan..n-1,ton bulan n]). PMY: BA 2122 -> 2131, hanya afd A dan C ada di file.
Tie-out terbukti: total per BA YTD Sep = ESTATE_COST (SEK 44.989,3; SBR 33.700,5; PMY 4.211,6); per afd SEK + SBR A/E persis; SBR B/C/D berbeda dari ESTATE_COST (afd B +38, C +699, D -737) -> pakai file."""
import sys, glob, os, csv, json, collections, warnings
import pandas as pd
warnings.filterwarnings('ignore')
D, OUT = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 9
M = ['JAN', 'FEB', 'MAR', 'APR', 'MEI', 'JUN', 'JUL', 'AGS', 'SEP', 'OKT', 'NOV', 'DES']
FIX = {('2124', 'A', '709'): '2023', ('2124', 'A', '710'): '2023', ('2124', 'A', '711'): '2023', ('2124', 'D', '704'): '2023'}
d = pd.concat([pd.read_html(f, header=0)[0] for f in sorted(glob.glob(os.path.join(D, '*_data_perencanaan_produksi_*.xls')))], ignore_index=True)
d['ba'] = d['BA CODE'].astype(str).replace({'2122': '2131'}); d['afd'] = d['AFD CODE'].astype(str)
d['blok'] = d['BLOCK - DESC'].astype(str).str.split(' - ').str[0].str.strip()
for m in M: d['d' + m] = pd.to_numeric(d['DISTRIBUSI ' + m], errors='coerce').fillna(0)
mp = {}
for f in glob.glob(os.path.join(D, '*_template_upload_perencanaan_produksi_*.csv')):
    for r in list(csv.reader(open(f, encoding='utf-8-sig')))[1:]: mp[(r[1].replace('2122', '2131'), r[2], r[3])] = r[7]
d['thn'] = [FIX.get((b, a, k), mp.get((b, a, k), '?')) or '?' for b, a, k in zip(d.ba, d.afd, d.blok)]
d['prof'] = pd.to_numeric(d['YIELD PROFILE TON'], errors='coerce').fillna(0); d['pot'] = pd.to_numeric(d['POTENSI TON'], errors='coerce').fillna(0)   # setahun (ton)
d['ha'] = (pd.to_numeric(d['PERIODE BUDGET SMS1 HA'], errors='coerce').fillna(0) + pd.to_numeric(d['PERIODE BUDGET SMS2 HA'], errors='coerce').fillna(0)) / 2   # ha budget (rata-rata semester)
d['hp'] = d.ha.where(d.prof > 0, 0); d['hq'] = d.ha.where(d.pot > 0, 0)   # ha hanya blok yang punya profile / potensi (pembagi yield)
d['ytd'] = d[['d' + m for m in M[:n]]].sum(axis=1); d['mon'] = d['d' + M[n - 1]]; d['prev'] = d.ytd - d.mon
d[['ba', 'afd', 'blok', 'thn', 'prev', 'mon', 'ytd', 'prof', 'pot'] + ['d' + m for m in M]].to_json(os.path.join(OUT, 'r_bgtblok.json'), orient='records')
g = d.groupby(['ba', 'afd', 'thn'])[['prev', 'mon']].sum().round(2).reset_index()
json.dump(g.values.tolist(), open(os.path.join(OUT, 'r_bgtthn.json'), 'w'))
gp = d.groupby(['ba', 'afd', 'thn'])[['prof', 'pot', 'hp', 'hq']].sum().round(2).reset_index()   # profile & potensi setahun per afd x tahun tanam
json.dump(gp.values.tolist(), open(os.path.join(OUT, 'r_pp.json'), 'w'))
print(d.groupby('ba')[['ytd', 'mon', 'prof', 'pot']].sum().round(1)); print(d.groupby(['ba', 'afd']).ytd.sum().round(1).to_string())
