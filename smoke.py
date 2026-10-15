#!/usr/bin/env python3
"""Smoke test: python3 smoke.py PAGE.html OUTDIR  -> console errors, horizontal overflow, KPI text, screenshots."""
import sys, os, pathlib
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
full = os.path.join(out, 'full.html')
open(full, 'w', encoding='utf-8').write("<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'></head><body>" + open(src, encoding='utf-8').read() + "</body></html>")
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, n in ((1200, 'desktop'), (400, 'mobile')):
        pg = b.new_page(viewport={'width': w, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
        pg.goto(pathlib.Path(full).resolve().as_uri()); pg.wait_for_timeout(500)
        print(n, 'errors:', errs, 'scrollWidth', pg.evaluate("document.documentElement.scrollWidth"), 'of', w)
        pg.screenshot(path=os.path.join(out, n + '.png'), full_page=True)
        if n == 'desktop':
            print(pg.evaluate("document.querySelector('.kpis').innerText"))
            for per in range(3):
                pg.evaluate(f"document.querySelectorAll('#sPer button')[{per}].click()")
                pg.wait_for_timeout(100)
            print('after period toggles errors:', errs)
    b.close()
