# Storefront REST API

![CI](https://github.com/fastlearner111/storefront_api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF.svg)
![Render](https://img.shields.io/badge/Render-Deployed-d97706.svg)


An e-commerce REST API built with FastAPI, PostgreSQL, and SQLAlchemy: JWT authentication, role-based access control (user vs admin), a product catalog with search and pagination, and a per-user wishlist.

**Live deployment**
- Base URL: https://storefront-api-1sqc.onrender.com
- Swagger UI: https://storefront-api-1sqc.onrender.com/docs
- ReDoc: https://storefront-api-1sqc.onrender.com/redoc

Hosted on Render's free tier (Docker) with a Supabase PostgreSQL database. After a period of inactivity the first request can be slow while the instance wakes up.

## What it does

- Registration and login with bcrypt-hashed passwords and JWT bearer tokens (OAuth2 password flow, form-encoded `/login`). Passwords are limited to 72 bytes, the most bcrypt can use.
- Two roles. Every public registration creates a `user`. Admins are created by promoting an account in the database. The server reads the role from the database on every request and never trusts the role claim inside the token.
- Admin-only product create, update, and delete through a reusable `require_admin` dependency. Browsing products is public.
- Product list with `search`, `limit` (1 to 100), and `skip`, ordered by id so pages are stable. Responses include `owner_id` but no owner details.
- Per-user wishlist with a composite primary key (`user_id`, `product_id`), added or removed through one toggle endpoint
- `GET /users/{id}` is limited to the user themselves or an admin
- Login rate limit of 5 requests per minute per client IP, best effort (see Known limitations)
- `/health` endpoint that returns 503 when the database check fails

## Stack

Python 3.11, FastAPI, SQLAlchemy, PostgreSQL (Supabase in production, a Postgres container locally), bcrypt, python-jose, SlowAPI, Pytest, Docker and Docker Compose, GitHub Actions, Render.

## API

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/users/` | none | JSON `{"email", "password"}`. Role is always `user`. 409 on a duplicate email, 422 on invalid input. |
| POST | `/login` | none | Form-encoded `username` and `password`. 403 on bad credentials, 429 over the limit. |
| GET | `/users/{id}` | bearer | Own record or admin. 403 otherwise. |
| GET | `/products/` | none | Query params `search` (max 100 characters), `limit` (1 to 100, default 10), `skip` (0 or more) |
| GET | `/products/{id}` | none | 404 if missing |
| POST | `/products/` | bearer, admin | 401 without a token, 403 for non-admins |
| PUT | `/products/{id}` | bearer, admin | 403 for non-admins |
| DELETE | `/products/{id}` | bearer, admin | 204, 403 for non-admins |
| POST | `/wishlist/` | bearer | `{"product_id", "dir"}` with `dir` 0 or 1. `dir=1` adds (409 on a duplicate), `dir=0` removes. |
| GET | `/wishlist/` | bearer | Items for the logged-in user |
| GET | `/health` | none | 200 when the database answers, 503 when it does not |

**Register** (a `role` field in the request is ignored)

```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/users/' \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response (201):

```json
{"id": 5, "email": "user@example.com", "role": "user", "created_at": "2026-10-04T14:21:00.741221Z"}
```

**Log in** (form-encoded, so the Authorize button in Swagger works)

```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/login' \
  -d 'username=user@example.com&password=yourpassword'
```

Response (200): `{"access_token": "<jwt>", "token_type": "bearer"}`

**Create a product** (admin only)

```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/products/' \
  -H 'Authorization: Bearer <admin_jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Desk Lamp", "description": "Adjustable LED lamp", "price": 24.99}'
```

A non-admin token returns 403 `Admins only`, and no token returns 401.

**Toggle a wishlist item**

```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/wishlist/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"product_id": 1, "dir": 1}'
```

## Project structure

```
app/
  routers/       auth, users, products, wishlist
  config.py      settings from environment variables
  database.py    SQLAlchemy engine and session
  dependencies.py  require_admin guard
  limiter.py     SlowAPI limiter and client key function
  main.py        app setup, routers, health check
  models.py      User, Product, Wishlist
  oauth2.py      JWT creation and verification, get_current_user
  schemas.py     Pydantic request and response models
  utils.py       bcrypt hash and verify
tests/           Pytest suite
alembic/         migration (see Known limitations)
docker-compose.yml, Dockerfile
.github/workflows/ci.yml
```

## Design decisions

**RBAC through a dependency.** `require_admin` wraps `get_current_user` and is attached to each admin route with `dependencies=[Depends(require_admin)]`, so the restriction is visible in the route definition.

**The database decides the role.** The token carries a `role` claim, but `get_current_user` loads the user from the database and uses the stored role. A token that claims `admin` for a normal user is still a normal user, and demoting an admin takes effect on the next request. This costs one database lookup per request.

**Wishlist uses a composite primary key** (`user_id`, `product_id`) instead of an auto-increment id plus a unique constraint, so the schema itself rejects a duplicate pair.

**Input is validated at the edge.** Pagination bounds, the bcrypt password limit, and the wishlist `dir` value are checked by request schemas, so bad input gets a 422 before it reaches the database.

**One config for local and hosted databases.** `config.py` accepts either individual database variables or a single `DATABASE_URL`, and rewrites `postgres://` to `postgresql://`, so the same code runs in Docker Compose and on a managed host.

## Testing

45 tests. CI runs the suite against a PostgreSQL service on every push and pull request, with coverage reported by `pytest --cov=app`.

```bash
docker compose up -d --build
docker compose exec api pytest -v --cov=app
```

The suite covers authentication and login edge cases, the rate limiter's key function, products (admin-only create, update, and delete, plus pagination bounds), regression tests for each security bug below, users, the wishlist (duplicate adds, removal, per-user lists, owner details staying hidden), and `/health`.

What the suite does and does not do:
- Tests use real signed tokens from the real token code, and each test starts from freshly created tables.
- `tests/conftest.py` refuses to run against a database host that is not local, because the tests drop and recreate every table.
- The login rate limiter is disabled during the suite. Only its key function has unit tests.
- Product name and price validation is not tested (it does not exist yet, see Known limitations).
- The "token for a deleted user returns 401" path and the concurrent wishlist add path have no tests.

## Bugs found and fixed

**Security**

- **Anyone could register as an admin.** Registration passed the caller's `role` field straight into the database. Fixed so every registration creates a `user`, with a test that fails if the field is honored again. Verified on the deployed API: the same request that used to return `"role": "admin"` now returns `"role": "user"`.
- **The JWT secret was a hardcoded string in the repository.** Anyone could sign a token claiming to be an admin. The secret now comes from the environment and was rotated in production. Verified on the deployed API: a token signed with the old string gets a 401.
- **The token's role claim overrode the database role.** `get_current_user` copied the role from the token onto the user. Fixed so the database role is the only source of truth. A test fails if the override comes back.
- **The public product list exposed every owner's email and role.** Product responses now return `owner_id` only, with a test, and the change was verified on the deployed API.
- **Any logged-in user could read any other user's email and role** through `GET /users/{id}`. Now limited to the user themselves or an admin, with tests.
- **The login rate limiter never limited anything in production.** Behind Render's proxy the app only sees Render's internal proxy addresses, which vary per request, so no address ever reached the limit. It now keys on a proxy-appended `X-Forwarded-For` entry and limits correctly from separate networks (see Known limitations for what it still cannot do).

**Reliability**

- **A duplicate email returned a 500.** The database rejected the second insert and nothing caught it. It now returns 409.
- **A password longer than 72 bytes returned a 500** at registration and at login, because bcrypt refuses longer input. Registration now rejects it with a 422, counting bytes and not characters, and login treats it as a wrong password.
- **Negative `limit` or `skip` returned a 500, and `limit` had no upper bound,** so one request could return the whole table. Both are validated now (limit 1 to 100, skip 0 or more) and pages are ordered by id.
- **Any wishlist `dir` below 1 was treated as a removal.** The schema now accepts only 0 or 1. Two simultaneous adds of the same item now return 409 instead of a database error (a code fix without a test, since the race is hard to reproduce).
- **`/health` reported `"status": "ok"` when the database check failed.** It now returns 503.
- **A token for a user who no longer exists crashed `get_current_user`.** It now returns a 401.
- **The local Docker Compose file did not work.** It used GitHub Actions secret syntax and pointed the API at `localhost` instead of the database container. Rewritten.
- **The test suite could drop tables in a real database.** It now refuses to run against a non-local host.

## Known limitations

- **Login rate limiting is best effort.** `/login` is limited to 5 requests per minute per client IP, and it limits correctly from separate networks. A client that forges proxy headers can still evade it in production. Counters are in memory and Render runs a single worker, so they reset on a restart. Clients behind one shared network address share one bucket. Registration and the other endpoints have no rate limit.
- **Product input is lightly validated.** The schema only checks types for `name`, `description`, and `price`, so an empty name or a zero or negative price is accepted. Only admins can create or update products.
- **Prices are stored as floating point.** Money should use `NUMERIC` or integer cents.
- **Registration reveals whether an email is already registered** (409), and emails are case-sensitive.
- **Access tokens cannot be revoked before they expire,** and there are no refresh tokens.
- **There is no admin signup.** Promote an account with `UPDATE users SET role = 'admin' WHERE email = '...'`.
- **The old hardcoded JWT secret is still in the git history.** It was rotated and no longer signs valid tokens.
- **Alembic has one migration, but the app creates tables at startup** with `create_all`, and the migration has not been verified against an empty database.

## Running locally

Prerequisites: Docker and Docker Compose.

```bash
git clone https://github.com/fastlearner111/storefront_api.git
cd storefront_api
docker compose up --build
```

The API is available at http://localhost:8000 (docs at `/docs`) after about 15 seconds on first start. Compose starts the API (service `api`) and PostgreSQL (service `db`) and creates the tables at startup. It uses development defaults for the database password and the JWT secret. Set your own for anything beyond local use:

```bash
SECRET_KEY=your-own-random-value docker compose up --build
```

If port 5432 is already in use, stop the other Postgres container first.
