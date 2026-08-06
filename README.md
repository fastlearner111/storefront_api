# Storefront REST API

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg)
![Render](https://img.shields.io/badge/Render-Deployed-d97706.svg)

A high-performance, asynchronous e-commerce REST API built with FastAPI, PostgreSQL, and SQLAlchemy. Designed with industry best practices, featuring granular access control, rate limiting, containerized deployment, and a fully automated CI/CD pipeline.

---

## 🌐 Live Cloud Deployment

* **Base API URL:** `[https://storefront-api-1sqc.onrender.com](https://storefront-api-1sqc.onrender.com)`
* **Interactive Swagger UI Docs:** `[https://storefront-api-1sqc.onrender.com/docs](https://storefront-api-1sqc.onrender.com/docs)`
* **ReDoc Specification:** `[https://storefront-api-1sqc.onrender.com/redoc](https://storefront-api-1sqc.onrender.com/redoc)`

---

## Key Features

* **Stateless Authentication & RBAC:** OAuth2 password flow using JWT tokens, bcrypt password hashing, and Role-Based Access Control (`user` vs. `admin` permissions).
* **Rate Limiting & Abuse Prevention:** Custom IP-based rate limiting implemented via SlowAPI (`limiter.py`) returning `429 Too Many Requests` on endpoint abuse.
* **Container Health Monitoring:** Active `/health` endpoint performing live PostgreSQL DB pings (`SELECT 1`) for container orchestrators.
* **E-Commerce Domain:** Fully normalized schemas managing Users, Product Inventories, Categories, and Customer Wishlists.
* **Automated Schema Migrations:** Reproducible database state management using version-controlled Alembic migration scripts.
* **Multi-Container Stack:** Fully isolated local setup using Docker and Docker Compose (`api` + `db`).
* **Comprehensive Testing:** Automated unit and integration test suite using Pytest with code coverage tracking (`pytest-cov`).
* **Production-Grade CI/CD:** GitHub Actions pipeline executing automated test runs on isolated PostgreSQL service containers on every push/PR.

---

## System Architecture & Tech Stack

* **Framework:** FastAPI (Python 3.11+)
* **Database & ORM:** PostgreSQL + SQLAlchemy ORM
* **Migrations:** Alembic
* **Security:** Passlib (bcrypt), PyJWT
* **Rate Limiting:** SlowAPI
* **Containerization:** Docker & Docker Compose
* **Testing:** Pytest, Pytest-Cov
* **CI/CD:** GitHub Actions
* **Hosting:** Render (Web Service + Managed PostgreSQL)

---

## Project Structure

```text
storefront_api/
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI/CD pipeline
├── alembic/                 # Alembic migration scripts & versions
├── app/
│   ├── routers/             # API Controllers (auth, users, products, wishlist)
│   ├── config.py            # Pydantic Settings configuration
│   ├── database.py          # SQLAlchemy engine & session setup
│   ├── limiter.py           # SlowAPI rate limiter instance
│   ├── main.py              # FastAPI app setup, middlewares, & routes
│   ├── models.py            # SQLAlchemy database models
│   ├── oauth2.py            # JWT token creation & verification
│   ├── schemas.py           # Pydantic data validation schemas
│   └── utils.py             # Password hashing helpers
├── tests/                   # Pytest suite
├── docker-compose.yml       # Local multi-container configuration
├── Dockerfile               # API container recipe
├── alembic.ini              # Alembic config
└── requirements.txt         # Python dependencies
```


## 🛠️ Getting Started Locally

### 📌 Prerequisites
- Docker & Docker Compose
- Git

---

## 1️⃣ Clone the Repository

```bash

git clone https://github.com/fastlearner111/storefront_api.git
cd storefront_api
```


## 2️⃣ Create a .env File

```env
DATABASE_HOSTNAME=db
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=storefront

SECRET_KEY=your_super_secret_jwt_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 3️⃣ Start the Docker Stack
```bash
docker compose up --build
```
     API will be available at:
     *   http://localhost:8000
     *   http://localhost:8000/docs
    


## 4️⃣ Apply Database Migrations

```bash
docker compose exec api alembic upgrade head
```


## 🧪 Running Tests
Execute the test suite with coverage tracking locally:
```bash
docker compose exec api pytest -v --cov=app
```











Test commit for GitHub identity
