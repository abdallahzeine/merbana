def _debtor_payload():
    return {
        "id": "12121212-1212-1212-1212-121212121212",
        "name": "Customer A",
        "amount": 55.5,
        "note": "weekly",
        "created_at": "2026-03-20T00:00:00Z",
    }


def test_debtors_crud_and_mark_paid(client):
    payload = _debtor_payload()

    created = client.post("/api/debtors", json=payload)
    assert created.status_code == 201

    unpaid = client.get("/api/debtors?status=unpaid")
    assert unpaid.status_code == 200
    assert unpaid.json()["data"][0]["id"] == payload["id"]

    paid = client.post(f"/api/debtors/{payload['id']}/mark-paid", json={})
    assert paid.status_code == 200
    assert paid.json()["paid_at"] is not None

    paid_list = client.get("/api/debtors?status=paid")
    assert paid_list.status_code == 200
    assert len(paid_list.json()["data"]) == 1

    deleted = client.delete(f"/api/debtors/{payload['id']}")
    assert deleted.status_code == 204


def test_debtors_duplicate_and_missing(client):
    payload = _debtor_payload()
    assert client.post("/api/debtors", json=payload).status_code == 201

    duplicate = client.post("/api/debtors", json=payload)
    assert duplicate.status_code == 409

    missing = client.get("/api/debtors/ffffffff-ffff-ffff-ffff-ffffffffffff")
    assert missing.status_code == 404
