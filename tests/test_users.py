def test_create_user(client):
    res = client.post("/users/", json={
        "email": "test@example.com",
        "password": "password123"
    })

    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "test@example.com"

def test_user_can_read_self(authorized_client, test_user):
    assert authorized_client.get(f"/users/{test_user['id']}").status_code == 200


def test_user_cannot_read_other_user(authorized_client, test_user2):
    assert authorized_client.get(f"/users/{test_user2['id']}").status_code == 403


def test_admin_can_read_any_user(authorized_admin_client, test_user):
    assert authorized_admin_client.get(f"/users/{test_user['id']}").status_code == 200

def test_duplicate_email_is_rejected(client):
    payload = {"email": "dup@example.com", "password": "password123"}
    assert client.post("/users/", json=payload).status_code == 201
    res = client.post("/users/", json=payload)
    assert res.status_code == 409