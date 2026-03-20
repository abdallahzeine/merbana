def test_products_crud_and_filtering(client):
    category = {
        "id": "44444444-4444-4444-4444-444444444444",
        "name": "Cold Drinks",
    }
    assert client.post("/api/categories", json=category).status_code == 201

    product = {
        "id": "55555555-5555-5555-5555-555555555555",
        "name": "Lemonade",
        "price": 2.5,
        "category_id": category["id"],
        "created_at": "2026-03-20T00:00:00Z",
        "sizes": [
            {
                "id": "66666666-6666-6666-6666-666666666666",
                "name": "Large",
                "price": 0.5,
                "sort_order": 1,
            }
        ],
    }

    created = client.post("/api/products", json=product)
    assert created.status_code == 201
    assert created.json()["category_name"] == "Cold Drinks"

    listed = client.get(f"/api/products?category_id={category['id']}")
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    updated = client.put(
        f"/api/products/{product['id']}",
        json={"name": "Lemonade XL", "sizes": []},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Lemonade XL"

    deleted = client.delete(f"/api/products/{product['id']}")
    assert deleted.status_code == 204


def test_products_invalid_category_and_duplicate(client):
    payload = {
        "id": "77777777-7777-7777-7777-777777777777",
        "name": "Ghost Product",
        "price": 1.0,
        "category_id": "88888888-8888-8888-8888-888888888888",
        "created_at": "2026-03-20T00:00:00Z",
        "sizes": [],
    }
    invalid_category = client.post("/api/products", json=payload)
    assert invalid_category.status_code == 422

    valid = payload | {"category_id": None}
    assert client.post("/api/products", json=valid).status_code == 201
    duplicate = client.post("/api/products", json=valid)
    assert duplicate.status_code == 409
