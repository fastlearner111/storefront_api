def test_add_to_wishlist(authorized_client, test_products):
    res = authorized_client.post("/wishlist/", json={
        "product_id": test_products[0].id,
        "dir": 1,
    })
    assert res.status_code == 201