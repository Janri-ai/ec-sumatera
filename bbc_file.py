"""BBC per afdeling dari file 'Tarikan BBC Periode ... Detail Blok.xlsx' (sheet SAP, tarikan sensus BBC SAP).
python3 bbc_file.py FILE.xlsx REPORT_MONTH OUT.json
Isi file: satu baris per blok per bulan sensus (kolom MONTH = 1..3 = tiga bulan terakhir, REPORT_MONTH-2..REPORT_MONTH; MONTH 3 terbukti
cocok dengan BBC bulan laporan pemilik untuk SEK 4.997, SBR 3.817, PMY 373 pada September 2026).
BBC bulan itu = 'Tbs Bulan Ke-1' (ton) dari sensus bulan yang sama, dijumlah per afdeling. File tidak memuat Jan-Jun, jadi BBC YTD tidak bisa dihitung dari file ini.
Output: {"month": M, "data": {"2121A": {"7": ton, "8": ton, "9": ton}, ...}}  (PMY = BA 2131 afd A dan C)."""
import sys, json
import pandas as pd
f, m, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
BA = {'SEKERNAN ESTATE': '2121', 'SAWIT BRAHMA': '2124', 'PLASMA PEMAYUNG ESTATE': '2131'}
df = pd.read_excel(f, sheet_name='SAP', header=0)
df = df[df['Nama Kebun'].isin(BA)].copy()
df['ba'] = df['Nama Kebun'].map(BA)
df['k'] = df['ba'] + df['Afdeling'].astype(str).str.strip()
g = df.groupby(['k', 'MONTH'])['Tbs Bulan Ke-1'].sum().round(2)
data = {}
for (k, mo), v in g.items():
    data.setdefault(k, {})[str(m - 3 + int(mo))] = float(v)
json.dump({'month': m, 'data': data}, open(out, 'w'))
tot = {}
for k, d in data.items():
    tot[k[:4]] = tot.get(k[:4], 0) + d[str(m)]
print(json.dumps({'month': m, 'data': data}, separators=(',', ':')))
print({k: round(v) for k, v in tot.items()})

# Outlook: sensus bulan laporan (MONTH 3) memuat proyeksi 4 bulan: Ke-1 = bulan laporan, Ke-2..Ke-4 = bulan berikutnya.
# python3 bbc_file.py FILE.xlsx REPORT_MONTH OUT.json  -> juga menulis OUT_outlook.json {"2121A": {"10":..,"11":..,"12":..}}
mx = df[df['MONTH'] == df['MONTH'].max()]
ol = {}
for col, off in (('Tbs Bulan Ke-2', 1), ('Tbs Bulan Ke-3', 2), ('Tbs Bulan Ke-4', 3)):
    for k, v in mx.groupby('k')[col].sum().round(2).items():
        if m + off <= 12:
            ol.setdefault(k, {})[str(m + off)] = float(v)
json.dump({'month': m, 'data': ol}, open(out.replace('.json', '_outlook.json'), 'w'))
print('outlook', {ba: [round(sum(d.get(str(mm), 0) for k, d in ol.items() if k.startswith(ba) and not (ba == '2131' and k.endswith('B'))) ) for mm in (10, 11, 12)] for ba in ('2121', '2124', '2131')})
