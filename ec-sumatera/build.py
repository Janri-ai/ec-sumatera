#!/usr/bin/env python3
"""Build the EC Region Sumatera page from Snowflake result files.

usage: python3 build.py YEAR END_MONTH WORKDIR OUT.html [template.html]

WORKDIR must contain r_main.json r_tm.json r_mon.json r_pup.json r_lang.json (the "data" array of each
query produced by gen_sql.py). Needs END_MONTH >= 2 (the comparator period A = Jan..END_MONTH-1).

ALL cost, budget, ton and TM-hectare figures come from PRD_DB_PRESENTATION.PRS_COST.ESTATE_COST (owner's instruction). Only harvested
area, HK, BBC, TM ton (yield TM), fertilizer kg and palm counts come from the integration layer (not cost data).
The old budget-file / residual logic (parse_budget.py, q_budba, bud_afd.json) is retired.

Business rules applied here (do not change without the owner's OK):
  * PMY = BA 2131 afd A + afd C merged into one afdeling named "PMY"; afd B is excluded entirely.
  * Pupuk names are normalised; rows with 0 target and 0 actual are dropped.
  * September-style incompleteness is auto-detected: if depreciation of the last month is 0 in a BA,
    the page shows a warning banner and a dashed last trend segment.
"""
import json, sys, os, datetime

year, n = int(sys.argv[1]), int(sys.argv[2])
wd, out = sys.argv[3], sys.argv[4]
here = os.path.dirname(os.path.abspath(__file__))
tpl = open(sys.argv[5] if len(sys.argv) > 5 else os.path.join(here, 'template.html'), encoding='utf-8').read()
L = lambda f: json.load(open(os.path.join(wd, f)))
main, tm, mon, pup, lang = L('r_main.json'), L('r_tm.json'), L('r_mon.json'), L('r_pup.json'), L('r_lang.json')
pok = L('r_pok.json')
assert n >= 2, 'END_MONTH must be >= 2'

MS = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
ML = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
BAS = ['2121', '2124', '2131']
f = lambda x: 0.0 if x is None else float(x)


# ---- R rows: [ba,afd,per, ton,bbc,hap,hk,tonB,hkB,ha,haB, act[7], bud[7]] -------------------------------
def merge_rows(rows):
    o = list(rows[0][:3]) + [0.0] * 22
    for r in rows:
        for i in range(3, 25):
            o[i] += f(r[i])
    o[1] = 'PMY'
    return [round(x, 1) if isinstance(x, float) else x for x in o]

# ---- BBC bulan laporan (periode M) dari file tarikan BBC SAP (bbc_file.py), bila ada dan bulannya sama -----------------------
bbf_p = os.path.join(sys.argv[3], 'r_bbcfile.json')
bbf = json.load(open(bbf_p)) if os.path.exists(bbf_p) else None
if bbf and bbf.get('month') == n:
    # Periode M dan A dari file SAP (bulan-bulan yang ada di file). Jan..(bulan pertama file - 1) tidak ada di file:
    # dipakai kumulatif Snowflake YTD_TON_BBC (r_bbc.json), dikalibrasi per BA ke YTD resmi owner bila ada (r_bbc_owner.json {ba: YTD}).
    fm = sorted({int(m) for v in bbf['data'].values() for m in v})
    first = fm[0]
    cum = json.load(open(os.path.join(wd, 'r_bbc.json'))) if os.path.exists(os.path.join(wd, 'r_bbc.json')) else {}
    own_p = os.path.join(wd, 'r_bbc_owner.json')
    own = json.load(open(own_p)) if os.path.exists(own_p) else {}
    keys = {r[0] + r[1] for r in main if r[2] == 'M' and r[0] in BAS}
    base = {k: f(cum.get(k, {}).get(str(first - 1), 0.0)) for k in keys}
    fsum = {k: sum(v for m, v in bbf['data'].get(k, {}).items() if int(m) <= n) for k in keys}
    cal = {}
    for ba in BAS:
        ks = [k for k in keys if k.startswith(ba) and not (ba == '2131' and k.endswith('B'))]
        if ba in own and sum(base[k] for k in ks) > 0:
            cal[ba] = (own[ba] - sum(fsum[k] for k in ks)) / sum(base[k] for k in ks)
        else:
            cal[ba] = 1.0
    for r in main:
        if r[0] not in BAS or r[2] not in 'MAY':
            continue
        k = r[0] + r[1]
        fd = bbf['data'].get(k, {})
        bs = base.get(k, 0.0) * cal[r[0]]
        pm = f(fd.get(str(n), 0.0))
        pa = bs + sum(v for m, v in fd.items() if int(m) <= n - 1)
        r[4] = pm if r[2] == 'M' else (pa if r[2] == 'A' else pa + pm)
    print('BBC M dari file:', {ba: round(sum(f(bbf['data'].get(k, {}).get(str(n), 0)) for k in keys if k.startswith(ba) and not (ba == '2131' and k.endswith('B')))) for ba in BAS})
    print('BBC Y (Jan..n):', {ba: round(sum(r[4] for r in main if r[0] == ba and r[2] == 'Y' and not (ba == '2131' and r[1] == 'B'))) for ba in BAS}, 'kalibrasi', {k: round(v, 3) for k, v in cal.items()})
elif bbf:
    print('PERINGATAN: file BBC bulan', bbf.get('month'), '!= bulan laporan', n, '- diabaikan')

R = []
pmy = {}
for r in main:
    ba, afd, p = r[0], r[1], r[2]
    if ba == '2131':
        if afd == 'B':
            continue                      # afd B excluded entirely
        if afd in ('A', 'C'):
            pmy.setdefault(p, []).append(r)
            continue
    if not any(f(x) for x in r[3:]):
        continue                          # afd without any data (e.g. empty/unplanted)
    R.append([ba, afd, p] + [f(x) for x in r[3:]])
for p, rows in pmy.items():
    R.append(merge_rows(rows))
R.sort(key=lambda r: (r[0], r[1] == 'PMY', r[1], 'AMY'.index(r[2]) if r[2] in 'AMY' else 9))

# budget produksi (ton) per afdeling dari file perencanaan produksi per blok (menggantikan tonB ESTATE_COST)
bb_f = os.path.join(sys.argv[3], 'r_bgtblok.json')
if os.path.exists(bb_f):
    MS12 = ['dJAN', 'dFEB', 'dMAR', 'dAPR', 'dMEI', 'dJUN', 'dJUL', 'dAGS', 'dSEP', 'dOKT', 'dNOV', 'dDES']
    bb = {}
    for r in json.load(open(bb_f)):
        k = (r['ba'], 'PMY' if r['ba'] == '2131' else r['afd'])
        v = bb.setdefault(k, [0.0] * 12)
        for i, m in enumerate(MS12): v[i] += r[m]
    for r in R:
        v = bb.get((r[0], r[1]))
        if v is None: continue
        new_b = sum(v[:n]) if r[2] == 'Y' else v[n - 1] if r[2] == 'M' else sum(v[:n - 1])
        print('tonB', r[0], r[1], r[2], round(r[7], 1), '->', round(new_b, 1)) if abs(r[7] - new_b) > 1 else None
        r[7] = round(new_b, 1)

# ---- TMD / ADJ ----------------------------------------------------------------------------------------
# TMD = [ha TM (ESTATE_COST HA_ACTUAL), ha panen, ton from TM blocks]; ADJ = [budget up, inf, fert (ESTATE_COST), ha budget, 5 x share=1].
# Cost has no TM/TBM split in ESTATE_COST, so all cost is used as-is (shares fixed at 1).
tmx = {}
for r in tm:
    ba, afd, p = r[0], r[1], r[2]
    if ba == '2131':
        if afd == 'B':
            continue
        afd = 'PMY'
    x = tmx.setdefault((ba, afd, p), [0.0, 0.0])
    x[0] += f(r[3]); x[1] += f(r[4])
TMD, ADJ = {}, {}
# Budget Ha TM per afdeling from the RKT 2026 Hectare Statement files (hs_budget.py -> r_hsbgt.json; {ba+afd: [TM sms1, TM sms2]}).
hsb_f = os.path.join(wd, 'r_hsbgt.json')
hsb = json.load(open(hsb_f)) if os.path.exists(hsb_f) else {}
def bgt_ha(ba, afd, em):
    si = 0 if em <= 6 else 1
    if afd == 'PMY':
        return sum(hsb.get(ba + a, [0, 0])[si] for a in ('A', 'C'))
    return hsb.get(ba + afd, [0, 0])[si]
# Ha TM = Hectare Statement (INT_HEKTAR_BLOK) TM-planted hectares at the last month of the period (Y, M: n; A: n-1); PMY = afd A + C.
hstm_f = os.path.join(wd, 'r_hstm.json')
hstm = {}
if os.path.exists(hstm_f):
    for ba, afd, m, ha in json.load(open(hstm_f)):
        if ba == '2131':
            if afd == 'B':
                continue
            afd = 'PMY'
        hstm[(ba, afd, int(m))] = hstm.get((ba, afd, int(m)), 0.0) + float(ha)
for r in R:
    k = r[0] + r[1] + r[2]
    hp, tt = tmx.get((r[0], r[1], r[2]), [0.0, 0.0])
    hm = hstm.get((r[0], r[1], n - 1 if r[2] == 'A' else n)) if hstm else None
    TMD[k] = [round(hm if hm is not None else (r[9] if not hstm else 0.0), 1), round(hp, 1), round(tt, 1)]
    ADJ[k] = [round(r[18]), round(r[19]), round(r[20]), round(bgt_ha(r[0], r[1], n - 1 if r[2] == 'A' else n) if hsb else r[10], 1), 1, 1, 1, 1, 1]

# ---- MON ---------------------------------------------------------------------------------------------
MON = {b: [] for b in BAS}
for r in sorted(mon, key=lambda r: (r[0], r[1])):
    MON[r[0]].append([f(r[2]), f(r[3]), f(r[4]), f(r[5])])
for b in BAS:
    assert len(MON[b]) == n, f'{b}: {len(MON[b])} months, expected {n}'

# ---- SUMMARY (tab Summary): per BA per bulan: ton aktual, BBC, target (budget file), cost 7 kategori aktual & budget ------------
SUMM = {}
sc_f = os.path.join(wd, 'r_sumcost.json')
if os.path.exists(sc_f):
    scr = json.load(open(sc_f))
    for b in BAS:
        rows = sorted([r for r in scr if r[0] == b], key=lambda r: r[1])
        assert len(rows) == n, f'sumcost {b}: {len(rows)} months'
        ton = [f(m[2]) for m in MON[b]]
        tgt = [0.0] * n
        if 'bb' in globals():
            tg = [0.0] * 12
            for (kb, ka), v in bb.items():
                if kb == b:
                    for i in range(12): tg[i] += v[i]
            tgt = [round(x, 1) for x in tg[:n]]
        bbcm = [0.0] * n
        if bbf and bbf.get('month') == n:
            ks = [k for k in keys if k.startswith(b) and not (b == '2131' and k.endswith('B'))]
            for m in range(1, n + 1):
                if m < first:
                    bbcm[m - 1] = sum(f(cum.get(k, {}).get(str(m), 0)) - f(cum.get(k, {}).get(str(m - 1), 0)) for k in ks) * cal[b]
                else:
                    bbcm[m - 1] = sum(f(bbf['data'].get(k, {}).get(str(m), 0)) for k in ks)
        else:
            bbcm = [f(m[3]) for m in MON[b]]
        afds = sorted({r[1] for r in R if r[0] == b and r[2] == 'Y'})
        ha_m = [round(sum(hstm.get((b, a_, m), 0.0) for a_ in afds), 1) for m in range(1, n + 1)]
        hab_m = [round(sum(bgt_ha(b, a_, m) for a_ in afds), 1) if hsb else 0.0 for m in range(1, n + 1)]
        SUMM[b] = {'ha': ha_m, 'hab': hab_m, 'ton': ton, 'bbc': [round(x, 1) for x in bbcm], 'tgt': tgt,
                   'act': [[f(r[2 + i]) for r in rows] for i in range(7)], 'bud': [[f(r[9 + i]) for r in rows] for i in range(7)],
                   'ampb': (json.load(open(os.path.join(wd, 'r_ampb.json'))).get(b, [0.0] * n) if os.path.exists(os.path.join(wd, 'r_ampb.json')) else [0.0] * n),
                   'amp': (json.load(open(os.path.join(wd, 'r_amp.json'))).get(b, [0.0] * n) if os.path.exists(os.path.join(wd, 'r_amp.json')) else [0.0] * n)}
        yb = [r for r in R if r[0] == b and r[2] == 'Y' and not (b == '2131' and False)]
        print('SUMM', b, 'ton', round(sum(ton), 1), 'vs R', round(sum(r[3] for r in yb), 1), '| bbc', round(sum(bbcm), 1), 'vs R', round(sum(r[4] for r in yb), 1), '| tgt', round(sum(tgt), 1), 'vs R', round(sum(r[7] for r in yb), 1))

# ---- CORRELATION CHART (tab Summary): per BA/afd/bulan cost 5 komponen (tanpa Infra & Penyusutan), ton, Ha TM + anchor USTP/TAPG dari pbix ---------
CORR = {}
cr_f, an_f = os.path.join(wd, 'r_corr.json'), os.path.join(wd, 'r_anchor.json')
if os.path.exists(cr_f) and os.path.exists(an_f):
    cr = json.load(open(cr_f))
    hstm_raw = {(x[0], x[1], int(x[2])): float(x[3]) for x in json.load(open(hstm_f))}   # Ha TM per afd asli (PMY afd A dan C terpisah)
    tmf = json.load(open(os.path.join(wd, 'r_corrtm.json')))   # ton blok TM per bulan (yield TM = ton TM / Ha TM)
    CORR = {'anc': json.load(open(an_f)), 'bas': {}}
    for k, v in cr.items():
        b, a_ = k[:4], k[4:]
        assert len(v['c5']) >= n and len(v['ton']) >= n, f'corr {k}: months'
        CORR['bas'].setdefault(b, {})[a_] = {'c5': v['c5'][:n], 'ton': v['ton'][:n], 'tm': (tmf.get(k) or [0.0] * n)[:n], 'ha': [round(hstm_raw.get((b, a_, m), 0.0), 2) for m in range(1, n + 1)]}
    for b in BAS:
        if b in SUMM and b in CORR['bas']:
            tc = sum(sum(x['ton']) for x in CORR['bas'][b].values()); ts = sum(SUMM[b]['ton'])
            cc = sum(sum(x['c5']) for x in CORR['bas'][b].values()); cs = sum(sum(SUMM[b]['act'][i]) for i in (0, 2, 3, 4, 5))
            print('CORR', b, 'ton', round(tc, 1), 'vs SUMM', round(ts, 1), '| c5', round(cc), 'vs SUMM', round(cs))

# ---- TREND (tab Laporan produksi): ton per afd per bulan; Jan..n aktual, n+1..12 BBC sensus (proyeksi 4 bulan file SAP), Target 12 bulan ---------
TREND = {}
ol_f = os.path.join(wd, 'r_bbcout.json')
if os.path.exists(os.path.join(wd, 'r_corr.json')) and 'bb' in globals():
    cr_ = json.load(open(os.path.join(wd, 'r_corr.json')))
    olj = json.load(open(ol_f)) if os.path.exists(ol_f) else None
    if olj and olj.get('month') != n:
        print('PERINGATAN: r_bbcout bulan', olj.get('month'), '!=', n, '- outlook diabaikan'); olj = None
    for k, v in cr_.items():
        b, a_ = k[:4], k[4:]
        if b not in BAS: continue
        ak = 'PMY' if b == '2131' else a_
        d = TREND.setdefault(b, {}).setdefault(ak, {'act': [0.0] * n, 'bbc': [0.0] * (12 - n), 'tgt': [0.0] * 12})
        for i in range(n): d['act'][i] += f(v['ton'][i])
        if olj:
            for m_ in range(n + 1, 13): d['bbc'][m_ - n - 1] += f(olj['data'].get(k, {}).get(str(m_), 0))
    for (kb, ka), v in bb.items():
        if kb in TREND and ka in TREND[kb]: TREND[kb][ka]['tgt'] = [round(x, 1) for x in v]
    for b in TREND:
        for ak_, a_ in TREND[b].items():
            a_['ha'] = [round(hstm.get((b, ak_, m_), 0.0), 1) for m_ in range(1, n + 1)]
            a_['hab'] = [round(bgt_ha(b, ak_, m_), 1) for m_ in range(1, 13)] if hsb else [0.0] * 12
            a_['ybbc'] = round(sum(f(r[4]) for r in R if r[0] == b and r[2] == 'Y' and ((r[1] != 'B') if b == '2131' else (r[1] == ak_))), 1)
        for a_ in TREND[b].values():
            a_['act'] = [round(x, 1) for x in a_['act']]; a_['bbc'] = [round(x, 1) for x in a_['bbc']]
        print('TREND', b, 'ybbc', round(sum(x['ybbc'] for x in TREND[b].values()), 1), 'act', round(sum(sum(x['act']) for x in TREND[b].values()), 1), 'vs MON', round(sum(m[0] if False else m[2] for m in MON[b]), 1), '| bbc Q4', round(sum(sum(x['bbc']) for x in TREND[b].values())), '| tgt FY', round(sum(sum(x['tgt']) for x in TREND[b].values())))

# ---- PUP ---------------------------------------------------------------------------------------------
NAMES = {'BORATE': 'Borate', 'CUSO4': 'CuSO4', 'DOLOMITE': 'Dolomite', 'KIESERITE': 'Kieserite', 'MOP': 'MOP',
         'RP': 'RP', 'SRF': 'SRF', 'UREA': 'Urea'}
def pname(s):
    s = s.upper().replace('PUPUK ', '', 1).strip()
    s = s.replace(' + ', '+').replace(' +', '+').replace('+ ', '+')
    return NAMES.get(s, s if s.startswith('NPK') else s.title())
PUPA = {}                                           # ba|afd -> [[jenis, target kg YTD, actual kg YTD, target kg full year]] on TM blocks only
PUPX = {}                                           # ba -> [target kg, actual kg] on non-TM (TBM / blank maturity), excluded
for ba, afd, j, t, a, tx, ax, fy in pup:
    if j is None or j.startswith('#'):
        continue
    if ba == '2131' and afd == 'B':
        continue                                    # afd B excluded entirely
    x = PUPX.setdefault(ba, [0.0, 0.0])
    x[0] += f(tx)
    x[1] += f(ax)
    if f(t) == 0 and f(a) == 0 and f(fy) == 0:
        continue
    if ba == '2131':
        afd = 'PMY'                                 # A + C
    afd = afd or '(tanpa afd)'                      # rows without an afdeling code
    d = PUPA.setdefault(ba + '|' + afd, {})
    x = d.setdefault(pname(j), [0.0, 0.0, 0.0])
    x[0] += f(t)
    x[1] += f(a)
    x[2] += f(fy)
PUPA = {k: sorted(([n, v[0], v[1], v[2]] for n, v in d.items()), key=lambda x: x[0].lower()) for k, d in PUPA.items()}
PUP = {b: {} for b in BAS}                          # BA total = sum of afd (TM)
for k, lst in PUPA.items():
    for nm, t, a, fy in lst:
        x = PUP[k.split('|')[0]].setdefault(nm, [0.0, 0.0, 0.0])
        x[0] += t
        x[1] += a
        x[2] += fy
POK = {}                                            # ba|afd -> [avg TM ha YTD, palms YTD, ha full year, palms full year]; PMY = A + C, afd B dropped
for ba, afd, ha, pk_, hafy, pkfy in pok:
    if ba == '2131' and afd == 'B': continue
    key = ba + '|' + ('PMY' if ba == '2131' else afd)
    x = POK.setdefault(key, [0.0, 0.0, 0.0, 0.0]); x[0] += f(ha); x[1] += f(pk_); x[2] += f(hafy); x[3] += f(pkfy)
PUP = {b: sorted(([n, v[0], v[1], v[2]] for n, v in d.items()), key=lambda x: x[0].lower()) for b, d in PUP.items()}

LANG = {r[0]: [f(r[1]), f(r[2])] for r in lang}
for b in BAS:
    LANG.setdefault(b, [0, 0])

# ---- checks ------------------------------------------------------------------------------------------
warn = []
for b in BAS:
    ay = [r for r in R if r[0] == b and r[2] == 'Y']
    cost = sum(sum(r[11:18]) for r in ay)
    mc = sum(m[0] for m in MON[b])
    ton = sum(r[3] for r in ay)
    mt = sum(m[2] for m in MON[b])
    print(f'{b}: cost afd-sum {cost:,.0f} vs monthly {mc:,.0f} (diff {cost - mc:,.0f}); ton {ton:,.1f} vs {mt:,.1f}')
    if abs(cost - mc) > 0.002 * mc + 5 or abs(ton - mt) > 0.5:
        warn.append(f'{b}: tie-out difference between afd-sum and monthly series')
if warn:
    print('WARNING:', warn)

# ---- incompleteness of the last month ---------------------------------------------------------------
dep0 = [b for b in BAS if sum(r[17] for r in R if r[0] == b and r[2] == 'M') == 0]
ovh0 = []
for r in R:
    if r[2] != 'M' or r[9] <= 0:
        continue
    prev = [q for q in R if q[0] == r[0] and q[1] == r[1] and q[2] == 'A']
    avg = prev[0][16] / (n - 1) if prev else 0
    if avg > 500 and r[16] < 0.05 * avg:          # OVH of last month < 5% of the usual monthly level
        ovh0.append(f'{r[0]} {r[1]}')
incomplete = bool(dep0)
mlong, mshort = ML[n - 1], MS[n - 1]
BN = {'2121': 'SEK', '2124': 'SBR', '2131': 'PMY'}
if incomplete:
    txt = f'<b>Biaya {mlong} belum lengkap.</b> Penyusutan {mlong} belum terposting di {", ".join(BN[b] for b in dep0)} (Rp 0)'
    if ovh0:
        txt += f', dan biaya umum (OVH) {mlong} di {", ".join(sorted(set(o.split()[0] for o in ovh0)))} untuk beberapa afdeling nyaris nol'
    txt += (f'. Akibatnya EC Rp/Kg MTD {mshort} dan YTD Jan–{mshort} terlihat terlalu hemat. Produksi dan HK lengkap sampai akhir bulan. '
            f'Untuk perbandingan yang adil, pakai “YTD Jan–{MS[n - 2]} (lengkap)” sampai biaya {mlong} ditutup.')
    banner = f'<div class="warnbox" id="inc">{txt}</div>'
else:
    banner = ''

# ---- data.js + token fill ----------------------------------------------------------------------------
dj = lambda o: json.dumps(o, ensure_ascii=False)
data = ('// kolom R: ba,afd,periode(Y=Jan-' + mshort + ',M=' + mshort + ',A=Jan-' + MS[n - 2] + '), ton,bbc,hapanen,hk,tonB,hkB,ha,haB, act[up,inf,fert,harv,trans,ovh,depr], bud[7] (Rp ribu)\n'
        'const R=[\n' + ',\n'.join(dj(r) for r in R) + '];\n'
        f'const PUPE={dj(json.load(open(os.path.join(wd, "r_pupelem.json"))) if os.path.exists(os.path.join(wd, "r_pupelem.json")) else {})};\n'
        f'const MON={dj(MON)};\nconst PUP={dj(PUP)};\nconst PUPA={dj(PUPA)};\nconst PUPX={dj(PUPX)};\nconst POK={dj(POK)};\nconst LANG={dj(LANG)};\n'
        '// per BA+afd+periode: [ha TM, ha panen (HEKTAR_PANEN rata-rata bulanan), ton dari blok TM]\n'
        f'const TMD={dj(TMD)};\n'
        '// per BA+afd+periode: [budget upkeep TM, budget infra TM, budget pupuk TM, ha budget TM, share TM biaya aktual: upkeep, infra, pupuk, panen, transport]\n'
        f'const ADJ={dj(ADJ)};\n')
pulled = datetime.date.today().isoformat()
rep = {'{{TITLE_PERIOD}}': f'Januari – {mlong} {year}', '{{MTD_LONG}}': f'{mlong} {year}',
       '{{PREV}}': f'Jan–{MS[n - 2]}', '{{YTD}}': f'Jan–{mshort}', '{{MTD}}': mshort, '{{YEAR}}': str(year),
       '{{PULLED}}': pulled, '{{MN_JSON}}': dj(MS[:n]), '{{INCOMPLETE_JS}}': 'true' if incomplete else 'false',
       '{{INCOMPLETE_BANNER}}': banner}
assert '/*__DATA__*/' in tpl
pan_f = os.path.join(sys.argv[3], 'r_pan.json')
pan = json.load(open(pan_f)) if os.path.exists(pan_f) else {}
if isinstance(pan, list):  # raw Snowflake result: [["2121A|01,...;02,..."], ...] -> {"2121A": [[1.0,...], ...]}
    pan = {s[0].split('|')[0]: [[float(x) for x in r.split(',')] for r in s[0].split('|')[1].split(';')] for s in pan}
else:
    pass
for k in pan:
    pan[k] = [r for r in pan[k] if r[0] <= n]
hs_f = os.path.join(sys.argv[3], 'r_hs.json')
hs_raw = json.load(open(hs_f)) if os.path.exists(hs_f) else []
hs = {}
for r in hs_raw:                                   # [ba,afd,thn,ms,kt,ha,pokok,nblok,bibit]; PMY = afd A + C merged, afd B dropped
    ba, afd = r[0], r[1]
    if ba == '2131':
        if afd == 'B':
            continue
        afd = 'PMY'
    k = (ba, afd, r[2], r[3], r[4], r[8].replace('_', ' ') if len(r) > 8 else '-')   # + progeni (BIBIT)
    v = hs.setdefault(k, [0.0, 0.0, 0])
    v[0] += float(r[5]); v[1] += float(r[6]); v[2] += int(float(r[7]))
HS = [[k[0], k[1], k[2], k[3], k[4], round(v[0], 2), round(v[1]), v[2], k[5]] for k, v in sorted(hs.items())]
ptt_f = os.path.join(sys.argv[3], 'r_ptt_pg.json' if os.path.exists(os.path.join(sys.argv[3], 'r_ptt_pg.json')) else 'r_ptt.json')   # _pg = dengan progeni dominan per blok (kolom ke-9)
ptt_raw = json.load(open(ptt_f)) if os.path.exists(ptt_f) else []
pt = {}
for r in ptt_raw:                                  # [ba,afd,thn,ms,ton_a,ton_m,hp_a,hp_m]; PMY = afd A + C merged
    ba, afd = r[0], r[1]
    if ba == '2131':
        if afd == 'B':
            continue
        afd = 'PMY'
    k = (ba, afd, r[2], r[3], str(r[8]).replace('_', ' ') if len(r) > 8 else '-')
    v = pt.setdefault(k, [0.0] * 4)
    for i in range(4):
        v[i] += float(r[4 + i])
PTT = [[k[0], k[1], k[2], k[3]] + [round(x, 2) for x in v] + [k[4]] for k, v in sorted(pt.items())]
hs0_f = os.path.join(sys.argv[3], 'r_hs0.json')
hs0_raw = json.load(open(hs0_f)) if os.path.exists(hs0_f) else []
def hs_rows(raw):
    d = {}
    for r in raw:
        ba, afd = r[0], r[1]
        if ba == '2131':
            if afd == 'B':
                continue
            afd = 'PMY'
        v = d.setdefault((ba, afd, r[2], r[3], r[4]), [0.0, 0.0, 0])
        v[0] += float(r[5]); v[1] += float(r[6]); v[2] += int(float(r[7]))
    return [[k[0], k[1], k[2], k[3], k[4], round(v[0], 2), round(v[1]), v[2]] for k, v in sorted(d.items())]
HS0 = hs_rows(hs0_raw)
ha_f = os.path.join(sys.argv[3], 'r_hsavg_pg.json' if os.path.exists(os.path.join(sys.argv[3], 'r_hsavg_pg.json')) else 'r_hsavg.json')
ha_raw = json.load(open(ha_f)) if os.path.exists(ha_f) else []
hd = {}
for r in ha_raw:                                   # [ba,afd,thn,kind,ha_a,ha_m]; PMY = afd A + C, afd B dropped
    ba, afd = r[0], r[1]
    if ba == '2131':
        if afd == 'B':
            continue
        afd = 'PMY'
    v = hd.setdefault((ba, afd, r[2], r[3], str(r[6]).replace('_', ' ') if len(r) > 6 else '-'), [0.0, 0.0])
    v[0] += float(r[4]); v[1] += float(r[5])
HSA = [[k[0], k[1], k[2], k[3], round(v[0], 2), round(v[1], 2), k[4]] for k, v in sorted(hd.items())]
# bobot alokasi budget/BBC per afd x tahun tanam (tgt = INT_PANEN_HARIAN_TARGET, BBC = Snowflake Jan-Jun + file SAP Jul-Sep)
al_f = os.path.join(sys.argv[3], 'r_alloc.json'); af_f = os.path.join(sys.argv[3], 'r_allocfile.json')
ALC = {}
# tgt = BUDGET TON per blok (file perencanaan produksi, DISTRIBUSI_* Jan..Des) dijumlah per afd x tahun tanam; '?' = blok tak terdaftar di HS
for ba, afd, thn, ta, tm_ in json.load(open(os.path.join(sys.argv[3], 'r_bgtthn.json'))):
    o = ALC.setdefault((ba, afd, thn), [0.0] * 7); o[0] += ta; o[1] += tm_
for ba, afd, thn, kind, ta, tm_, h1, m7, m8, m9 in json.load(open(al_f)):
    if thn == '?': continue
    o = ALC.setdefault((ba, afd, thn), [0.0] * 7); o[2] += h1
for k, v in json.load(open(af_f)).items():
    ba, afd, thn = k.split('|')
    if thn == '?' or (ba, afd, thn) not in ALC: continue
    o = ALC[(ba, afd, thn)]; o[3] += v.get('7', 0); o[4] += v.get('8', 0); o[5] += v.get('9', 0)
ALCJ = [[k[0], k[1], k[2]] + [round(x, 2) for x in v[:6]] for k, v in sorted(ALC.items())]
# profile & potensi setahun (ton) per afd x tahun tanam dari file perencanaan produksi per blok; PMY = afd A + C digabung
PPD = {}
pp_f = os.path.join(sys.argv[3], 'r_pp.json')
for ba, afd, thn, pr, po, hp_, hq_ in (json.load(open(pp_f)) if os.path.exists(pp_f) else []):
    k = (ba, 'PMY' if ba == '2131' else afd, thn)
    v = PPD.setdefault(k, [0.0] * 4)
    for i, x in enumerate((pr, po, hp_, hq_)): v[i] += x
PPJ = [[k[0], k[1], k[2]] + [round(x, 2) for x in v] for k, v in sorted(PPD.items())]   # [ba,afd,thn,profile ton, potensi ton, ha profile, ha potensi]
AKPJ = json.load(open(os.path.join(wd, 'r_akp.json'))) if os.path.exists(os.path.join(wd, 'r_akp.json')) else {}
RWJ = {'m': n, 'd': json.load(open(os.path.join(wd, 'r_rawat.json'))) if os.path.exists(os.path.join(wd, 'r_rawat.json')) else {}, 'o': json.load(open(os.path.join(wd, 'r_rawout.json'))) if os.path.exists(os.path.join(wd, 'r_rawout.json')) else {}, 'n': json.load(open(os.path.join(wd, 'r_rawnorm.json'))) if os.path.exists(os.path.join(wd, 'r_rawnorm.json')) else {}}
html = tpl.replace('__RW__', json.dumps(RWJ, separators=(',', ':'))).replace('__CE__', json.dumps(dict(json.load(open(os.path.join(wd, 'r_ce.json'))), m=n) if os.path.exists(os.path.join(wd, 'r_ce.json')) else {}, separators=(',', ':'), ensure_ascii=False)).replace('__HC__', open(os.path.join(wd, 'r_hc.json'), encoding='utf-8').read() if os.path.exists(os.path.join(wd, 'r_hc.json')) else '{"g":[],"src":""}').replace('__HN__', open(os.path.join(wd,'r_hcns.json'),encoding='utf-8').read() if os.path.exists(os.path.join(wd,'r_hcns.json')) else '{"src":"","det":{},"cls":{}}').replace('__OJ__', open(os.path.join(wd,'r_oj.json'),encoding='utf-8').read() if os.path.exists(os.path.join(wd,'r_oj.json')) else '{"src":"","rows":[]}').replace('__CX__', open(os.path.join(wd, 'r_capex.json'), encoding='utf-8').read() if os.path.exists(os.path.join(wd, 'r_capex.json')) else '{"es":{},"asof":""}').replace('__OH__', open(os.path.join(wd, 'r_opex.json'), encoding='utf-8').read() if os.path.exists(os.path.join(wd, 'r_opex.json')) else '{"rows":{},"ha":{},"asof":""}').replace('__GJ__', json.dumps({'m': n, 'd': json.load(open(os.path.join(wd, 'r_gaji.json'))) if os.path.exists(os.path.join(wd, 'r_gaji.json')) else {}}, separators=(',', ':'))).replace('__AKP__', json.dumps(AKPJ, separators=(',', ':'))).replace('__SUMM__', json.dumps(SUMM, separators=(',', ':'))).replace('__CORR__', json.dumps(CORR, separators=(',', ':'))).replace('__TREND__', json.dumps(TREND, separators=(',', ':'))).replace('__PP__', json.dumps(PPJ, separators=(',', ':'))).replace('__ALC__', json.dumps(ALCJ, separators=(',', ':'))).replace('__HSA__', json.dumps(HSA, separators=(',', ':'))).replace('__HS0__', json.dumps(HS0, separators=(',', ':'))).replace('__PTT__', json.dumps(PTT, separators=(',', ':'))).replace('__HS__', json.dumps(HS, separators=(',', ':'))).replace('/*__DATA__*/', data).replace('__PANEN__', json.dumps(pan, separators=(',', ':')))
for k, v in rep.items():
    html = html.replace(k, v)
assert '{{' not in html, 'unfilled token: ' + html[html.index('{{'):html.index('{{') + 30]
open(out, 'w', encoding='utf-8').write(html)
print('written', out, len(html), 'bytes; incomplete =', incomplete, dep0, ovh0)
