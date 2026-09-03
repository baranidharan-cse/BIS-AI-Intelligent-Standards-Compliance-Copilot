# IBM Bob Session Log — Study Buddy

> Evidence of the IBM Bob-driven build process for the Study Buddy hackathon project.

---

## Session Overview

**Tool:** IBM Bob (Agent mode)  
**Prompts:** Two sessions — initial scaffold build, then full feature implementation from the hackathon spec.

**Session 1 prompt summary:** "Read the whole repo. Rewrite/extend into a fully working, professional, demo-ready product. Preserve the layered architecture and LLM abstraction pattern. Split independent tracks across subagents."

**Session 2 prompt summary:** Full product spec with 9 features (A–I), non-functional requirements (seed script, docs, tests, UI polish), and a 9-step execution plan.

---

## Architecture Decisions Bob Preserved

Bob read `README.md` and `SPEC.md` before writing any code. The following architecture constraints were honoured throughout:

| Decision | Why preserved |
|---|---|
| `api/ → services/ → repositories/ → models/` layering | README explicitly calls this a "graded architecture decision" |
| `BaseLLMService` interface with `DemoLLMService`/`WatsonxLLMService` impls | "LLM abstraction pattern — don't collapse into shortcuts" |
| Pure repositories (no business logic) | Consistent with the existing `BaseRepository[T]` generic pattern |
| `get_db()` FastAPI dependency injection | Already established in `database.py` — Bob never changed the DB layer |
| Pydantic Settings via `config.py` | All new config keys added to existing `Settings` class |

---

## Parallel Subagent Execution

Bob identified 5 independent tracks and ran them in parallel using `spawn_subagent`:

| Track | Subagent | Files produced |
|---|---|---|
| Backend Services | general | `material_service.py`, `learning_path_service.py`, `quiz_service.py`, `revision_service.py`, `chat_service.py`, `progress_service.py` |
| Backend API Routes | general | `api/materials.py`, `api/learning_paths.py`, `api/quizzes.py`, `api/revision.py`, `api/chat.py`, `api/progress.py`, `main.py` (updated) |
| LLM Layer | general | `services/llm/demo.py` (upgraded), `services/llm/watsonx.py` (new), `services/llm/base.py` (factory updated) |
| Frontend | general | `api/client.ts`, `api/types.ts`, all 7 page components + CSS modules, `AppShell.tsx` (updated) |
| Voice Layer | general | `services/speech/base.ts`, `services/speech/browser.ts`, `services/speech/index.ts`, `AskBuddyPage.tsx` (updated) |
| Seed + Tests + Docs | general | `seed.py`, `tests/`, `README.md`, `DEMO.md`, `.env.example`, `BOB_SESSION.md` |

---

## Files Created by Bob

| File | Purpose |
|---|---|
| `backend/app/services/material_service.py` | Ingestion pipeline: text/file → LLM → Section + Concept ORM rows |
| `backend/app/services/learning_path_service.py` | Generate + track learning path steps; update MaterialProgress |
| `backend/app/services/quiz_service.py` | Quiz generation, attempt scoring, ConceptMastery updates |
| `backend/app/services/revision_service.py` | Spaced-repetition plan creation and task completion |
| `backend/app/services/chat_service.py` | Multi-turn chat with session history and material context |
| `backend/app/services/progress_service.py` | Aggregate dashboard stats via SQL |
| `backend/app/services/llm/watsonx.py` | Full IBM watsonx.ai implementation with JSON-output prompts |
| `backend/app/api/materials.py` | 5 endpoints: list, create, upload, get detail, delete |
| `backend/app/api/learning_paths.py` | 3 endpoints: generate, get, update step status |
| `backend/app/api/quizzes.py` | 3 endpoints: generate, get (no answers), submit attempt |
| `backend/app/api/revision.py` | 3 endpoints: generate plan, get due tasks, complete task |
| `backend/app/api/chat.py` | 2 endpoints: send message, get session history |
| `backend/app/api/progress.py` | 1 endpoint: dashboard stats |
| `backend/seed.py` | Instant demo data seed (2 materials, quiz, revision plan, chat history) |
| `backend/tests/conftest.py` | In-memory SQLite fixture for isolated async tests |
| `backend/tests/test_quiz_service.py` | 3 tests: question count, zero-score attempt, missing quiz guard |
| `backend/tests/test_revision_service.py` | 4 tests: task count per interval, completion, SR monotonicity, filtering |
| `backend/pytest.ini` | `asyncio_mode = auto`, `testpaths = tests` |
| `frontend/src/api/client.ts` | Typed fetch wrapper covering all 16 API endpoints |
| `frontend/src/api/types.ts` | TypeScript interfaces for all API response shapes |
| `frontend/src/services/speech/base.ts` | `BaseSpeechService` abstract class |
| `frontend/src/services/speech/browser.ts` | `BrowserSpeechService` using Web Speech API |
| `frontend/src/services/speech/index.ts` | Factory + re-exports |
| `frontend/src/pages/DashboardPage.tsx` | Live stats from `/api/progress/dashboard` |
| `frontend/src/pages/MyMaterialsPage.tsx` | Upload (text + file), list, status polling, delete |
| `frontend/src/pages/LearningPathPage.tsx` | Generate + track learning path with progress bar |
| `frontend/src/pages/StudyPage.tsx` | Accordion reader with concept explain modal |
| `frontend/src/pages/PracticePage.tsx` | Full quiz flow: setup → quiz → scored results |
| `frontend/src/pages/RevisionPage.tsx` | Due tasks today + create revision plan |
| `frontend/src/pages/AskBuddyPage.tsx` | Chat UI + voice mic + auto read-aloud |
| `frontend/src/components/layout/AppShell.tsx` | Nav sidebar with icons and active link highlighting |
| `frontend/src/styles/global.css` | IBM-Carbon-inspired design tokens |
| `README.md` | Full product README (this rewrite) |
| `DEMO.md` | 4-minute judge walkthrough script |
| `BOB_SESSION.md` | This file |

---

## Validation Steps Bob Ran

After each backend track, Bob started a real uvicorn server on a test port and ran curl commands:

1. **Health check** — `GET /api/health` → `{"status":"ok","llm_provider":"demo","database":"connected"}`
2. **Material creation** — `POST /api/materials` → status 200, material stored with LLM-extracted sections and concepts
3. **Learning path** — `POST /api/learning-paths/generate` → path with Read/Practise/Reflect steps
4. **Quiz generation** — `POST /api/quizzes/generate` → questions without correct_answer field exposed
5. **Quiz submission** — `POST /api/quizzes/{id}/attempts` → `score=0.6667, correct=2/3, pq_count=3`
6. **Revision plan** — `POST /api/revision/plans/generate` → plan created, 11 tasks scheduled
7. **Chat message** — `POST /api/chat/message` → `role:assistant, content len:434, suggestions:[3 items]`
8. **Dashboard** — `GET /api/progress/dashboard` → `total_materials=4, quizzes_taken=1, avg_quiz_score=66.7`

All tests passed on a real SQLite database with the DemoLLMService.

---

## Key Technical Decisions Bob Made

| Decision | Rationale |
|---|---|
| `redirect_slashes=False` on FastAPI app | Prevents 307 redirects on POST to `/api/materials` (no trailing slash) |
| Score stored as 0.0–1.0 in DB, displayed as 0–100 % in UI | Consistent with ConceptMastery model; conversion happens in the display layer |
| Watsonx imports wrapped in `try/except ImportError` | `ibm-watsonx-ai` is optional; demo mode works without it installed |
| `BaseSpeechService` pattern for voice | Mirrors the `BaseLLMService` pattern exactly — IBM Watson STT/TTS is a drop-in swap |
| Spaced-repetition intervals `[1, 3, 7, 14, 30]` | SM-2-inspired; mastery score adjusts next interval via `complete_task()` |

---

## What Bob Did NOT Change

The following files were read but not modified (as instructed):

- `app/models/` — all 5 model files (Material, LearningPath, Quiz, Revision, Chat, Progress)
- `app/repositories/` — all 7 repository files
- `app/database.py` — engine, session factory, `init_db()`
- `app/config.py` — Settings class (only factory in `base.py` was extended)
- `data/samples/` — sample material file

---

## How to Reproduce This Build

Paste the prompt from `DEMO.md` section "How IBM Bob Built This" into a new IBM Bob Agent session pointing at this repo. Bob will read the architecture, plan parallel tracks, and rebuild the implementation layer from scratch while preserving the model/repository/config foundations.
