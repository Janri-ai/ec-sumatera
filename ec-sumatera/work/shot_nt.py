import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':900})
        await pg.goto('file:///home/claude/ec-sumatera/work/new25.html')
        print(await pg.evaluate('[document.querySelectorAll("details.nt").length, document.querySelectorAll("details.nt[open]").length]'))
        for t in ['PR','EC','SM','PN','HS']:
            await pg.locator(f'#sTab button[data-t="{t}"]').click()
            print(t, await pg.evaluate('[...document.querySelectorAll("p.note")].filter(e=>e.offsetParent!==null).length'))
        await pg.locator(f'#sTab button[data-t="PR"]').click()
        await pg.locator('#tProd').scroll_into_view_if_needed()
        d=pg.locator('#tabPR details.nt').nth(1); await d.locator('summary').click()
        await d.screenshot(path='work/shots/nt.png')
        await b.close()
asyncio.run(main())
