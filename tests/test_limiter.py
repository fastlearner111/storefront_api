from types import SimpleNamespace

from app.limiter import client_key


def _req(headers, host="10.0.0.1"):
    return SimpleNamespace(headers=headers, client=SimpleNamespace(host=host))


def test_key_is_third_entry_from_the_right():
    req = _req({"x-forwarded-for": "35.1.2.3, 172.71.0.1, 10.0.0.1"})
    assert client_key(req) == "35.1.2.3"


def test_key_ignores_entries_the_client_prepends():
    req = _req({"x-forwarded-for": "1.2.3.4, 5.6.7.8, 35.1.2.3, 172.71.0.1, 10.0.0.1"})
    assert client_key(req) == "35.1.2.3"


def test_key_ignores_cloudflare_header_sent_by_client():
    req = _req({"cf-connecting-ip": "8.8.8.8", "x-forwarded-for": "35.1.2.3, 172.71.0.1, 10.0.0.1"})
    assert client_key(req) == "35.1.2.3"


def test_key_falls_back_to_connection_address():
    assert client_key(_req({}, host="127.0.0.1")) == "127.0.0.1"
    assert client_key(_req({"x-forwarded-for": "35.1.2.3"}, host="10.0.0.1")) == "10.0.0.1"