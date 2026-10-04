from jose import jwt
from app.oauth2 import create_access_token

PRODUCT = {"name": "Desk Lamp", "description": "Adjustable LED lamp", "price": 24.99}


def test_register_ignores_role_field(client):
    res = client.post("/users/", json={
        "email": "sneaky@example.com", "password": "password123", "role": "admin"})
    assert res.status_code == 201
    assert res.json()["role"] == "user"


def test_no_token_cannot_create_product(client):
    assert client.post("/products/", json=PRODUCT).status_code == 401


def test_non_admin_cannot_create_product(authorized_client):
    assert authorized_client.post("/products/", json=PRODUCT).status_code == 403


def test_admin_can_create_product(authorized_admin_client):
    assert authorized_admin_client.post("/products/", json=PRODUCT).status_code == 201


def test_token_signed_with_old_hardcoded_secret_is_rejected(client, test_user):
    forged = jwt.encode({"user_id": test_user["id"], "role": "admin"},
                        "your_secret_key", algorithm="HS256")
    res = client.post("/products/", json=PRODUCT,
                      headers={"Authorization": f"Bearer {forged}"})
    assert res.status_code == 401


def test_admin_claim_in_token_does_not_override_database_role(client, test_user):
    # Valid signature, but the database says this user is a normal user.
    token = create_access_token({"user_id": test_user["id"], "role": "admin"})
    res = client.post("/products/", json=PRODUCT,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403