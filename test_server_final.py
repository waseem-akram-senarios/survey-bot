"""Final i18n verification on server - quick targeted checks."""
import time
from playwright.sync_api import sync_playwright

SERVER = "http://54.86.65.150:8080"
SURVEY_IN_PROGRESS = "demo_robert_1771418512"
SURVEY_COMPLETED = "1772046362166_816"
results = []

def log(ok, msg):
    tag = "PASS" if ok else "FAIL"
    results.append((ok, msg))
    print(f"  [{tag}] {msg}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 1. Landing page - EN/ES toggle works
    print("\n=== 1. Landing: Language Toggle ===")
    page.goto(f"{SERVER}/survey/{SURVEY_IN_PROGRESS}", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(5)
    body = page.inner_text("body")
    log("EN" in body and "ES" in body, "Language toggle buttons visible")
    log("SurvAI" in page.content(), "SurvAI branding")
    log("Text Survey" in body, "English 'Text Survey' button")

    # 2. Switch to Spanish
    print("\n=== 2. Landing: Spanish Mode ===")
    es_btn = page.query_selector("button:has-text('ES')")
    if es_btn:
        es_btn.click()
        time.sleep(3)
    body = page.inner_text("body")
    log("Encuesta de Texto" in body, "Spanish 'Encuesta de Texto'")
    log("Encuesta por Voz" in body, "Spanish 'Encuesta por Voz'")
    log("Encuesta con IA" in body, "Spanish 'Encuesta con IA' badge")

    # 3. Direct nav to text survey in Spanish
    print("\n=== 3. Text Survey (Spanish) ===")
    page.goto(f"{SERVER}/survey/{SURVEY_IN_PROGRESS}/text?lang=es", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(5)
    body = page.inner_text("body")
    log("Progreso" in body, "Spanish 'Progreso' label")
    log("Preguntas" in body, "Spanish 'Preguntas' label")
    log("Enviar Encuesta" in body, "Spanish 'Enviar Encuesta' button")
    log("Anterior" in body, "Spanish 'Anterior' (Previous)")
    log("Siguiente" in body, "Spanish 'Siguiente' (Next)")

    # 4. Text survey in English
    print("\n=== 4. Text Survey (English) ===")
    page.goto(f"{SERVER}/survey/{SURVEY_IN_PROGRESS}/text?lang=en", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(5)
    body = page.inner_text("body")
    log("Progress" in body, "English 'Progress' label")
    log("Questions" in body, "English 'Questions' label")
    log("Submit Survey" in body, "English 'Submit Survey' button")
    log("Previous" in body, "English 'Previous'")
    log("Next" in body, "English 'Next'")

    # 5. Start page Spanish
    print("\n=== 5. Start Page (Spanish) ===")
    page.goto(f"{SERVER}/survey/{SURVEY_IN_PROGRESS}/start?lang=es", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(4)
    body = page.inner_text("body")
    log("Encuesta de Texto" in body, "Spanish start page text survey")
    log("Encuesta por Voz" in body, "Spanish start page voice survey")
    log("Iniciar" in body, "Spanish 'Iniciar' buttons")

    # 6. Complete page (completed survey, Spanish)
    print("\n=== 6. Complete Page (Spanish) ===")
    page.goto(f"{SERVER}/survey/{SURVEY_COMPLETED}/complete?lang=es", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)
    time.sleep(5)
    body = page.inner_text("body")
    print(f"  [DEBUG] Complete body (first 300): {body[:300]}")
    log("Completada" in body or "Felicitaciones" in body or "completado" in body.lower(),
        "Spanish completion text")

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
else:
    print("\nAll tests passed! i18n is working correctly.")
print("=" * 50)
