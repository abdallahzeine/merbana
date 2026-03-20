def _seed_product(client):
    client.post(
        "/api/categories",
        json={"id": "99999999-9999-9999-9999-999999999999", "name": "Bakery"},
    )
    product = {
        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "name": "Croissant",
        "price": 4.0,
        "category_id": "99999999-9999-9999-9999-999999999999",
        "created_at": "2026-03-20T00:00:00Z",
        "sizes": [],
    }
    assert client.post("/api/products", json=product).status_code == 201
    return product


def test_orders_create_list_get_delete(client):
    product = _seed_product(client)

    next_number = client.get("/api/orders/next-number")
    assert next_number.status_code == 200
    assert next_number.json()["order_number"] == 1

    order_payload = {
        "payment_method": "cash",
        "order_type": "dine_in",
        "note": "table 1",
        "items": [
            {
                "product_id": product["id"],
                "name": product["name"],
                "price": 4.0,
                "quantity": 2,
                "size": None,
                "subtotal": 8.0,
            }
        ],
    }

    created = client.post("/api/orders", json=order_payload)
    assert created.status_code == 201
    order_id = created.json()["id"]
    assert created.json()["total"] == 8.0

    listed = client.get("/api/orders")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    fetched = client.get(f"/api/orders/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["order_number"] == 1

    deleted = client.delete(f"/api/orders/{order_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/api/orders/{order_id}")
    assert missing.status_code == 404


def test_orders_invalid_payload_and_missing_delete(client):
    bad = client.post(
        "/api/orders",
        json={"payment_method": "cash", "order_type": "dine_in", "items": []},
    )
    assert bad.status_code == 422

    missing = client.delete("/api/orders/ffffffff-ffff-ffff-ffff-ffffffffffff")
    assert missing.status_code == 404
