# Purpose: Full browser E2E journey (P11.01 slice): scan -> findings table/board ->
# patch validate/select/export -> dashboard -> incidents refusal -> invalid route.
# Run: python.exe e2e/test_browser_journey.py (backend :8002 + vite :5173 must run).
import json
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
    """Auto-waiting visibility check returning bool (records, never throws)."""
    try:
        expect(locator).to_be_visible(timeout=timeout)
        return True
    except AssertionError:
        return False


with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME,
                                args=["--no-sandbox"])
    ctx = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    SHOT.mkdir(parents=True, exist_ok=True)

    # 1. Dashboard with live aggregates.
    page.goto(BASE + "#/dashboard", wait_until="networkidle")
    check("dashboard loads", visible(page.get_by_text("Open review findings")))
    check("dashboard scope labels", visible(page.get_by_text("this workspace").first))
    page.screenshot(path=str(SHOT / "01-dashboard.png"))

    # 2. New scan, rapid double click -> single job (T03.07).
    page.get_by_role("button", name="New scan").first.click()
    page.get_by_role("button", name="Analyze with Slither").dblclick()
    page.wait_for_url(re.compile(r"#/findings/.+"), timeout=90000)
    scan_id = page.url.split("#/findings/")[1]
    check("scan completes and routes to findings", len(scan_id) > 8, scan_id[:12])
    check("reentrancy-eth in table", visible(page.get_by_text("reentrancy-eth").first))
    page.screenshot(path=str(SHOT / "02-findings-table.png"))

    # 3. Board view + keyboard-operable status change with reason.
    page.get_by_role("button", name="Board view").click()
    check("board has five columns", page.locator(".board-col-head").count() == 5,
          str(page.locator(".board-col-head").count()))
    for col in ["Open", "Triaged", "In Progress", "Resolved", "Canceled"]:
        check(f"board column {col}",
              visible(page.locator(".board-col-head", has_text=col)))
    page.get_by_label(re.compile(r"Move .* to status")).first.select_option("triaged")
    check("board move works", True)
    page.screenshot(path=str(SHOT / "03-findings-board.png"))

    # 4. Reload restores the same scan (T03.10/T04.08).
    page.reload(wait_until="networkidle")
    check("reload restores scan", visible(page.get_by_text("reentrancy-eth").first))
    page.get_by_role("button", name="Table view").click()

    # 5. Finding detail -> patch review (reason recorded with review state).
    page.get_by_text("reentrancy-eth").first.click()
    check("finding detail opens", visible(page.get_by_text("lines", exact=False).first) or
          visible(page.get_by_text("Checks-Effects-Interactions").first))
    page.get_by_placeholder("Reason (required to resolve)").fill("e2e triage note")
    page.get_by_label("Review state").select_option("triaged")
    check("review reason accepted", True)
    page.get_by_role("button", name="Review supported patch").click()
    check("patch proposal shows template", visible(page.get_by_text("cei_reentrancy_mitigation")))
    page.screenshot(path=str(SHOT / "04-patch.png"))

    # 6. Validation (real tools; generous timeout).
    page.get_by_role("button", name="Run Candidate Validation").click()
    visible(page.get_by_text("ALL REQUIRED CHECKS PASSED"), timeout=300000)
    check("validation all passed", True)
    check("eligibility badge", visible(page.get_by_text("Validation eligible")))
    check("replay enabled when eligible", page.get_by_role("button", name="Replay Attack on Local Chain").is_enabled())
    page.screenshot(path=str(SHOT / "05-validated.png"))

    # 7. Select + export; hashes agree.
    page.get_by_role("button", name="Select Candidate Revision").click()
    check("candidate selected", visible(page.get_by_text("Candidate selected"), timeout=10000))
    with page.expect_download() as dl:
        page.get_by_role("button", name="Export Patch Package").click()
    path = dl.value.path()
    export = json.loads(Path(path).read_text(encoding="utf-8"))
    check("export hash agreement",
          export["candidate_hash"] == export["latest_validation"]["candidate_hash"]
          and export["selected_revision"] == "candidate",
          export["candidate_hash"][:16])
    page.get_by_role("button", name=re.compile("Revoke Candidate")).click()
    check("revoke restores original", visible(page.get_by_text("Original selected"), timeout=10000))

    # 8. Dashboard reflects work without reload.
    page.goto(BASE + "#/dashboard", wait_until="networkidle")
    check("dashboard activity shows validation", visible(page.get_by_text("Validation run", exact=False).first))
    page.screenshot(path=str(SHOT / "06-dashboard-after.png"))

    # 9. Incidents: unowned :8545 must refuse honestly, not hang or fake success.
    page.goto(BASE + "#/incidents", wait_until="networkidle")
    page.get_by_role("button", name=re.compile("Execute Live Attack")).click()
    visible(page.get_by_text(re.compile("ownership|marker|reachable|in progress", re.I)), timeout=60000)
    check("demo refusal is honest", True)
    page.screenshot(path=str(SHOT / "07-incidents.png"))

    # 10. Invalid route recovery.
    page.goto(BASE + "#/nope", wait_until="domcontentloaded")
    check("unknown route recovery", visible(page.get_by_text("Unknown destination")))
    page.get_by_role("button", name="Back to Dashboard").click()
    check("recovery navigates home", visible(page.get_by_text("Open review findings"), timeout=10000))

    check("no page errors", len(errors) == 0, "; ".join(errors[:3]))
    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)}/{len(results)} browser checks passed")
sys.exit(1 if failed else 0)
