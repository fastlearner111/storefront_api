🛒 Storefront REST API

```
An e-commerce REST API built with FastAPI, PostgreSQL, and SQLAlchemy, featuring JWT authentication, role-based access control (user vs. admin), a product catalog, and a per-user wishlist.
```

🌐 Live Cloud Deployment
Base API URL: https://storefront-api-1sqc.onrender.com
Interactive Swagger UI Docs: https://storefront-api-1sqc.onrender.com/docs
ReDoc Specification: https://storefront-api-1sqc.onrender.com/redoc

```
✨ Core Features
Tests: 7/7 passing, 82% coverage (pytest -v --cov=app).
JWT Authentication: OAuth2 password flow (/login) issuing tokens that carry both user_id and role, verified on every protected request via get_current_user.
Role-Based Access Control: A require_admin dependency gates product create/update/delete to admin users only; product browsing (GET) stays public.
Rate Limiting on Login: /login is limited to 5 requests/minute per IP via SlowAPI, to slow down credential-stuffing/brute-force attempts.
Wishlist with Composite Key: Wishlist uses a composite primary key (user_id, product_id), so "already in wishlist" is enforced at the database level, not just in application code. A single toggle endpoint (dir=1/dir=0) adds or removes items.
Product Search & Pagination: GET /products/ supports search, limit, and skip query params.
Health Check: /health pings the database with SELECT 1 for container orchestrators.
Dual-Environment DB Config: config.py supports both local dev (individual Postgres env vars) and platform deployments (a single DATABASE_URL, with automatic postgres:// → postgresql:// normalization).
```

```
🛠️ Tech Stack
Framework: FastAPI (Python 3.11+)
Database & ORM: PostgreSQL + SQLAlchemy ORM
Migrations: Alembic
Security: Passlib/bcrypt password hashing, python-jose (JWT)
Rate Limiting: SlowAPI
Containerization: Docker & Docker Compose
Testing: Pytest
CI/CD: GitHub Actions
Hosting: Render (Web Service + Managed PostgreSQL)
```

```
📁 Project Structure
storefront_api/
├── .github/workflows/
│   └── ci.yml               # GitHub Actions CI/CD pipeline
├── alembic/                 # Alembic migration scripts & versions
├── app/
│   ├── routers/
│   │   ├── auth.py          # Login (JWT issuance, rate-limited)
│   │   ├── users.py         # Registration, get-by-id
│   │   ├── products.py      # Public browse, admin-only write/delete
│   │   └── wishlist.py      # Add/remove/list wishlist items
│   ├── config.py            # Pydantic Settings (local + platform env support)
│   ├── database.py          # SQLAlchemy engine & session setup
│   ├── dependencies.py      # require_admin route guard
│   ├── limiter.py           # SlowAPI limiter instance
│   ├── main.py               # FastAPI app setup, routers, health check
│   ├── models.py             # SQLAlchemy models (Product, User, Wishlist)
│   ├── oauth2.py             # JWT creation/verification, get_current_user
│   ├── schemas.py            # Pydantic request/response schemas
│   └── utils.py              # bcrypt password hash/verify
├── tests/                    # Pytest suite
├── docker-compose.yml         # Local multi-container configuration
├── Dockerfile                  # API container recipe
├── alembic.ini                  # Alembic config
└── requirements.txt              # Python dependencies
```

🔌 API Request / Response Examples

1. Register (POST /users/)
```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/users/' \
  -H 'Content-Type: application/json' \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "user",
  "created_at": "2026-08-08T00:00:00.000Z"
}
```

2. Login (POST /login) — form-encoded, OAuth2 password flow
```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=yourpassword'
```
  Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```
Wrong credentials → 403 Forbidden. More than 5 requests/minute from the same IP → 429 Too Many Requests.

3. Create Product (admin only)
```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/products/' \
  -H 'Authorization: Bearer <admin_jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"name": "Desk Lamp", "description": "Adjustable LED lamp", "price": 24.99}'
```
Non-admin token → 403 Forbidden: "Admins only".

4. Toggle Wishlist Item
```bash
curl -X POST 'https://storefront-api-1sqc.onrender.com/wishlist/' \
  -H 'Authorization: Bearer <jwt_token>' \
  -H 'Content-Type: application/json' \
  -d '{"product_id": 1, "dir": 1}'
```
Response: {"message": "Successfully added to wishlist"}. dir=0 removes it; adding a duplicate returns 409 Conflict.

```
🏛️ Design Decisions & Trade-Offs

RBAC via a dependency, not a decorator or middleware. require_admin wraps get_current_user and is attached per-route with dependencies=[Depends(require_admin)]. This keeps admin-only routes explicit and readable (you can see the restriction right in the route signature) rather than relying on a global rule that's easy to lose track of.

Wishlist uses a composite primary key instead of an auto-increment ID + unique constraint. (user_id, product_id) as the primary key means "duplicate wishlist entry" is structurally impossible at the database level, not just checked in application code — one less place for a bug to hide.

Role is embedded in the JWT at login time. create_access_token bakes role into the token payload, so require_admin doesn't need a DB lookup beyond fetching the user. The trade-off: if a user's role changes after a token is issued (e.g., an admin gets demoted), that token keeps the old role until it expires — role changes aren't revoked immediately. A production system handling this would need short-lived tokens plus refresh, or a DB check on every request instead of trusting the token claim.

Dual-mode database config. config.py supports both individual local Postgres env vars and a single DATABASE_URL (with postgres:// → postgresql:// normalization for Heroku-style URLs), so the same codebase runs unmodified in local Docker Compose and on a managed Postgres host.
```

```
⚠️ Known Issues

Being transparent about current gaps rather than hiding them:

- JWT secret is currently hardcoded in oauth2.py rather than read from config.py/.env — the SECRET_KEY environment variable is defined but not yet wired in.

 - /health reports "status": "ok" even when the database ping fails (only the nested "database" field flips to "error") — a monitoring system polling this endpoint would not currently catch a DB outage.

- get_current_user can raise an unhandled error instead of a clean 401 if a valid token references a user that no longer exists in the database.

- Rate limiting currently applies only to /login (5 requests/minute per IP) — product and wishlist routes are not yet rate-limited.
```

🚀 Getting Started Locally
Prerequisites
Docker & Docker Compose
Git

1. Clone the Repository
```bash
git clone https://github.com/fastlearner111/storefront_api.git
cd storefront_api
```

2. Create a .env File
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

3. Start the Docker Stack
```bash
docker compose up --build

API available at http://localhost:8000 and http://localhost:8000/docs.

4. Apply Database Migrations
```bash
docker compose exec api alembic upgrade head
```

🧪 Running Tests
```bash
docker compose exec api pytest -v --cov=app
```

```

🔮 Future Improvements
1. Fix the hardcoded JWT secret to read from settings.secret_key.

2. Fix /health to return a non-200 status and "status": "error" when the DB ping fails.

3. Expand rate limiting to product and wishlist write endpoints, not just login.

4.Immediate role revocation — re-check role against the database instead of trusting the JWT claim, or move to short-lived tokens with refresh.

5. Order/checkout flow — currently the API covers catalog + wishlist, not purchasing.

6. Pagination on the wishlist endpoint to match the product listing.
```