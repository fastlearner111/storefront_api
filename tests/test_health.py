from app.database import get_db
from app.main import app


class BrokenSession:
    def execute(self, *args, **kwargs):
        raise RuntimeError("database down")


def test_health_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "database": "connected"}


def test_health_reports_failure_when_database_is_down(client):
    app.dependency_overrides[get_db] = lambda: BrokenSession()
    res = client.get("/health")
    assert res.status_code == 503
    assert res.json()["status"] == "error"