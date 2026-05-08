from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_vite_localhost_and_loopback_origins() -> None:
    client = TestClient(app)

    for origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
        response = client.options(
            "/api/reports",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin
