import asyncio,sys
from playwright.async_api import async_playwright
JS='''()=>{const o={};document.querySelectorAll("table").forEach(t=>{const vis=t.offsetParent!==null||t.closest("details");const rows=[...t.querySelectorAll("tbody tr")].map(r=>r.cells[0]?r.cells[0].innerText.trim():"");o[t.id||"?"]=rows.length+": "+rows.slice(0,40).join(" | ")});return o}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900}); pg.on('pageerror',lambda e:print('ERR',e)); pg.on('console',lambda m:print('CON',m.text) if m.type=='error' else None)
        await pg.goto('file:///home/claude/ec-sumatera/'+sys.argv[1])
        for t,sc in [('HS','hsSc'),('SM','smSc'),('PR','sScopeP'),('EC','sScope'),('PN','pnSc')]:
            await pg.locator(f'#sTab button[data-t="{t}"]').click()
            if sc:
                await pg.locator(f'#{sc} button').nth(1).click()
            r=await pg.evaluate(JS)
            print('=====',t,'scope SEK')
            tab=await pg.evaluate('(t)=>[...document.querySelectorAll("#tab"+t+" table")].map(x=>x.id)',t)
            for k in tab: print(k, r.get(k,'')[:230])
        await b.close()
asyncio.run(main())
