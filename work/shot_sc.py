import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':900})
        pg.on('pageerror',lambda e:print('ERR',e))
        await pg.goto('file:///home/claude/ec-sumatera/work/new28.html')
        await pg.locator('#tnSc button').nth(2).click()
        for t in ['tnT1','tnT2']:
            print(t, await pg.evaluate(f'[...document.querySelectorAll("#{t} tbody tr")].map(r=>r.cells[0].innerText).join("|")'))
        await pg.locator('#sTab button[data-t="SM"]').click()
        await pg.locator('#smSc button').nth(3).click()
        for i in ['smC1','smC4','smC6','smC9','coC1']:
            await pg.locator('#'+i).scroll_into_view_if_needed()
            await pg.locator('#'+i).screenshot(path=f'work/shots/sc_{i}.png')
        await b.close()
asyncio.run(main())
