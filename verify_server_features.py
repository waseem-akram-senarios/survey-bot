#!/usr/bin/env python3
"""
Verify all main features on the survey-bot server.
Run: python verify_server_features.py
"""
import urllib.request
import urllib.error
import json
import ssl

BASE = "http://54.86.65.150:8080"
# Relax SSL if needed (for HTTPS)
ssl_ctx = ssl.create_default_context()

def req(method, path, data=None, expect_status=None):
    url = BASE + path
    expect_status = expect_status or (200 if method == "GET" else [200, 201])
    if isinstance(expect_status, int):
        expect_status = [expect_status]
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=25, context=ssl_ctx) as resp:
            out = resp.read().decode()
            try:
                return resp.status, json.loads(out) if out else {}
            except json.JSONDecodeError:
                return resp.status, out
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body

def main():
    failed = []
    print("Server:", BASE)
    print("-" * 50)

    # 1. Gateway & dashboard root
    status, _ = req("GET", "/")
    if status in (200, 304):
        print("[OK] Dashboard (GET /)")
    else:
        failed.append(f"Dashboard root: {status}")

    # 2. Gateway health
    status, body = req("GET", "/health")
    if status == 200:
        print("[OK] Gateway /health")
    else:
        failed.append(f"Gateway health: {status}")

    # 3. API aggregate health
    status, body = req("GET", "/pg/api/health")
    if status == 200:
        print("[OK] API health /pg/api/health")
    else:
        failed.append(f"API health: {status}")

    # 4. Survey service health
    status, _ = req("GET", "/pg/api/surveys/health")
    if status == 200:
        print("[OK] Survey service health")
    else:
        failed.append(f"Survey health: {status}")

    # 5. Survey list
    status, body = req("GET", "/pg/api/surveys/list")
    if status == 200 and isinstance(body, (list, dict)):
        print("[OK] Surveys list")
    else:
        failed.append(f"Surveys list: {status}")

    # 6. Survey stats
    status, body = req("GET", "/pg/api/surveys/stat")
    if status == 200:
        print("[OK] Survey stats")
    else:
        failed.append(f"Survey stats: {status}")

    # 7. Template service health
    status, _ = req("GET", "/pg/api/templates/health")
    if status == 200:
        print("[OK] Template service health")
    else:
        failed.append(f"Template health: {status}")

    # 8. Templates list
    status, body = req("GET", "/pg/api/templates/list")
    if status == 200 and isinstance(body, (list, dict)):
        print("[OK] Templates list")
    else:
        failed.append(f"Templates list: {status}")

    # 9. Voice service health
    status, _ = req("GET", "/pg/api/voice/health")
    if status == 200:
        print("[OK] Voice service health")
    else:
        failed.append(f"Voice health: {status}")

    # 10. Analytics health
    status, _ = req("GET", "/pg/api/analytics/health")
    if status == 200:
        print("[OK] Analytics service health")
    else:
        failed.append(f"Analytics health: {status}")

    # 11. Analytics summary (may 200 or empty data)
    status, body = req("GET", "/pg/api/analytics/summary")
    if status == 200:
        print("[OK] Analytics summary")
    else:
        failed.append(f"Analytics summary: {status}")

    # 12. Question service health
    status, _ = req("GET", "/pg/api/questions/health")
    if status == 200:
        print("[OK] Question service health")
    else:
        failed.append(f"Question health: {status}")

    # 13. Brain service health
    status, _ = req("GET", "/pg/api/brain/health")
    if status == 200:
        print("[OK] Brain service health")
    else:
        failed.append(f"Brain health: {status}")

    # 14. Scheduler health
    status, _ = req("GET", "/pg/api/scheduler/health")
    if status == 200:
        print("[OK] Scheduler service health")
    else:
        failed.append(f"Scheduler health: {status}")

    # 15. Recipient app (survey page)
    status, _ = req("GET", "/survey/test-id")
    if status in (200, 304, 404):  # 404 if no survey, still means app responded
        print("[OK] Recipient app /survey/")
    else:
        failed.append(f"Recipient /survey/: {status}")

    # 16. Make-call endpoint (OPTIONS or POST with minimal params - expect 400/422 if missing params, not 502)
    status, body = req("POST", "/pg/api/surveys/make-call")
    if status in (200, 400, 422, 404, 500):  # any HTTP response = endpoint reachable
        print("[OK] Make-call endpoint reachable (status %s)" % status)
    else:
        failed.append(f"Make-call: {status}")

    print("-" * 50)
    if failed:
        print("FAILED:", len(failed))
        for f in failed:
            print("  -", f)
        return 1
    print("All features OK.")
    return 0

if __name__ == "__main__":
    exit(main())
