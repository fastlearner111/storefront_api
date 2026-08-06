def test_add_to_wishlist(client):
    #Creating user
    client.post("/users/", json={
        "email": "wish@example.com",
        "password": "password123",
        "role": "admin"
    })

    # Login
    login = client.post("/login", data={
        "username": "wish@example.com",
        "password": "password123"
    })
    token = login.json()["access_token"]

    # Create product
    product = client.post("/products/", json={
        "name": "Phone",
        "description": "Smartphone",
        "price": 999.99,
        "is_available": True
    }, headers={"Authorization": f"Bearer {token}"})

    product_id = product.json()["id"]

    # Add to wishlist USING JSON BODY, never use param, will get 404
    res = client.post("/wishlist/", json={
        "product_id": product_id,
        "dir": 1
    }, headers={"Authorization": f"Bearer {token}"})

    print("\n[DEBUG RESPONSE]:", res.status_code, res.json())

    assert res.status_code == 201
