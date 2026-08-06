def test_create_product(client):
    # Create a user
    client.post("/users/", json={
        "email": "prod@example.com",
        "password": "password123",
        "role": "admin"
    })

    # Login
    login = client.post("/login", data={
        "username": "prod@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    # Create product
    res = client.post("/products/", json={
        "name": "Laptop",
        "description": "Gaming laptop",
        "price": 1299.99,
        "is_available": True
    }, headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 1299.99
    assert data["is_available"] is True


def test_get_products(client):
    res = client.get("/products/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
