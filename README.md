# web-llm-project-template-v1

A full-stack web application template designed for LLM-assisted development. Clone this to get auth, database, real-time notifications, AI chat, file storage, and email working from day one.

---

## Building Blocks

| Block | Status | Key files | Required env vars |
|---|---|---|---|
| **PostgreSQL + SQLAlchemy** | ✅ included | `backend/app/core/database.py`, `backend/app/models/` | `DATABASE_URL` |
| **Alembic Migrations** | ✅ included | `backend/alembic/` | — |
| **Email/Password Auth + JWT** | ✅ included | `backend/app/api/v1/auth.py`, `backend/app/services/auth_service.py` | `SECRET_KEY` |
| **Google OAuth** | ✅ included | `backend/app/core/google_oauth.py` | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| **Redis + SSE (real-time)** | ✅ included | `backend/app/services/event_manager.py`, `backend/app/api/v1/events.py` | `REDIS_URL` |
| **Gemini AI (chat + streaming)** | ✅ included | `backend/app/core/gemini.py`, `backend/app/api/v1/chat.py` | `GEMINI_API_KEY` |
| **Brevo Email** | ✅ included | `backend/app/core/email.py` | `BREVO_API_KEY` |
| **Google Cloud Storage** | ✅ included | `backend/app/core/storage.py` | `GCS_BUCKET_NAME`, `GCS_PROJECT_ID` |
| **Firestore** | ✅ included | `backend/app/core/firestore.py` | `FIRESTORE_PROJECT_ID` |
| **React 19 + Vite + Tailwind** | ✅ included | `frontend/` | — |
| **Auth UI (login + register)** | ✅ included | `frontend/src/components/auth/` | — |
| **Auth Context + useAuth hook** | ✅ included | `frontend/src/services/authContext.tsx` | — |
| **SSE client hook (useSSE)** | ✅ included | `frontend/src/hooks/useSSE.ts` | — |
| **Chat UI + useChat hook** | ✅ included | `frontend/src/components/chat/`, `frontend/src/hooks/useChat.ts` | — |
| **Dashboard shell** | ✅ included | `frontend/src/components/dashboard/DashboardShell.tsx` | — |

---

## I only need a subset — what to remove

| Skip this block | Delete these files | Remove from |
|---|---|---|
| **Google OAuth** | `backend/app/core/google_oauth.py` | Auth routes in `auth.py`, env vars |
| **SSE / Redis** | `backend/app/services/event_manager.py`, `backend/app/api/v1/events.py` | `router.py`, `docker-compose.yml`, `useSSE.ts` |
| **Gemini AI** | `backend/app/core/gemini.py`, `backend/app/api/v1/chat.py` | `router.py`, `useChat.ts`, `ChatComponent.tsx` |
| **Brevo Email** | `backend/app/core/email.py` | Any service that calls `get_email_service()` |
| **Google Cloud Storage** | `backend/app/core/storage.py` | Any service that calls `get_storage_service()` |
| **Firestore** | `backend/app/core/firestore.py` | Any service that calls `get_firestore_service()` |

---

## Architecture

```
Browser
  │
  ├── GET /api/v1/events/stream  ─── SSE (real-time events)
  ├── POST /api/v1/auth/*        ─── Auth (login, register, OAuth)
  ├── POST /api/v1/chat/stream   ─── Gemini streaming
  └── GET /api/v1/users/me       ─── User profile

FastAPI Backend
  ├── PostgreSQL   ── users, app data (SQLAlchemy + Alembic)
  ├── Redis        ── pub/sub channel for SSE events
  ├── Gemini       ── AI chat (mock/real)
  ├── Brevo        ── transactional email (mock/real)
  ├── GCS          ── file storage (mock/real)
  └── Firestore    ── real-time document store (mock/real)
```

---

## Mock / Real pattern

Every external service defaults to a mock in development — no cloud credentials needed to run locally.

```
USE_MOCK_GEMINI=true     → logs echo responses to console
USE_MOCK_EMAIL=true      → logs emails to console (no Brevo account needed)
USE_MOCK_STORAGE=true    → writes files to local_storage/ directory
USE_MOCK_FIRESTORE=true  → uses an in-memory Python dict
```

Switch to `false` + provide the real credentials to use production services.

---

## Quick start

```bash
# 1. Clone and enter project
git clone <repo-url> my-app && cd my-app

# 2. Start infrastructure (Postgres + Redis)
docker compose up -d

# 3. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp ../.env.example .env   # edit with your values
alembic upgrade head
uvicorn app.main:app --reload
# → http://localhost:8000

# 4. Frontend (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Project structure

```
web-llm-project-template-v1/
├── README.md
├── CLAUDE.md               ← LLM navigation guide (which file to touch for what)
├── .env.example            ← all env vars documented
├── docker-compose.yml      ← Postgres + Redis
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/
│   │   └── env.py
│   └── app/
│       ├── main.py                    ← FastAPI app, CORS, lifespan
│       ├── core/
│       │   ├── config.py              ← all settings (Pydantic Settings)
│       │   ├── database.py            ← SQLAlchemy engine + get_db()
│       │   ├── redis.py               ← Redis connection
│       │   ├── gemini.py              ← Gemini service (mock/real)
│       │   ├── email.py               ← Brevo email service (mock/real)
│       │   ├── storage.py             ← GCS file storage (mock/real)
│       │   ├── firestore.py           ← Firestore service (mock/real)
│       │   └── google_oauth.py        ← Google OAuth helpers
│       ├── models/
│       │   ├── user.py                ← User SQLAlchemy ORM model
│       │   └── schemas.py             ← Pydantic request/response schemas
│       ├── services/
│       │   ├── auth_service.py        ← JWT, password hashing, user queries
│       │   └── event_manager.py       ← Redis pub/sub → SSE bridge
│       └── api/v1/
│           ├── router.py              ← mounts all routers
│           ├── deps.py                ← FastAPI dependencies (get_current_user)
│           ├── auth.py                ← /auth/* routes
│           ├── users.py               ← /users/* routes
│           ├── events.py              ← /events/stream SSE endpoint
│           └── chat.py                ← /chat/* Gemini endpoints
│
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx                    ← routes + ProtectedRoute
        ├── main.tsx
        ├── index.css
        ├── types/index.ts             ← shared TypeScript types
        ├── api/
        │   ├── client.ts              ← Axios instance + auth interceptors
        │   ├── auth.ts                ← auth API calls
        │   └── chat.ts                ← chat API calls (streaming + non-streaming)
        ├── services/
        │   └── authContext.tsx        ← AuthProvider + useAuth hook
        ├── hooks/
        │   ├── useSSE.ts              ← SSE subscription hook
        │   └── useChat.ts             ← chat state hook
        ├── components/
        │   ├── auth/
        │   │   ├── LoginPage.tsx
        │   │   └── RegisterPage.tsx
        │   ├── chat/
        │   │   └── ChatComponent.tsx
        │   └── dashboard/
        │       └── DashboardShell.tsx ← layout + SSE listener
        └── pages/
            └── Dashboard.tsx
```

---

## Tech stack

| Layer | Tech |
|---|---|
| Backend framework | FastAPI 0.115+ |
| Database | PostgreSQL 16 + SQLAlchemy 2 (async) + Alembic |
| Real-time | Redis 7 pub/sub → SSE |
| AI | Google Gemini 1.5 Flash |
| Auth | JWT (python-jose) + bcrypt + Google OAuth 2.0 |
| Email | Brevo (transactional) |
| File storage | Google Cloud Storage |
| Document store | Google Firestore |
| Frontend | React 19 + TypeScript + Vite + Tailwind CSS |
| HTTP client | Axios |
| Routing | React Router v7 |
