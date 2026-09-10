import os
import sys
import httpx

BASE_URL = os.getenv("NOXIS_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("NOXIS_API_KEY", "")

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h

def test_health():
    r = httpx.get(f"{BASE_URL}/health", timeout=10)
    ok = r.status_code == 200 and r.json().get("status") == "ok"
    print(f"[{PASS if ok else FAIL}] GET /health -> {r.status_code}")
    return ok

def test_models():
    r = httpx.get(f"{BASE_URL}/v1/models", headers=headers(), timeout=10)
    data = r.json()
    count = len(data.get("data", []))
    ok = r.status_code == 200 and count >= 14
    print(f"[{PASS if ok else FAIL}] GET /v1/models -> {r.status_code} ({count} models)")
    return ok

def test_chat():
    payload = {"model": "gemini", "messages": [{"role": "user", "content": "Say hi"}]}
    r = httpx.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers(), timeout=60)
    data = r.json()
    ok = r.status_code == 200 and "choices" in data
    print(f"[{PASS if ok else FAIL}] POST /v1/chat/completions (gemini) -> {r.status_code}")
    if not ok and "error" in data:
        print(f"       error: {data['error'].get('message', '')}")
    return ok

def test_unknown_model():
    payload = {"model": "nonexistent", "messages": [{"role": "user", "content": "test"}]}
    r = httpx.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers(), timeout=10)
    ok = r.status_code == 404
    print(f"[{PASS if ok else FAIL}] POST /v1/chat/completions (unknown) -> {r.status_code} (expected 404)")
    return ok

def test_stream_reject():
    payload = {"model": "gemini", "messages": [{"role": "user", "content": "test"}], "stream": True}
    r = httpx.post(f"{BASE_URL}/v1/chat/completions", json=payload, headers=headers(), timeout=10)
    ok = r.status_code == 400
    print(f"[{PASS if ok else FAIL}] POST /v1/chat/completions (stream) -> {r.status_code} (expected 400)")
    return ok

def test_auth_reject():
    payload = {"model": "gemini", "messages": [{"role": "user", "content": "test"}]}
    r = httpx.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=10)
    if API_KEY:
        ok = r.status_code == 401
        print(f"[{PASS if ok else FAIL}] POST /v1/chat/completions (no auth) -> {r.status_code} (expected 401)")
        return ok
    else:
        print(f"[PASS] Auth disabled (no NOXIS_API_KEY set)")
        return True

if __name__ == "__main__":
    print(f"N?XIS Gateway Tests -> {BASE_URL}\n")
    results = []
    results.append(test_health())
    results.append(test_models())
    results.append(test_chat())
    results.append(test_unknown_model())
    results.append(test_stream_reject())
    results.append(test_auth_reject())
    passed = sum(results)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)
