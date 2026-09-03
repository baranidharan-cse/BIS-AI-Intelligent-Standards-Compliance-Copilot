# Study Buddy 🎓

> An AI-powered study companion — upload your material, get a personalised learning path, practise with AI-generated quizzes, stay on track with a spaced-repetition revision schedule, and ask questions to your AI tutor — all powered by **IBM watsonx.ai**.

---

## Problem

Students face three interconnected problems:

1. **Information overload** — reading alone doesn't create retention; passive study is inefficient.
2. **No personalisation** — every student gets the same textbook but learns differently.
3. **Forgotten material** — without structured review, 80 % of new knowledge is forgotten within a week (Ebbinghaus Forgetting Curve).

Study Buddy solves all three: it *structures* your material into atomic concepts, *personalises* the learning path, *tests* understanding with adaptive quizzes, and *schedules* revision at scientifically optimal intervals.

---

## Features

| Feature | Description |
|---|---|
| 📥 **Material Ingestion** | Paste text or upload `.txt` files — IBM watsonx.ai extracts sections and atomic concepts automatically |
| 🗺️ **Learning Path** | AI generates a step-by-step study roadmap (Read → Practise → Reflect) with time estimates; track progress inline |
| 📖 **Study Reader** | Browse sections and concepts with definitions and code examples in a clean accordion reader |
| ✏️ **Adaptive Quizzes** | MCQ, true/false, and short-answer questions; concept mastery scores updated after every attempt |
| 🔁 **Spaced Repetition** | Auto-scheduled revision tasks at 1 → 3 → 7 → 14 → 30-day intervals, adjusted by per-concept mastery score |
| 💬 **Ask Buddy** | Multi-turn chatbot grounded in your material; persistent session history; contextual follow-up suggestions |
| 🎤 **Voice Mode** | Speak questions, hear answers — `BaseSpeechService` abstraction ready for IBM Watson STT/TTS |
| 📊 **Dashboard** | Live stats — materials loaded, concepts mastered, quizzes taken, revision tasks due today |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                React / TypeScript UI                     │
│  Dashboard · Materials · Study · Practice · Revision ... │
│               src/api/client.ts (typed fetch)            │
└────────────────────────┬────────────────────────────────┘
                         │  REST JSON
┌────────────────────────▼────────────────────────────────┐
│              FastAPI (async)  —  app/api/                │
│  /materials · /learning-paths · /quizzes                 │
│  /revision  · /chat  · /progress                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│           Business logic  —  app/services/               │
│  MaterialService · LearningPathService · QuizService     │
│  RevisionService · ChatService · ProgressService         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │         LLM Abstraction  —  services/llm/        │   │
│  │  BaseLLMService                                  │   │
│  │    ├─ DemoLLMService     (no credentials)        │   │
│  │    └─ WatsonxLLMService  (ibm-watsonx-ai SDK)    │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│           Data access  —  app/repositories/              │
│  MaterialRepository · QuizRepository · ChatRepository …  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│        SQLAlchemy ORM models  —  app/models/             │
│  Material · Section · Concept · LearningPath             │
│  Quiz · RevisionPlan · ChatMessage · ConceptMastery …    │
│                                                          │
│        SQLite (dev)   ↔   PostgreSQL (prod)             │
└─────────────────────────────────────────────────────────┘
```

**Key design principle:** business logic never bypasses layers. Every API handler calls a service; every service calls a repository; no handler touches the DB directly.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 · TypeScript · Vite · CSS Modules |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 (async) · Pydantic v2 |
| Database | SQLite (development) · PostgreSQL-ready (swap `DATABASE_URL`) |
| AI / LLM | IBM watsonx.ai · `ibm/granite-13b-instruct-v2` via `ibm-watsonx-ai` SDK |
| Speech | Web Speech API (browser) · `BaseSpeechService` abstraction for IBM Watson STT/TTS |

---

## Why IBM watsonx.ai?

- **Enterprise-grade reliability** — watsonx.ai is IBM's production AI platform, not a hobby API. It provides the governance and SLAs needed for real educational tools.
- **Granite models are instruction-tuned** — IBM's Granite models excel at structured, JSON-output tasks like concept extraction and quiz generation — exactly what Study Buddy needs.
- **One env var to switch** — set `LLM_PROVIDER=watsonx` in `.env`; every service and API route continues to work identically because nothing knows which LLM is behind the interface.
- **Privacy-ready** — watsonx.ai supports data residency on IBM Cloud, important for student data in regulated markets.

---

## How IBM Bob Built This

Study Buddy was designed and implemented in **IBM Bob (Agent mode)**:

1. Bob read the full repo first — architecture decisions in `README.md` were respected, not overridden.
2. Bob planned a **parallel execution** across five independent tracks (services, API routes, LLM layer, frontend, voice) using its subagent capability — each track ran simultaneously.
3. Bob preserved the **layered architecture** without collapsing shortcuts — repositories stay pure data access, services own all business logic.
4. Bob implemented the **real `WatsonxLLMService`** using JSON-output prompts with `ibm-watsonx-ai` SDK, including regex fallback JSON parsing.
5. Bob wrote the **pytest test suite** for quiz scoring and spaced-repetition scheduling.
6. Bob ran **live end-to-end API tests** after each backend track — curl tests against a running uvicorn server to verify real database writes.

Full session log: [`BOB_SESSION.md`](BOB_SESSION.md)

---

## Quick Start

### Prerequisites
- Python 3.12 + pip
- Node.js 18 + npm

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit if needed — defaults work out of the box
python seed.py              # pre-load demo data (takes ~2 s, no API calls)
uvicorn app.main:app --reload
# API docs → http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

### Enable IBM watsonx.ai

```bash
# In backend/.env:
LLM_PROVIDER=watsonx
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2

pip install ibm-watsonx-ai>=1.0.0
```

### Run Tests
```bash
cd backend && pytest
```

---

## Project Structure

```
study-buddy/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers — one file per domain
│   │   ├── services/
│   │   │   └── llm/          # BaseLLMService · DemoLLMService · WatsonxLLMService
│   │   ├── repositories/     # Async SQLAlchemy data access (pure CRUD + queries)
│   │   └── models/           # SQLAlchemy ORM models
│   ├── tests/                # pytest test suite
│   ├── seed.py               # Demo data seed (no LLM calls, instant)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/              # client.ts (typed fetch) · types.ts
│       ├── components/       # AppShell layout, shared components
│       ├── pages/            # One component per route
│       └── services/speech/  # BaseSpeechService · BrowserSpeechService
├── data/samples/             # Sample study material text
├── DEMO.md                   # 4-minute judge walkthrough script
└── BOB_SESSION.md            # IBM Bob session log
```

---

## Environment Variables

See [`.env.example`](backend/.env.example) for all variables with inline documentation.

---

## Assumptions

- **Single-user** — no auth/multi-tenant; suitable for demo and personal use.
- **SQLite by default** — no database setup required; swap `DATABASE_URL` for Postgres in production.
- **`create_all` on startup** — tables are created automatically; not for production schema management (use Alembic for migrations in production).
- **Demo provider** — `LLM_PROVIDER=demo` (default) uses `DemoLLMService` which produces realistic, varied output without any API keys. The app is fully functional end-to-end in demo mode.

---

## Licence

MIT
