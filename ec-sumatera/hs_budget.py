#!/usr/bin/env python3
"""Budget Ha TM per afdeling dari file RKT 2026 "REKAP HECTARE STATEMENT" (folder EC PROJECT CONTOH/HS 2026).

usage: python3 hs_budget.py OUT.json FILE1 [FILE2 ...]
File: SEKERNAN_*.xls, PEMAYUNG_*.xls (html sederhana) dan untuk SBR: BRAHMA SAWIT_*_files/sheet001.htm
(file .xls SBR hanya frameset javascript). Tiap baris afd: LUAS TANAM SMS 1 (TBM0,1,2,3,TM,TOTAL) lalu SMS 2.
Output: {"2121A":[tm_sms1, tm_sms2], ...} (BA 2122 -> 2131; PMY digabung A+C di build.py).
"""
import re, html, sys, json

def rows(path):
    t = open(path, encoding='cp1252', errors='replace').read()
    for r in re.findall(r'<tr.*?</tr>', t, flags=re.S | re.I):
        c = [html.unescape(re.sub(r'<[^>]+>', '', x)).replace('\xa0', ' ').strip() for x in re.findall(r'<t[dh].*?</t[dh]>', r, flags=re.S | re.I)]
        c = [x for x in c if x != '']
        if c:
            yield c

num = lambda x: float(x.replace(',', ''))
out = {}
for p in sys.argv[2:]:
    ba = None
    for c in rows(p):
        if re.fullmatch(r'\d{4}', c[0]) and len(c) >= 16 and 'HA STATEMENT' in ' '.join(c[:4]).upper().replace('  ', ' ').replace('SEBARAN HA', 'SEBARAN HA'):
            ba, c = c[0], c[3:]
        elif re.fullmatch(r'\d{4}', c[0]) and len(c) >= 16:
            continue                      # baris HA PANEN / TBS PANEN
        if ba is None or not re.fullmatch(r'[A-Z]', c[0]) or len(c) < 13:
            continue
        try:
            v = [num(x) for x in c[1:13]]
        except ValueError:
            continue
        b = '2131' if ba == '2122' else ba
        out[b + c[0]] = [v[4], v[10]]      # TM sms1, TM sms2
json.dump(out, open(sys.argv[1], 'w'), indent=0)
for k, v in sorted(out.items()):
    print(k, v)
for ba in sorted({k[:4] for k in out}):
    print(ba, 'total TM sms1/sms2:', round(sum(v[0] for k, v in out.items() if k[:4] == ba), 2), round(sum(v[1] for k, v in out.items() if k[:4] == ba), 2))
