"""Small smoke coverage retained while entity-level tests live in dedicated modules."""


def test_health_check_returns_healthy(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_redirect_slash_behavior_is_disabled(client):
    response = client.get("/api/users/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
