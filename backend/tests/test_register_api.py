def test_register_deposit_withdraw_and_close_shift(client):
    initial = client.get("/api/register")
    assert initial.status_code == 200
    assert initial.json()["current_balance"] == 0

    deposit = client.post(
        "/api/register/deposit",
        json={"amount": 120, "note": "float"},
    )
    assert deposit.status_code == 201
    assert deposit.json()["type"] == "deposit"

    withdraw = client.post(
        "/api/register/withdrawal",
        json={"amount": 20, "note": "petty cash"},
    )
    assert withdraw.status_code == 201
    assert withdraw.json()["type"] == "withdrawal"

    state = client.get("/api/register")
    assert state.status_code == 200
    assert state.json()["current_balance"] == 100

    close = client.post("/api/register/close-shift", json={"note": "night"})
    assert close.status_code == 201


def test_register_negative_cases(client):
    invalid = client.post("/api/register/deposit", json={"amount": 0})
    assert invalid.status_code == 422

    too_much = client.post("/api/register/withdrawal", json={"amount": 50})
    assert too_much.status_code == 422

    transactions = client.get("/api/register/transactions")
    assert transactions.status_code == 200
    assert "data" in transactions.json()
