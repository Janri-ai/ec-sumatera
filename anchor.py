# Anchor garis USTP & TAPG untuk Correlation chart (tab Summary). Sumber: pbix "COST REVIEW & CAPEX 2026_new" (halaman Correlation chart Rp/Kg), data Jan-Jul 2026.
# TAPG = seluruh 28 BA di pbix (termasuk SEK/SBR/PMY). Rp/Kg = SUM(Rupiah[Rp Actual])/SUM(FFB[Kg Actual]); Yield = SUM(Kg)/rata2 Ha TM bulanan/1000.
# Rupiah di pbix hanya 5 grup (RAWAT, PUPUK, PANEN, TRANSPORT, UMUM) -> tanpa Infra & Penyusutan.
# Jalankan: python3 -I anchor.py /home/claude/pbix work/r_anchor.json
import sys, json, pandas as pd
d, out = sys.argv[1], sys.argv[2]
R = pd.read_pickle(d + '/R.pkl'); F = pd.read_pickle(d + '/F.pkl'); H = pd.read_pickle(d + '/H.pkl'); U = pd.read_pickle(d + '/U.pkl'); UF = pd.read_pickle(d + '/UF.pkl').dropna(subset=['Period'])
rp = pd.to_numeric(R['Rp Actual']).sum(); kg = pd.to_numeric(F['Kg Actual']).sum(); ha = H.groupby('Period')['Ha TM'].sum().mean()
urp = U['Rp Actual'].astype(float).sum(); ukg = UF['USTP Actual'].sum(); uha = UF['Ha Actual'].mean()
a = {'months': 7, 'tapg': {'rpkg': rp / kg, 'yield': kg / ha / 1000}, 'ustp': {'rpkg': urp / ukg, 'yield': ukg / uha / 1000}}
json.dump(a, open(out, 'w')); print(a)
