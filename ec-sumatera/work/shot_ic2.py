import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for sch in ['light','dark']:
            ctx=await b.new_context(viewport={'width':1000,'height':500},color_scheme=sch,device_scale_factor=3)
            pg=await ctx.new_page()
            await pg.goto('file:///home/claude/ec-sumatera/work/new27.html')
            await pg.locator('.tabs').screenshot(path=f'work/shots/ict_{sch}.png')
        await b.close()
asyncio.run(main())
