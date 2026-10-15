import sys,os
from playwright.sync_api import sync_playwright
src,out=sys.argv[1],sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1100,'height':900},color_scheme='light')
    pg.goto('file://'+os.path.abspath(src)); pg.wait_for_timeout(500)
    pg.click('#sTab button[data-t="SM"]'); pg.wait_for_timeout(300)
    htmls=[]
    for i in (0,1):
        pg.locator('#coP button').nth(i).click(); pg.wait_for_timeout(200)
        htmls.append(pg.evaluate('''()=>{const s=document.querySelector("section:has(#coC1)").cloneNode(true);
          s.querySelectorAll(".bar,#coW[hidden],.tip").forEach(e=>{if(e.id!=="coW")e.remove()});s.querySelectorAll("[id]").forEach(e=>e.removeAttribute("id"));return s.outerHTML}'''))
    pg.evaluate('''(h)=>{const w=document.createElement("div");w.id="pdfroot";w.innerHTML=h.map((x,i)=>`<div class="pg" style="${i?"break-before:page":""}">${x}</div>`).join("");
      document.body.querySelectorAll(":scope > *:not(script):not(style)").forEach(e=>e.remove());document.body.appendChild(w)}''',htmls)
    pg.evaluate('''()=>document.querySelectorAll("#pdfroot .tw").forEach((t,i)=>{const h=document.createElement("h3");h.style.cssText="font-size:13px;margin:0 0 6px";h.textContent="Tabel Correlation chart: "+(i?"YTD Sep (anchor proyeksi Jan–Sep)":"YTD Jul (anchor asli Jan–Jul)");t.prepend(h)})''')
    pg.add_style_tag(content='@page{size:A4 landscape;margin:10mm}body{background:#fff!important}section{box-shadow:none!important;border:none!important;padding:0!important;margin:0!important}.chartbox svg{min-width:0!important;width:100%!important}table{font-size:10px}th,td{padding:3px 6px!important}.tw{overflow:visible!important}p.note{font-size:9.5px;max-width:none!important;margin:2px 0!important}.chartbox{padding:0!important}.chartbox svg{max-height:112mm!important;height:auto!important;display:block;margin:0 auto}.tw{break-before:page;padding-top:2mm}h2{font-size:16px}')
    pg.wait_for_timeout(300)
    pg.pdf(path=out,format='A4',landscape=True,print_background=True,margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'})
    b.close()
