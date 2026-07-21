def test_create_and_list_expense(client):
    payload = {
        "expense_name": "Coffee",
        "amount": 3.5,
        "expense_date": "2024-01-10",
        "category": "Food"
    }
    r = client.post("/api/expenses/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["expense_name"] == "Coffee"

    r2 = client.get("/api/expenses/")
    assert r2.status_code == 200
    items = r2.json()
    assert any(i["expense_name"] == "Coffee" for i in items)
