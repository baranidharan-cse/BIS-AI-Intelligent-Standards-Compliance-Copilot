# Study Buddy 🎓

An AI-powered study assistant that ingests your documents, generates structured
learning paths, quizzes, explanations, and revision schedules — all powered by
an LLM backend (IBM watsonx.ai or demo mode).

> **Session 1 — Foundation Layer only.**
> Feature pages are placeholder shells. Ingestion, quiz, explain, revision,
> and chatbot are implemented in subsequent sessions.

---

## Architecture Overview

```
study-buddy/
├── backend/          FastAPI (Python 3.12)
│   └── app/
│       ├── api/          HTTP route handlers (thin, delegate to services)
│       ├── models/       SQLAlchemy ORM models (no business logic)
│       ├── repositories/ Data-access layer (no business logic)
│       ├── services/     Business logic + LLM abstraction
│       │   └── llm/      BaseLLMService · DemoLLMService · (WatsonxLLMService TODO)
│       ├── config.py     Pydantic Settings — all env vars in one place
│       ├── database.py   Async SQLAlchemy engine, session factory, init_db()
│       └── main.py       FastAPI app factory + lifespan
├── frontend/         React 18 + TypeScript + Vite
│   └── src/
│       ├── components/
│       │   ├── common/   Shared UI components (PlaceholderPage, etc.)
│       │   └── layout/   AppShell (sidebar navigation)
│       ├── pages/        One file per nav item (9 pages)
│       ├── styles/       Global CSS
│       └── App.tsx       React Router routing tree
└── data/
    └── samples/      Sample study documents for ingestion
```

**Key design principles:**
- Repositories have **zero** business logic — only data access.
- Services own all business rules and orchestrate LLM calls.
- The LLM layer is fully abstracted: swap `demo` → `watsonx` by changing one env var.
- `DATABASE_URL` is the only change needed to move from SQLite → Postgres.

---

## Folder Structure

```
study-buddy/
├── SPEC.md                          Product spec (replace placeholder with real spec)
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── health.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── material.py          Material · Section · Concept
│       │   ├── learning_path.py     LearningPath · LearningStep
│       │   ├── quiz.py              Quiz · QuizQuestion · QuizAttempt
│       │   ├── revision.py          RevisionPlan · RevisionTask
│       │   ├── chat.py              ChatMessage
│       │   └── progress.py          ConceptMastery · MaterialProgress
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── base.py              Generic CRUD BaseRepository[T]
│       │   ├── material_repository.py
│       │   ├── learning_path_repository.py
│       │   ├── quiz_repository.py
│       │   ├── revision_repository.py
│       │   ├── chat_repository.py
│       │   └── progress_repository.py
│       └── services/
│           └── llm/
│               ├── __init__.py
│               ├── base.py          BaseLLMService (ABC) + get_llm_service() factory
│               └── demo.py          DemoLLMService — deterministic sample responses
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx                  React Router tree
│       ├── styles/
│       │   └── global.css
│       ├── components/
│       │   ├── common/
│       │   │   ├── PlaceholderPage.tsx
│       │   │   └── PlaceholderPage.module.css
│       │   └── layout/
│       │       ├── AppShell.tsx
│       │       └── AppShell.module.css
│       └── pages/
│           ├── DashboardPage.tsx    (skeleton with stat cards)
│           ├── MyMaterialsPage.tsx  (placeholder — Session 2)
│           ├── LearningPathPage.tsx (placeholder — Session 3)
│           ├── StudyPage.tsx        (placeholder — Session 4)
│           ├── PracticePage.tsx     (placeholder — Session 5)
│           ├── RevisionPage.tsx     (placeholder — Session 6)
│           ├── AskBuddyPage.tsx     (placeholder — Session 7)
│           ├── SettingsPage.tsx     (placeholder)
│           └── ProfilePage.tsx      (placeholder)
└── data/
    └── samples/
        └── python_programming_fundamentals.txt
```

---

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+
- (Optional) `python-venv` or `conda`

### Backend

```bash
cd study-buddy/backend

# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env if needed — defaults work for local dev with demo LLM provider

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd study-buddy/frontend

# 1. Install dependencies
npm install

# 2. Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.
All `/api/*` requests are proxied to the backend automatically.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Study Buddy` | Application display name |
| `DEBUG` | `false` | Enable SQLAlchemy query logging |
| `DATABASE_URL` | `sqlite+aiosqlite:///./study_buddy.db` | Database connection string |
| `LLM_PROVIDER` | `demo` | `demo` or `watsonx` |
| `WATSONX_API_KEY` | _(empty)_ | IBM Cloud API key — required for watsonx |
| `WATSONX_PROJECT_ID` | _(empty)_ | watsonx project ID |
| `WATSONX_URL` | `https://us-south.ml.cloud.ibm.com` | watsonx regional endpoint |
| `WATSONX_MODEL_ID` | `ibm/granite-13b-instruct-v2` | Foundation model to use |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS-allowed frontend origin |

See [`backend/.env.example`](backend/.env.example) for the full reference with comments.

---

## Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected response (demo mode, DB connected):**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.000000+00:00",
  "version": "0.1.0",
  "llm_provider": "demo",
  "database": "connected"
}
```

---

## Implemented vs. Deferred

### ✅ Implemented (Session 1)

| Layer | What's built |
|---|---|
| Project structure | Full folder layout, all packages, `__init__` files |
| Config | `Settings` via Pydantic Settings, `.env.example`, `get_settings()` |
| Database | Async SQLAlchemy engine, session factory, `init_db()`, `get_db()` |
| Models | All 12 ORM models across 6 files |
| Repositories | `BaseRepository[T]` + 7 concrete repositories, all with domain-specific queries |
| LLM abstraction | `BaseLLMService` (ABC) with 5 method signatures + typed DTOs |
| DemoLLMService | Fully implemented with realistic shaped responses for all 5 methods |
| WatsonxLLMService | `TODO` marker with full constructor signature documented |
| LLM factory | `get_llm_service()` wires provider from env var |
| Health endpoint | `GET /api/health` — DB ping + provider info |
| Sample data | Python Programming Fundamentals text (7 topics, 253 lines) |
| Frontend shell | React Router, AppShell sidebar, 9 placeholder pages |
| README | This file |

### 🔜 Deferred (future sessions)

| Feature | Session | Notes |
|---|---|---|
| Ingestion pipeline | Session 2 | PDF/text/URL → sections → concepts via LLM |
| Learning Path generator | Session 3 | Calls `generate_learning_path()` |
| Explain Engine | Session 4 | Calls `explain_topic()`, section reader UI |
| Quiz Engine | Session 5 | Calls `generate_quiz()`, attempt tracking |
| Revision Planner | Session 6 | Spaced repetition, due-today list |
| Chatbot | Session 7 | Calls `answer_question()`, session history |
| WatsonxLLMService | Session 2+ | `ibm-watsonx-ai` SDK integration |
| Authentication | TBD | No user model yet — single-user mode assumed |
| Alembic migrations | TBD | `create_all` used now; swap when schema stabilises |

---

## Assumptions

> These decisions were made without access to the full SPEC.md. Review and
> override in the next session after adding the real spec.

1. **Single-user, no auth.** There is no `User` model. All data belongs to one
   implicit user. If SPEC.md requires multi-user, add a `User` model and FK
   relations in Session 2.

2. **SQLite for local dev, Postgres-ready.** `DATABASE_URL` uses
   `sqlite+aiosqlite://` by default. Switching to `postgresql+asyncpg://` requires
   no code changes — only the env var and installing `asyncpg`.

3. **`create_all` instead of Alembic.** Alembic migration tracking is not set up.
   `init_db()` runs `create_all` on every startup (idempotent). Add Alembic when
   the schema is stable enough to track migrations.

4. **`options` and `answers` stored as JSON text.** Quiz question options and
   attempt answers are stored as JSON strings in `Text` columns rather than
   JSONB. This works on SQLite; on Postgres, replace with `JSONB` columns for
   queryability.

5. **No file storage abstraction.** Uploaded files are saved to local disk
   (`source_path`). A future session should introduce an `StorageService`
   interface (local / S3 / COS) before the ingestion feature is built.

6. **Watsonx model default.** `WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2`
   was chosen as the default. Update to `ibm/granite-3-8b-instruct` or whichever
   model SPEC.md specifies.

7. **Frontend: no auth guards.** All routes are accessible without login.
   If authentication is required, add route guards in `App.tsx` in a later session.

8. **Frontend: no API client yet.** Pages are placeholders — no `fetch`/`axios`
   calls to the backend. A typed API client (e.g. using `openapi-fetch`) will be
   added when feature endpoints exist.

---

## API Endpoints

> ⬜ **Placeholder** — will be populated as features are built in later sessions.

| Method | Path | Description | Session |
|---|---|---|---|
| `GET` | `/api/health` | Health check | ✅ Session 1 |
| `POST` | `/api/materials` | Upload material | Session 2 |
| `GET` | `/api/materials/{id}/learning-path` | Get learning path | Session 3 |
| `GET` | `/api/concepts/{id}/explain` | Explain a concept | Session 4 |
| `POST` | `/api/materials/{id}/quiz` | Generate quiz | Session 5 |
| `GET` | `/api/revision/due-today` | Today's revision tasks | Session 6 |
| `POST` | `/api/chat` | Ask Buddy chatbot | Session 7 |

---

## Demo Mode Walkthrough

> ⬜ **Placeholder** — will be written in Session 2 once ingestion is live.

---

## Deployment Notes

> ⬜ **Placeholder** — will be written once the full feature set is implemented.

Key considerations for later:
- Switch `DATABASE_URL` to PostgreSQL in production.
- Set `LLM_PROVIDER=watsonx` and fill in watsonx credentials.
- Use a proper secret manager (IBM Secrets Manager / AWS Secrets Manager) instead of `.env`.
- Add `alembic` for database migrations.
- Set `FRONTEND_ORIGIN` to the production domain.
- Add a reverse proxy (nginx / Caddy) in front of uvicorn.
