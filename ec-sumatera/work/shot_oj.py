from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1300,'height':900});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/ec-sumatera/work/new104.html');pg.click('button[data-t="OJ"]');pg.wait_for_timeout(500)
    print(pg.inner_text('#ojKp'));print(pg.inner_text('#ojT')[:700])
    pg.locator('#tabOJ').screenshot(path='work/oj1.png');pg.click('#ojV button[data-v="VAR"]');pg.click('#ojM button[data-v="S"]');print(pg.inner_text('#ojKp'));print(errs)
