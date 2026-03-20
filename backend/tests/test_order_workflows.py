from backend.models import ActivityLog, CashTransaction, Product


def _seed_order_context(client):
    client.post(
        "/api/categories",
        json={"id": "cdcdcdcd-cdcd-cdcd-cdcd-cdcdcdcdcdcd", "name": "Workflow"},
    )
    client.post(
        "/api/products",
        json={
            "id": "edededed-eded-eded-eded-edededededed",
            "name": "Workflow Product",
            "price": 7,
            "category_id": "cdcdcdcd-cdcd-cdcd-cdcd-cdcdcdcdcdcd",
            "created_at": "2026-03-20T00:00:00Z",
            "sizes": [],
        },
    )


def test_order_create_register_and_delete_flow(client, test_db):
    _seed_order_context(client)

    product = test_db.query(Product).filter(Product.id == "edededed-eded-eded-eded-edededededed").first()
    product.track_stock = True
    product.stock = 10
    test_db.commit()

    order_payload = {
        "payment_method": "cash",
        "order_type": "dine_in",
        "user_name": "System",
        "items": [
            {
                "product_id": "edededed-eded-eded-eded-edededededed",
                "name": "Workflow Product",
                "price": 7,
                "quantity": 2,
                "size": None,
                "subtotal": 14,
            }
        ],
    }

    created = client.post("/api/orders", json=order_payload)
    assert created.status_code == 201
    order_id = created.json()["id"]

    sale_tx = test_db.query(CashTransaction).filter(CashTransaction.order_id == order_id).first()
    assert sale_tx is not None
    assert sale_tx.type == "sale"

    test_db.refresh(product)
    assert product.stock <= 10

    delete_response = client.delete(f"/api/orders/{order_id}")
    assert delete_response.status_code == 204

    removed_sale = test_db.query(CashTransaction).filter(CashTransaction.order_id == order_id).first()
    assert removed_sale is None

    logs = test_db.query(ActivityLog).all()
    assert len(logs) >= 2
