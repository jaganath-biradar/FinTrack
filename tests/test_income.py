def test_create_and_list_income(client):
    payload = {
        "income_name": "Salary",
        "amount": 2500.0,
        "income_date": "2024-01-05",
        "category": "Job"
    }
    r = client.post("/api/income/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["income_name"] == "Salary"

    r2 = client.get("/api/income/")
    assert r2.status_code == 200
    items = r2.json()
    assert any(i["income_name"] == "Salary" for i in items)
