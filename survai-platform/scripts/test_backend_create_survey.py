#!/usr/bin/env python3
"""
Test survey creation directly against the backend API (no frontend).
Run: python scripts/test_backend_create_survey.py [BASE_URL]
Example: python scripts/test_backend_create_survey.py http://54.86.65.150:8080
         python scripts/test_backend_create_survey.py http://localhost:8080
"""
import json
import sys
import uuid
from datetime import datetime

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080").rstrip("/")
API = f"{BASE}/api"


def main():
    template_name = f"Backend_Test_Survey_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
    question_id = str(uuid.uuid4())

    print(f"Base URL: {BASE}")
    print(f"Template name: {template_name}")
    print(f"Question ID:  {question_id}")
    print()

    # 1. Create template
    print("1. POST /api/templates/create ...")
    r = requests.post(
        f"{API}/templates/create",
        json={"TemplateName": template_name},
        headers={"Content-Type": "application/json", "accept": "application/json"},
        timeout=15,
    )
    if r.status_code not in (200, 201):
        print(f"   FAILED: {r.status_code} - {r.text}")
        return 1
    print(f"   OK: {r.status_code} - {r.text.strip()[:80]}")

    # 2. Create one open question
    print("2. POST /api/questions ...")
    question_payload = {
        "QueId": question_id,
        "QueText": "Test question from backend script",
        "QueCriteria": "open",
        "QueScale": None,
        "QueCategories": None,
        "ParentId": None,
        "ParentCategoryTexts": None,
        "Autofill": "No",
    }
    r = requests.post(
        f"{API}/questions",
        json=question_payload,
        headers={"Content-Type": "application/json", "accept": "application/json"},
        timeout=15,
    )
    if r.status_code not in (200, 201):
        print(f"   FAILED: {r.status_code} - {r.text}")
        return 1
    print(f"   OK: {r.status_code} - {r.text.strip()[:80]}")

    # 3. Add question to template
    print("3. POST /api/templates/addquestions ...")
    r = requests.post(
        f"{API}/templates/addquestions",
        json={
            "TemplateName": template_name,
            "QueId": question_id,
            "Order": 1,
        },
        headers={"Content-Type": "application/json", "accept": "application/json"},
        timeout=15,
    )
    if r.status_code not in (200, 201):
        print(f"   FAILED: {r.status_code} - {r.text}")
        return 1
    print(f"   OK: {r.status_code}")

    print()
    print("Backend survey creation succeeded. You can create a survey from the backend.")
    print(f"Template '{template_name}' is in the list at {BASE}/api/templates/list")
    return 0


if __name__ == "__main__":
    sys.exit(main())
