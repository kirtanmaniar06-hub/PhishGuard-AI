# PhishGuard AI — Backend

Enterprise-grade FastAPI backend for the PhishGuard AI platform.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT (access + refresh tokens) |
| Hashing | bcrypt via passlib |
| Validation | Pydantic v2 |
| Config | pydantic-settings + .env |
| Logging | Loguru |

## Folder Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/   # Route handlers
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings
│   │   └── logging.py       # Loguru configuration
│   ├── database/
│   │   ├── base.py          # Declarative base
│   │   └── session.py       # Async engine + session
│   ├── middleware/          # CORS, logging middleware
│   ├── models/              # SQLAlchemy ORM models
│   ├── routers/             # Central router registry
│   ├── schemas/             # Pydantic request/response schemas
│   ├── security/            # JWT encode/decode logic
│   ├── services/            # Business logic layer
│   └── utils/               # Shared helpers (hashing, etc.)
├── alembic/                 # Database migration scripts
├── tests/                   # Pytest test suite
├── .env.example             # Environment variable template
├── alembic.ini
└── requirements.txt
```

## Quickstart

```bash
# 1. Clone & enter backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret keys

# 5. Run database migrations
alembic upgrade head

# 6. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Authentication Flow

```
POST /api/v1/auth/register   → Create account
POST /api/v1/auth/login      → Returns access_token + refresh_token
POST /api/v1/auth/refresh    → Exchange refresh_token for new access_token
POST /api/v1/auth/logout     → Invalidate refresh token
GET  /api/v1/users/me        → Protected: current user profile
GET  /api/v1/users/          → Admin only: list all users
```

## Roles

| Role | Access |
|---|---|
| `user` | Own profile, phishing scans |
| `admin` | All users, system settings, reports |
