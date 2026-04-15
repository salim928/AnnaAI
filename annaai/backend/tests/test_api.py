"""Smoke tests for API routes."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"


def test_root_endpoint(client: TestClient) -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert "AnnaAi" in res.json().get("name", "")


def test_protected_route_rejects_anonymous(client: TestClient) -> None:
    res = client.get("/api/runs")
    assert res.status_code in (401, 403)


def test_webhook_route_rejects_bad_signature(client: TestClient) -> None:
    res = client.post(
        "/api/webhooks/paystack",
        json={"event": "charge.success"},
        headers={"x-paystack-signature": "invalid"},
    )
    assert res.status_code in (400, 401, 403)
