import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':900})
        await pg.goto('file:///home/claude/ec-sumatera/work/new23.html')
        await pg.get_by_text('Estate Cost',exact=True).first.click()
        for sc in ['Region','SBR']:
            await pg.locator('#sScope').get_by_text(sc,exact=True).click()
            print(sc, (await pg.locator('#kpis').inner_text()).replace('\n',' | '))
            await pg.locator('#kpis').screenshot(path=f'work/shots/kpi_{sc}.png')
        await b.close()
asyncio.run(main())
