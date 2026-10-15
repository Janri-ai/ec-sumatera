import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':900})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/ec-sumatera/work/new45.html')
        await pg.click('#sTab button[data-t="RW"]')
        await pg.screenshot(path='work/rw_all.png',full_page=True)
        await pg.click('#rwSc button[data-v="2124"]'); await pg.click('#rwPer button[data-v="M"]')
        await pg.screenshot(path='work/rw_sbr_m.png',full_page=True)
        print(errs)
        print(await pg.inner_text('#rwKp'))
        await b.close()
asyncio.run(main())
