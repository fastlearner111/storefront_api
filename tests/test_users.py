def test_create_user(client):
    res = client.post("/users/", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"
