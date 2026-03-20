def test_activity_list_and_filters(client):
    client.post(
        "/api/debtors",
        json={
            "id": "abababab-abab-abab-abab-abababababab",
            "name": "Debtor For Activity",
            "amount": 10,
            "note": "n",
            "created_at": "2026-03-20T00:00:00Z",
        },
    )

    listed = client.get("/api/activity")
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1

    first = listed.json()["data"][0]
    filtered = client.get(f"/api/activity?user_id={first['user_id']}")
    assert filtered.status_code == 200
    assert "data" in filtered.json()
