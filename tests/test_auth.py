def test_login_success(client):
    # Create a user first
    client.post("/users/", json={
        "email": "login@example.com",
        "password": "password123"
    })

    # Attempt login
    res = client.post("/login", data={
        "username": "login@example.com",
        "password": "password123"
    })

    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post("/users/", json={
        "email": "wrongpass@example.com",
        "password": "password123"
    })

    res = client.post("/login", data={
        "username": "wrongpass@example.com",
        "password": "incorrect"
    })

    assert res.status_code == 403


def test_login_nonexistent_user(client):
    res = client.post("/login", data={
        "username": "doesnotexist@example.com",
        "password": "whatever"
    })

    assert res.status_code == 403
