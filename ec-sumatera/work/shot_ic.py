import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for sch in ['light','dark']:
            pg=await b.new_page(viewport={'width':1000,'height':500},color_scheme=sch)
            await pg.goto('file:///home/claude/ec-sumatera/work/new26.html')
            await pg.locator('header').screenshot(path=f'work/shots/ic_{sch}.png')
            await pg.locator('.tabs').screenshot(path=f'work/shots/ict_{sch}.png',scale='device')
        await b.close()
asyncio.run(main())
