#!/usr/bin/env python3
"""Simulasi YTD Des (Rp/Kg dan Rp/Ha TM). usage: python3 sd_load.py WORKDIR [bulan=9]
Input di WORKDIR: r_an.json (aktual/budget YTD per komponen, rupiah juta), r_corr.json (ton aktual per afd), r_bbcout.json (outlook BBC),
r_bgtblok.json (target produksi), r_hstm.json (Ha TM bulan laporan), r_hsbgt.json (Ha TM budget RKT), r_pup.json (pupuk TM kg),
sd_bud.json (query INT_COST_BUDGET SOURCE_BUDGET='ESTATE_COST': ba,k,ytd budget,budget bulan sisa n+1..Des (Okt-Des utk n=9, Nov-Des utk n=10); k=indeks komponen 0..6). Output r_sd.json."""
import json, os, sys
wd = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 9
L = lambda f: json.load(open(os.path.join(wd, f)))
amp, ampb = (L('r_amp.json') if os.path.exists(os.path.join(wd,'r_amp.json')) else {}), (L('r_ampb.json') if os.path.exists(os.path.join(wd,'r_ampb.json')) else {})
an, corr, bb, bg, hs, hb, pup, bud = L('r_an.json'), L('r_corr.json'), L('r_bbcout.json')['data'], L('r_bgtblok.json'), L('r_hstm.json'), L('r_hsbgt.json'), L('r_pup.json'), L('sd_bud.json')
keep = lambda ba, afd: not (ba == '2131' and afd == 'B')
M = ['dJAN','dFEB','dMAR','dAPR','dMEI','dJUN','dJUL','dAGS','dSEP','dOKT','dNOV','dDES']
out = {'m': n, 'ba': {}}
for ba in ['2121', '2124', '2131']:
    act = sum(sum(v['ton'][:n]) for k, v in corr.items() if k.startswith(ba) and keep(ba, k[4:]))
    q4 = sum(sum(x.values()) for k, x in bb.items() if k.startswith(ba) and keep(ba, k[4:]))
    tg = sum(sum(r[m] for m in M) for r in bg if r['ba'] == ba and keep(ba, r['afd']))
    tgy = sum(sum(r[m] for m in M[:n]) for r in bg if r['ba'] == ba and keep(ba, r['afd']))
    ha = sum(h[3] for h in hs if h[0] == ba and h[2] == n and keep(ba, h[1]))
    hab = sum(v[1] for k, v in hb.items() if k.startswith(ba) and keep(ba, k[4:]))
    q4b = [0.0] * 7; b9 = [0.0] * 7
    for r in bud:
        if r[0] == ba: b9[int(r[1])] = float(r[2]); q4b[int(r[1])] = float(r[3])
    pk = [r for r in pup if r[0] == ba and keep(ba, r[1])]
    a = an['ba'][ba]
    out['ba'][ba] = {'ton9': round(a['T'], 1), 'ton9ol': round(act, 1), 'q4ol': round(q4, 1), 'tgt': round(tg, 1), 'tgt9': round(tgy, 1),
        'a': a['a'], 'b9': [round(x, 1) for x in a['b']], 'bq4': q4b, 'ha': round(ha, 1), 'hab': round(hab, 1),
        'kg': [sum(r[4] for r in pk), sum(r[7] for r in pk)],
        # Sewa AMP (bagian dari Umum), Rp juta: aktual YTD, budget YTD, budget bulan sisa (n+1..Des) = (12-n) x budget bulanan (budget AMP datar per bulan)
        'amp9': round(sum(amp.get(ba, [])[:n]) / 1000, 1), 'ampb9': round(sum(ampb.get(ba, [])[:n]) / 1000, 1), 'ampq4': round((ampb.get(ba, [0])[n - 1] if ampb.get(ba) else 0) * (12 - n) / 1000, 1)}
    print(ba, out['ba'][ba]['ton9'], out['ba'][ba]['ton9ol'], 'budget ytd9 tie', [round(x - y, 1) for x, y in zip(b9, a['b'])])
json.dump(out, open(os.path.join(wd, 'r_sd.json'), 'w'), separators=(',', ':'))
