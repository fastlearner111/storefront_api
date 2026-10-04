from app.oauth2 import create_access_token

def test_add_to_wishlist(authorized_client, test_products):
    res = authorized_client.post("/wishlist/", json={
        "product_id": test_products[0].id,
        "dir": 1,
    })
    assert res.status_code == 201

def test_duplicate_add_returns_409(authorized_client, test_products):
    body = {"product_id": test_products[0].id, "dir": 1}
    assert authorized_client.post("/wishlist/", json=body).status_code == 201
    assert authorized_client.post("/wishlist/", json=body).status_code == 409


def test_remove_from_wishlist(authorized_client, test_products):
    pid = test_products[0].id
    authorized_client.post("/wishlist/", json={"product_id": pid, "dir": 1})
    res = authorized_client.post("/wishlist/", json={"product_id": pid, "dir": 0})
    assert res.status_code == 201
    assert authorized_client.get("/wishlist/").json() == []


def test_remove_missing_entry_returns_404(authorized_client, test_products):
    res = authorized_client.post("/wishlist/", json={"product_id": test_products[0].id, "dir": 0})
    assert res.status_code == 404


def test_wishlist_unknown_product_returns_404(authorized_client):
    assert authorized_client.post("/wishlist/", json={"product_id": 99999, "dir": 1}).status_code == 404


def test_wishlist_dir_must_be_zero_or_one(authorized_client, test_products):
    assert authorized_client.post("/wishlist/", json={"product_id": test_products[0].id, "dir": -5}).status_code == 422


def test_list_wishlist_returns_added_items(authorized_client, test_products):
    pid = test_products[0].id
    authorized_client.post("/wishlist/", json={"product_id": pid, "dir": 1})
    res = authorized_client.get("/wishlist/")
    assert res.status_code == 200
    assert [item["product_id"] for item in res.json()] == [pid]


def test_wishlist_is_per_user(authorized_client, test_products, test_user2):
    pid = test_products[0].id
    other = {"Authorization": "Bearer " + create_access_token(
        {"user_id": test_user2["id"], "role": "user"})}
    # The other user adds an item; the logged-in user's own list must stay empty.
    authorized_client.post("/wishlist/", json={"product_id": pid, "dir": 1}, headers=other)
    assert authorized_client.get("/wishlist/").json() == []


def test_wishlist_requires_login(client):
    assert client.get("/wishlist/").status_code == 401

def test_wishlist_does_not_expose_owner_details(authorized_client, test_products):
    pid = test_products[3].id  # this product belongs to the other test user
    authorized_client.post("/wishlist/", json={"product_id": pid, "dir": 1})
    res = authorized_client.get("/wishlist/")
    assert res.status_code == 200
    assert "hello123456@gmail.com" not in res.text
    assert "owner" not in res.json()[0]["product"]