# Purpose: One-off click-stability probe.
from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.goto("http://127.0.0.1:5199#/dashboard", wait_until="networkidle")
    pg.wait_for_timeout(3000)
    btn = pg.get_by_role("button", name="Open findings")
    print("visible:", btn.is_visible(), "enabled:", btn.is_enabled(), "stable:",
          pg.evaluate("el => { const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }",
                      btn.element_handle()))
    try:
        btn.click(timeout=8000)
        print("clicked, url:", pg.url)
    except Exception as e:
        print("CLICK FAIL:", str(e)[-600:])
    b.close()
