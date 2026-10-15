import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':900})
        await pg.goto('file:///home/claude/ec-sumatera/work/new24.html')
        await pg.locator('#tnSec').screenshot(path='work/shots/tn.png')
        await pg.locator('#tnT1 tr[data-id="2124B"]').click()
        await pg.locator('#tnC').screenshot(path='work/shots/tn_sbrb.png')
        pg2=await b.new_page(viewport={'width':400,'height':800},color_scheme='dark')
        await pg2.goto('file:///home/claude/ec-sumatera/work/new24.html')
        await pg2.locator('#tnSec').screenshot(path='work/shots/tn_m.png')
        print(await pg2.evaluate('document.documentElement.scrollWidth'))
        await b.close()
asyncio.run(main())
