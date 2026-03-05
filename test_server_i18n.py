"""i18n test against the production server."""
import time
from playwright.sync_api import sync_playwright

SERVER = "http://54.86.65.150:8080"
SURVEY_ID = "demo_robert_1771418512"
SURVEY_URL = f"{SERVER}/survey/{SURVEY_ID}"
results = []

def log(ok, msg):
    tag = "PASS" if ok else "FAIL"
    results.append((ok, msg))
    print(f"  [{tag}] {msg}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. Landing page
    print("\n=== 1. Landing Page (English) ===")
    page.goto(SURVEY_URL, timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(5)

    body = page.inner_text("body")
    print(f"  [DEBUG] Body text (first 300): {body[:300]}")

    log("SurvAI" in page.content(), "SurvAI branding present")

    en_btn = page.query_selector("button:has-text('EN')")
    es_btn = page.query_selector("button:has-text('ES')")
    log(en_btn is not None and es_btn is not None, "EN/ES language toggle visible")
    log("Text Survey" in body or "AI-Powered" in body, "English content rendered")

    # 2. Switch to Spanish
    print("\n=== 2. Switch to Spanish ===")
    if es_btn:
        es_btn.click()
        time.sleep(3)
        body = page.inner_text("body")
        print(f"  [DEBUG] Body after ES click (first 300): {body[:300]}")
    
    log("Encuesta de Texto" in body or "Encuesta" in body, "Spanish text visible after ES click")
    log("confidenciales" in body.lower() or "anónimas" in body.lower() or "encuesta con ia" in body.lower(),
        "Spanish UI elements present")

    # 3. Navigate to text survey (Spanish)
    print("\n=== 3. Text Survey (Spanish) ===")
    text_btn = page.query_selector("button:has-text('Encuesta de Texto')")
    if text_btn:
        text_btn.click()
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(5)
    else:
        page.goto(f"{SURVEY_URL}/text?lang=es", timeout=20000)
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(5)

    url = page.url
    body = page.inner_text("body")
    print(f"  [DEBUG] Text page URL: {url}")
    print(f"  [DEBUG] Text page body (first 300): {body[:300]}")
    
    log("lang=es" in url, f"URL contains lang=es")
    log("Progreso" in body or "Anterior" in body or "Siguiente" in body,
        "Spanish navigation (Progreso/Anterior/Siguiente)")
    log("Enviar" in body, "Spanish submit button")

    # 4. Start page English
    print("\n=== 4. Start Page (English) ===")
    page.goto(f"{SURVEY_URL}/start?lang=en", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(4)
    body = page.inner_text("body")
    log("Text Survey" in body or "Start Normal" in body, "English start page")

    # 5. Start page Spanish
    print("\n=== 5. Start Page (Spanish) ===")
    page.goto(f"{SURVEY_URL}/start?lang=es", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(4)
    body = page.inner_text("body")
    log("Encuesta de Texto" in body or "Iniciar" in body, "Spanish start page")

    # 6. Complete page Spanish
    print("\n=== 6. Complete Page (Spanish) ===")
    page.goto(f"{SURVEY_URL}/complete?lang=es", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(4)
    body = page.inner_text("body")
    print(f"  [DEBUG] Complete page body (first 300): {body[:300]}")
    log("Completada" in body or "Felicitaciones" in body or "completado" in body.lower(),
        "Spanish complete page")

    browser.close()

# Summary
print("\n" + "=" * 50)
passed = sum(1 for ok, _ in results if ok)
failed = sum(1 for ok, _ in results if not ok)
print(f"RESULTS: {passed} passed, {failed} failed, {len(results)} total")
if failed:
    print("\nFailed tests:")
    for ok, msg in results:
        if not ok:
            print(f"  - {msg}")
print("=" * 50)
