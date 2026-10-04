def test_create_product(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={
        "name": "Laptop",
        "description": "Gaming laptop",
        "price": 1299.99,
        "is_available": True,
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 1299.99
    assert data["is_available"] is True


def test_get_products(client):
    res = client.get("/products/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)