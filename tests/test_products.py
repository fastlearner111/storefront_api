PRODUCT = {"name": "Desk Lamp", "description": "Adjustable LED lamp", "price": 24.99}


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

def test_admin_can_update_product(authorized_admin_client, test_products):
    pid = test_products[0].id
    res = authorized_admin_client.put(f"/products/{pid}", json={**PRODUCT, "name": "Updated Lamp"})
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Lamp"


def test_non_admin_cannot_update_product(authorized_client, test_products):
    pid = test_products[0].id
    assert authorized_client.put(f"/products/{pid}", json=PRODUCT).status_code == 403


def test_admin_can_delete_product(authorized_admin_client, test_products):
    pid = test_products[0].id
    assert authorized_admin_client.delete(f"/products/{pid}").status_code == 204
    assert authorized_admin_client.get(f"/products/{pid}").status_code == 404


def test_non_admin_cannot_delete_product(authorized_client, test_products):
    pid = test_products[0].id
    assert authorized_client.delete(f"/products/{pid}").status_code == 403


def test_delete_missing_product_returns_404(authorized_admin_client):
    assert authorized_admin_client.delete("/products/99999").status_code == 404


def test_public_product_list_hides_owner_details(client, test_products):
    res = client.get("/products/")
    assert res.status_code == 200
    assert len(res.json()) > 0
    for item in res.json():
        assert "owner" not in item
    assert "hello123@gmail.com" not in res.text

def test_negative_limit_is_rejected(client):
    assert client.get("/products/?limit=-1").status_code == 422


def test_negative_skip_is_rejected(client):
    assert client.get("/products/?skip=-1").status_code == 422


def test_limit_has_an_upper_bound(client):
    assert client.get("/products/?limit=100000").status_code == 422

VALID_PRODUCT = {"name": "Desk Lamp", "description": "Adjustable LED lamp", "price": 24.99}


def test_negative_price_is_rejected(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "price": -5})
    assert res.status_code == 422


def test_zero_price_is_rejected(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "price": 0})
    assert res.status_code == 422


def test_empty_name_is_rejected(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "name": ""})
    assert res.status_code == 422


def test_whitespace_only_name_is_rejected(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "name": "   "})
    assert res.status_code == 422


def test_absurd_price_is_rejected(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "price": 1e12})
    assert res.status_code == 422


def test_update_applies_the_same_rules(authorized_admin_client, test_products):
    pid = test_products[0].id
    res = authorized_admin_client.put(f"/products/{pid}", json={**VALID_PRODUCT, "price": -1})
    assert res.status_code == 422


def test_smallest_valid_price_is_accepted(authorized_admin_client):
    res = authorized_admin_client.post("/products/", json={**VALID_PRODUCT, "price": 0.01})
    assert res.status_code == 201