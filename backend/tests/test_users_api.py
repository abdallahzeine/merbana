from datetime import datetime, timezone


def _user_payload(user_id: str, name: str = "User One"):
    return {
        "id": user_id,
        "name": name,
        "password": "pw",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def test_users_crud_and_duplicate_conflict(client):
    payload = _user_payload("11111111-1111-1111-1111-111111111111")

    created = client.post("/api/users", json=payload)
    assert created.status_code == 201
    assert created.json()["id"] == payload["id"]

    duplicate = client.post("/api/users", json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "DUPLICATE_ID"

    listed = client.get("/api/users")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = client.put(
        f"/api/users/{payload['id']}",
        json={"name": "Updated"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"

    deleted = client.delete(f"/api/users/{payload['id']}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/users/{payload['id']}")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "NOT_FOUND"


def test_users_invalid_payload_rejected(client):
    response = client.post("/api/users", json={"id": "bad", "name": "x"})
    assert response.status_code == 422
