"""Debug what the landing page actually renders."""
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.on("console", lambda msg: print(f"  CONSOLE [{msg.type}]: {msg.text}"))
    page.on("pageerror", lambda err: print(f"  PAGE_ERROR: {err}"))

    page.goto("http://localhost:3000/survey/demo_1771414344")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(5)

    print("\n--- BODY TEXT ---")
    print(page.inner_text("body")[:2000])
    print("\n--- URL ---")
    print(page.url)

    # Also check text page
    print("\n\n=== TEXT PAGE ===")
    page.goto("http://localhost:3000/survey/demo_1771414344/text?lang=es")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(5)
    print(page.inner_text("body")[:2000])

    # Check complete page
    print("\n\n=== COMPLETE PAGE ===")
    page.goto("http://localhost:3000/survey/demo_1771414344/complete?lang=es")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(5)
    print(page.inner_text("body")[:2000])

    browser.close()
