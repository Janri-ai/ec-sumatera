import sys,asyncio
from playwright.sync_api import sync_playwright
f=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,vp,scheme,per in [('d7',(1200,900),'light',0),('d9',(1200,900),'light',1),('dk',(1200,900),'dark',0),('mb',(400,800),'light',0)]:
        pg=b.new_page(viewport={'width':vp[0],'height':vp[1]},color_scheme=scheme); errs=[]
        pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None); pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.goto('file://'+__import__('os').path.abspath(f)); pg.wait_for_timeout(500)
        pg.click('#sTab button[data-t="SM"]'); pg.wait_for_timeout(300)
        pg.locator('#coP button').nth(per).click(); pg.wait_for_timeout(200)
        pg.locator('#coC1').scroll_into_view_if_needed()
        sec=pg.locator('section:has(#coC1)'); sec.screenshot(path=f'work/shots/corr_{name}.png')
        sw=pg.evaluate('document.documentElement.scrollWidth'); print(name,errs,sw)
        if name=='d7':
            pg.locator('#coC1 g.h').nth(2).hover(); pg.wait_for_timeout(200); print(pg.locator('#coC1 .tip, .tip').first.inner_text() if pg.locator('.tip').count() else 'no tip')
    b.close()
