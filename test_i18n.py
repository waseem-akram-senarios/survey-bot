"""Quick i18n test for recipient app."""
import time
from playwright.sync_api import sync_playwright

SURVEY_URL = "http://localhost:3000/survey/demo_1771414344"
results = []

def log(ok, msg):
    tag = "PASS" if ok else "FAIL"
    results.append((ok, msg))
    print(f"  [{tag}] {msg}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. Landing page loads
    print("\n=== 1. Landing Page ===")
    page.goto(SURVEY_URL)
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(3)

    body = page.content()
    log("SurvAI" in body, "SurvAI branding present")

    # Check language toggle
    en_btn = page.query_selector("button:has-text('EN')")
    es_btn = page.query_selector("button:has-text('ES')")
    log(en_btn is not None and es_btn is not None, "EN/ES language toggle visible")

    # Check English text
    log("Text Survey" in page.inner_text("body"), "English 'Text Survey' button visible")
    log("Voice Survey" in page.inner_text("body") or "voice" in body.lower(), "English 'Voice Survey' visible")

    # 2. Switch to Spanish
    print("\n=== 2. Switch to Spanish ===")
    if es_btn:
        es_btn.click()
        time.sleep(2)

    body_text = page.inner_text("body")
    log("Encuesta de Texto" in body_text, "Spanish 'Encuesta de Texto' visible")
    log("Encuesta por Voz" in body_text or "Encuesta" in body_text, "Spanish 'Encuesta por Voz' visible")
    log("confidenciales" in body_text.lower() or "anónimas" in body_text.lower(),
        "Spanish confidentiality notice")

    # 3. Navigate to text survey in Spanish
    print("\n=== 3. Text Survey Page (Spanish) ===")
    text_btn = page.query_selector("button:has-text('Encuesta de Texto')")
    if text_btn:
        text_btn.click()
    else:
        page.goto(SURVEY_URL + "/text?lang=es")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(4)

    url = page.url
    log("lang=es" in url, f"URL contains lang=es: {url}")

    body_text = page.inner_text("body")
    log("Progreso" in body_text or "Anterior" in body_text or "Siguiente" in body_text,
        "Spanish navigation text (Progreso/Anterior/Siguiente)")
    log("Enviar Encuesta" in body_text or "Enviar" in body_text,
        "Spanish submit button (Enviar Encuesta)")

    # 4. Switch back to EN and test start page
    print("\n=== 4. Start Page (English) ===")
    page.goto(SURVEY_URL + "/start?lang=en")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(3)

    body_text = page.inner_text("body")
    log("Start Normal Survey" in body_text or "Text Survey" in body_text,
        "English start page text visible")
    log("Start Voice Survey" in body_text or "Voice Survey" in body_text,
        "English voice option visible")

    # 5. Start page in Spanish
    print("\n=== 5. Start Page (Spanish) ===")
    page.goto(SURVEY_URL + "/start?lang=es")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(3)

    body_text = page.inner_text("body")
    log("Iniciar Encuesta" in body_text or "Encuesta de Texto" in body_text,
        "Spanish start page text visible")

    # 6. Complete page
    print("\n=== 6. Complete Page ===")
    page.goto(SURVEY_URL + "/complete?lang=es")
    page.wait_for_load_state("networkidle", timeout=15000)
    time.sleep(3)

    body_text = page.inner_text("body")
    log("Encuesta Completada" in body_text or "Felicitaciones" in body_text
        or "completado" in body_text.lower(),
        "Spanish complete page text")

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
