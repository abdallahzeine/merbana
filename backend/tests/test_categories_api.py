def test_categories_crud_and_delete_guard(client):
    category = {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "Hot Drinks",
    }

    created = client.post("/api/categories", json=category)
    assert created.status_code == 201

    product = {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "Coffee",
        "price": 3.5,
        "category_id": category["id"],
        "created_at": "2026-03-20T00:00:00Z",
        "sizes": [],
    }
    assert client.post("/api/products", json=product).status_code == 201

    blocked_delete = client.delete(f"/api/categories/{category['id']}")
    assert blocked_delete.status_code == 409
    assert blocked_delete.json()["detail"]["code"] == "CONFLICT"

    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    allowed_delete = client.delete(f"/api/categories/{category['id']}")
    assert allowed_delete.status_code == 204


def test_categories_duplicate_and_missing(client):
    category = {
        "id": "aaaaaaaa-2222-2222-2222-222222222222",
        "name": "Sweets",
    }
    assert client.post("/api/categories", json=category).status_code == 201

    duplicate = client.post("/api/categories", json=category)
    assert duplicate.status_code == 409

    missing = client.get("/api/categories/ffffffff-ffff-ffff-ffff-ffffffffffff")
    assert missing.status_code == 404
