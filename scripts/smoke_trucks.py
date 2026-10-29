"""End-to-end smoke test cho Truck CRUD.

Chạy:
  .\\.venv\\Scripts\\python.exe -m scripts.smoke_trucks

Yêu cầu: uvicorn đang chạy ở http://127.0.0.1:8000.
"""

from __future__ import annotations

import json
import os
import sys
import uuid
from decimal import Decimal
import urllib.error
import urllib.request

# Fix Windows console codec (cp1252) để in được tiếng Việt + emoji test payload
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "http://127.0.0.1:8000/api/v1"

# Suffix ngẫu nhiên để tránh trùng với data cũ
SUFFIX = uuid.uuid4().hex[:6]


def _req(method: str, path: str, body: dict | None = None) -> tuple[int, dict | None]:
    url = f"{BASE}{path}"
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, default=str).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            raw = r.read().decode() or "null"
            return r.status, (json.loads(raw) if raw != "null" else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode() or "null"
        return e.code, (json.loads(raw) if raw != "null" else None)


def _expect(label: str, got: int, want: int, payload: dict | None = None) -> None:
    ok = got == want
    mark = "OK" if ok else "FAIL"
    print(f"  [{mark}] {label}: {got} (expect {want})")
    if not ok:
        print(f"    payload: {payload}")
        sys.exit(1)


def main() -> None:
    print("== 1. CREATE 2 trucks ==")
    t1_payload = {
        "brand": f"Hino-{SUFFIX}",
        "model": "XZU720L",
        "year": 2024,
        "payload_kg": 3500,
        "price_vnd": "680000000",
        "description": "Xe tải nhẹ 3.5T",
    }
    code, t1 = _req("POST", "/trucks", t1_payload)
    _expect("create Hino", code, 201, t1)
    t1_id = t1["id"]

    t2_payload = {
        "brand": f"Isuzu-{SUFFIX}",
        "model": "NLR",
        "year": 2023,
        "payload_kg": 1500,
        "price_vnd": "420000000",
    }
    code, t2 = _req("POST", "/trucks", t2_payload)
    _expect("create Isuzu", code, 201, t2)

    print("\n== 2. CREATE conflict (same brand/model/year) ==")
    code, body = _req("POST", "/trucks", t1_payload)
    _expect("conflict", code, 409, body)

    print("\n== 3. GET list ==")
    code, lst = _req("GET", "/trucks?only_active=true&limit=10")
    _expect("list", code, 200)
    print(f"    count: {len(lst)}")

    print("\n== 4. GET one ==")
    code, got = _req("GET", f"/trucks/{t1_id}")
    _expect("get by id", code, 200)
    assert got["brand"] == f"Hino-{SUFFIX}", got

    print("\n== 5. GET 404 (random uuid) ==")
    code, _ = _req("GET", f"/trucks/{uuid.uuid4()}")
    _expect("404", code, 404)

    print("\n== 6. PATCH price ==")
    code, patched = _req("PATCH", f"/trucks/{t1_id}", {"price_vnd": "650000000"})
    _expect("patch", code, 200)
    assert Decimal(patched["price_vnd"]) == Decimal("650000000"), patched

    print("\n== 7. SEARCH 'Hino' ==")
    code, found = _req("GET", "/trucks/search?q=Hino")
    _expect("search", code, 200)
    assert any(t["brand"].startswith("Hino") for t in found), found

    print("\n== 8. DELETE ==")
    code, _ = _req("DELETE", f"/trucks/{t1_id}")
    _expect("delete", code, 204)

    print("\n== 9. GET after delete → 404 ==")
    code, _ = _req("GET", f"/trucks/{t1_id}")
    _expect("404 after delete", code, 404)

    # Cleanup
    code, _ = _req("DELETE", f"/trucks/{t2['id']}")
    _expect("cleanup Isuzu", code, 204)

    print("\n[OK] All smoke tests passed.")


if __name__ == "__main__":
    main()