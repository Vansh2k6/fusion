# Purpose: Fast browser interaction tests (no tool runs): metric click-through,
# nested filters, keyboard row access, back-button restore, missing-record
# recovery, mobile drawer, unvalidated-accept acknowledgment.
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

BASE = "http://127.0.0.1:5199"
ROOT = Path(__file__).resolve().parent.parent
SHOT = ROOT / "data" / "e2e"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def visible(locator, timeout=15000):
    try:
        expect(locator).to_be_visible(timeout=timeout)
        return True
    except AssertionError:
        return False


def select_scan_named(pg, name_part):
    """Pick the newest scan whose dropdown label contains name_part."""
    sel = pg.locator("#scan-select")
    expect(sel).to_be_visible(timeout=15000)
    texts = sel.locator("option").all_inner_texts()
    values = sel.locator("option").evaluate_all("els => els.map(e => e.value)")
    for text, value in zip(texts, values):
        if name_part in text:
            sel.select_option(value)
            return value
    raise AssertionError(f"no scan named {name_part} in {texts[:5]}")


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    ctx = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))

    # 1. Metric click-through filters match displayed counts (T08.11).
    page.goto(BASE + "#/dashboard", wait_until="networkidle")
    check("dashboard metrics visible", visible(page.get_by_text("Open review findings")))
    page.wait_for_timeout(2000)  # let aggregate + scan reads settle before clicking
    page.get_by_role("button", name="Open findings").click(timeout=15000)
    check("metric opens findings", visible(page.locator("#scan-select")))
    select_scan_named(page, "VulnerableVault")
    check("vulnerable scan selected", visible(page.get_by_text("reentrancy-eth").first))

    # 2. Nested filter intersection + clear-all (T05.14).
    page.get_by_role("button", name=re.compile("Filter")).click()
    page.get_by_role("menuitem", name="Severity").hover()
    page.get_by_label("High", exact=True).check()
    page.keyboard.press("Escape")
    check("severity chip appears", visible(page.get_by_text("Severity: High")))
    check("filter narrows rows", visible(page.get_by_text("reentrancy-eth").first)
          and page.get_by_text("solc-version").count() == 0)
    page.get_by_role("button", name="Clear all").click()
    check("clear-all restores set", visible(page.get_by_text("solc-version").first))

    # 3. Keyboard row access opens detail (T05.06).
    page.locator(".findings-table tbody tr").first.focus()
    page.keyboard.press("Enter")
    check("keyboard opens detail", visible(page.get_by_text("Review supported patch")))

    # 4. Back from detail restores list (T04.09).
    page.get_by_role("button", name="Review supported patch").click()
    check("patch route", visible(page.get_by_text("cei_reentrancy_mitigation"), timeout=30000))
    page.go_back()
    check("back restores findings", visible(page.get_by_text("reentrancy-eth").first))

    # 5. Missing record -> recovery (T04.11).
    page.goto(BASE + "#/findings/does-not-exist", wait_until="domcontentloaded")
    check("missing scan recovery", visible(page.get_by_text("Scan record not found")))
    page.get_by_role("button", name="Open latest scan").click()
    check("recovery opens a scan", visible(page.locator("#scan-select"))
          and not visible(page.get_by_text("Scan record not found"), timeout=3000))
    page.screenshot(path=str(SHOT / "08-recovery.png"))

    # 6. Mobile drawer traps/Escape/returns focus (T04.10).
    page.set_viewport_size({"width": 700, "height": 900})
    check("drawer trigger visible", visible(page.get_by_role("button", name="Open navigation")))
    page.get_by_role("button", name="Open navigation").click()
    check("drawer opens", visible(page.locator(".sidebar.open")))
    page.keyboard.press("Escape")
    check("escape closes drawer", page.locator(".sidebar.open").count() == 0)
    check("focus returns to trigger",
          page.evaluate("document.activeElement?.getAttribute('aria-label')") == "Open navigation")
    page.set_viewport_size({"width": 1440, "height": 900})

    # 7. Unvalidated accept needs acknowledgment; replay stays disabled (T06.17 UI).
    page.goto(BASE + "#/scans/new", wait_until="networkidle")
    page.get_by_role("button", name="Analyze with Slither").click()
    page.wait_for_url(re.compile(r"#/findings/.+"), timeout=90000)
    page.get_by_text("reentrancy-eth").first.click()
    page.get_by_role("button", name="Review supported patch").click()
    check("unvalidated patch loads", visible(page.get_by_text("cei_reentrancy_mitigation"), timeout=30000))
    accept = page.get_by_role("button", name="Select Candidate Revision")
    check("accept blocked until acknowledged", accept.is_disabled())
    page.get_by_text("Select without passing validation").click()
    check("acknowledgment enables accept", accept.is_enabled())
    accept.click()
    check("unvalidated selection message",
          visible(page.get_by_text("without passing validation", exact=False)))
    check("replay stays disabled",
          page.get_by_role("button", name="Replay Attack on Local Chain").is_disabled())
    page.screenshot(path=str(SHOT / "09-unvalidated.png"))

    check("no page errors", len(errors) == 0, "; ".join(errors[:3]))
    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} browser checks passed")
sys.exit(1 if failed else 0)
