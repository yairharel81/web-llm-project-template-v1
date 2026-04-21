# CLAUDE.md — LLM Navigation Guide

This is a full-stack web application template. Use this file to know exactly which file to touch for each type of change.

## Stack
- **Backend:** FastAPI + PostgreSQL (SQLAlchemy/Alembic) + Redis + Python 3.11+
- **Frontend:** React 19 + TypeScript + Vite + Tailwind CSS + React Router
- **Auth:** Email/password + Google OAuth + JWT
- **Real-time:** Redis pub/sub → Server-Sent Events (SSE)
- **AI:** Google Gemini (mock/real pattern)
- **Email:** Brevo (mock/real pattern)
- **Storage:** Google Cloud Storage (mock/real pattern)
- **Database (real-time):** Firestore (mock/real pattern)

---

## Where to make changes

### Add a new API endpoint
1. Create or edit a route file in `backend/app/api/v1/`
2. Register the router in `backend/app/api/v1/router.py`
3. Add the corresponding API call in `frontend/src/api/`

### Add a new database table
1. Create a model in `backend/app/models/` (SQLAlchemy ORM)
2. Import it in `backend/alembic/env.py` so Alembic detects it
3. Run: `alembic revision --autogenerate -m "add_table"` then `alembic upgrade head`

> **Enums:** If your model uses a Python `enum.Enum` column, Alembic will auto-generate a `CREATE TYPE` statement in Postgres. This is handled automatically — no extra steps needed.

### Add a new Pydantic schema (request/response shape)
- Edit `backend/app/models/schemas.py`
- Group schemas by domain with a `# ── Domain ──` comment header (see existing file for pattern)
- Keep request schemas (`*Create`, `*Update`) and response schemas (`*Out`) in the same section

### Change auth behavior
- JWT logic: `backend/app/services/auth_service.py`
- Auth routes (register/login/OAuth): `backend/app/api/v1/auth.py`
- Frontend auth state: `frontend/src/services/authContext.tsx`
- Frontend auth API calls: `frontend/src/api/auth.ts`

### Send an email
- Call `get_email_service()` from `backend/app/core/email.py`
- Add new templates as functions at the bottom of that file
- Set `USE_MOCK_EMAIL=false` + `BREVO_API_KEY` in `.env` for production

### Publish a real-time event to a user
```python
from app.services.event_manager import publish
from app.models.schemas import SSEEvent

await publish(user_id, SSEEvent(type="my_event", data={"key": "value"}))
```

### Handle a real-time event on the frontend
Use `useSSEEvent` from `sseContext` — it subscribes to a specific event type via the single shared SSE connection that `SSEProvider` (in `App.tsx`) manages:

```tsx
import { useSSEEvent } from "../services/sseContext";

function MyPage() {
  useSSEEvent("my_event", (event) => {
    const { key } = event.data as { key: string };
    // update state, show notification, etc.
  });
}
```

**Do NOT call `useSSE()` inside pages** — it opens a second EventSource connection. `useSSE` is a low-level escape hatch for non-authenticated contexts only.

**SSE auth note:** `EventSource` cannot set custom headers, so the JWT is passed as `?token=TOKEN` in the query string. The backend `/events/stream` reads it from there — this is already wired up in `sseContext.tsx` and `events.py`.

### Add a new AI capability
- Add a method to `GeminiService` protocol + both `MockGeminiService` and `RealGeminiService` in `backend/app/core/gemini.py`
- Call via `get_gemini_service()` in any service or route

### Store/retrieve files
- Call `get_storage_service()` from `backend/app/core/storage.py`
- Set `USE_MOCK_STORAGE=false` + GCS env vars for production

### Use Firestore (real-time document store)
- Call `get_firestore_service()` from `backend/app/core/firestore.py`
- Set `USE_MOCK_FIRESTORE=false` + Firestore env vars for production

### Add a new frontend page
1. Create a component in `frontend/src/pages/`
2. Add a `<Route>` in `frontend/src/App.tsx`

### Change environment variables
- Backend: `backend/app/core/config.py` (Pydantic Settings)
- Add to `.env.example` with documentation
- Frontend: prefix with `VITE_` and access via `import.meta.env.VITE_*`

---

## Mock/Real pattern
Every external service has a mock for local development:

| Service | Toggle env var | Mock behavior |
|---|---|---|
| Gemini | `USE_MOCK_GEMINI` | Returns echo responses |
| Email | `USE_MOCK_EMAIL` | Logs to console |
| Storage | `USE_MOCK_STORAGE` | Writes to `local_storage/` |
| Firestore | `USE_MOCK_FIRESTORE` | In-memory dict |

Set all to `true` for local dev (default in `.env.example`).

---

## Testing (Playwright)

The baseline E2E suite lives in `tests/e2e/` and covers auth (register, login, wrong password, protected route, logout).

```bash
# First time only — install browsers
cd tests/e2e && npm install && npx playwright install chromium

# Run tests (requires both servers to be running first)
npx playwright test

# Debug a failing test visually
npx playwright test --headed
npx playwright show-trace test-results/<test-folder>/trace.zip
```

**Adding tests for a new feature:**
- Create `tests/e2e/tests/<feature>.spec.ts` — do not modify `auth.spec.ts`
- Use `page.goto("/login")` + fill credentials to log in before each test
- Name your SSE event types and assert toast notifications appear with `toBeVisible()`

---

## Running locally
```bash
# 1. Start infrastructure
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp ../.env.example .env
alembic upgrade head
uvicorn app.main:app --reload

# 3. Frontend
cd frontend
npm install
npm run dev
```
