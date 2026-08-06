import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models, utils
from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.oauth2 import create_access_token

# Disable rate limiting during automated test runs
app.state.limiter.enabled = False

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@{settings.database_hostname}:"
    f"{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


# --- Standard User Fixtures ---

@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "hello123456@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"], "role": test_user["role"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


# --- Admin User Fixtures (For testing Admin-only routes) ---

@pytest.fixture
def test_admin_user(session):
    admin_data = {
        "email": "admin@gmail.com",
        "password": utils.hash("adminpassword123"),
        "role": "admin"
    }
    user = models.User(**admin_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"id": user.id, "email": user.email, "password": "adminpassword123", "role": user.role}


@pytest.fixture
def admin_token(test_admin_user):
    return create_access_token({"user_id": test_admin_user["id"], "role": test_admin_user["role"]})


@pytest.fixture
def authorized_admin_client(client, admin_token):
    client.headers = {**client.headers, "Authorization": f"Bearer {admin_token}"}
    return client


# --- Products Fixture ---

@pytest.fixture
def test_products(test_user, session, test_user2):
    products_data = [
        {
            "name": "Wireless Mechanical Keyboard",
            "description": "Tactile RGB switch mechanical keyboard",
            "price": 89.99,
            "owner_id": test_user["id"],
        },
        {
            "name": "Ergonomic Gaming Mouse",
            "description": "16000 DPI optical sensor mouse",
            "price": 49.99,
            "owner_id": test_user["id"],
        },
        {
            "name": "4K Ultra HD Monitor",
            "description": "27-inch IPS display monitor",
            "price": 329.99,
            "owner_id": test_user["id"],
        },
        {
            "name": "Noise Cancelling Headphones",
            "description": "Over-ear wireless headphones with ANC",
            "price": 199.99,
            "owner_id": test_user2["id"],
        },
    ]

    products = []
    for data in products_data:
        product = models.Product(**data)
        session.add(product)
        session.commit()
        session.refresh(product)
        products.append(product)

    return products