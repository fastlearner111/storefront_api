from types import SimpleNamespace

from app.limiter import client_key


def _req(headers, host="10.0.0.1"):
    return SimpleNamespace(headers=headers, client=SimpleNamespace(host=host))


def test_key_uses_cloudflare_header_when_present():
    assert client_key(_req({"cf-connecting-ip": "35.1.2.3"})) == "35.1.2.3"


def test_key_ignores_x_forwarded_for():
    req = _req({"x-forwarded-for": "1.2.3.4, 35.1.2.3, 10.0.0.1"})
    assert client_key(req) == "10.0.0.1"


def test_key_falls_back_to_connection_address():
    assert client_key(_req({}, host="127.0.0.1")) == "127.0.0.1"