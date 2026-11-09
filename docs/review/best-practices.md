# Best practices — what, how, when

Only practices that solve a problem this codebase actually has. Ordered by value for effort.

| # | Practice | Fixes in this repo | When | Effort |
|---|---|---|---|---|
| 1 | Schema migrations | Bugs #1, #2, missing views | Now | ~1 h |
| 2 | Idempotent ingestion | Duplicate rows on retry (Windows, Android) | Now | ~1 h |
| 3 | One timestamp format (UTC) | 3 formats, naive local time, DST | Before more data accumulates | ~2 h |
| 4 | No side effects on import | `init_db`, `tracing`, `logger`, `tray_icon` | Before writing tests | ~1 h |
| 5 | Typed settings | Crossed env vars, `validate_env_variable` bugs | Now | 30 min |
| 6 | Shared contracts | Server/Android schema mismatch, swapped features | Next refactor | ~2 h |
| 7 | Tests for pure functions | Would have caught #3, #7, phone/OS mapping | After 4 | ~2 h |
| 8 | Linting + formatting | Unused imports, mixed quotes, bare except | Now | 15 min |
| 9 | Explicit error handling | Bare `except`, `print(e)`, silent thread death | Ongoing | — |
| 10 | Timeouts & retries on every network call | Hanging `requests.post`, lost browser events | Now | 15 min |

---

## 1. Schema migrations
**What:** every DB change is a numbered SQL file in git; the app applies missing ones at startup.
**How (no library):** `server/db/migrations/001_init.sql`, `002_….sql`. On startup read `PRAGMA user_version`, run files with a higher number in a transaction, then `PRAGMA user_version = N`. For the existing DB, write `001` as the current real schema and set `user_version = 1` by hand once.
**Android:** Room `exportSchema` + `AutoMigration` instead of `fallbackToDestructiveMigration`.
**When:** whenever the schema changes; start now because the git schema and your DB already differ.

## 2. Idempotent ingestion
**What:** sending the same event twice stores it once.
**How:** the client generates the ID (Windows already does; Android: a UUID column or `(packageName, eventStartTime)`), the server keeps it as `UNIQUE` and inserts with `ON CONFLICT(event_id) DO NOTHING`.
**When:** any time a client retries — which both of yours do.

## 3. Timestamps
**What:** store and transmit UTC; convert to local only for display.
**How:** agents send epoch milliseconds (browser and Android already do). Server stores `INTEGER` epoch ms or ISO-8601 with `Z`. Durations become plain subtraction. The UI formats with local time.
**When:** before the duration views/dashboards — DST shifts break local-time durations twice a year.

## 4. No side effects on import
**What:** importing a module defines things; it doesn't create files, open DBs or start loops.
**How:** `init_db()`, `setup_logging()`, `setup_tracing()` called from each entry point (`api.py` lifespan, `agent.py` main, `screen.py` main). Other modules use `logging.getLogger(__name__)`.
**When:** before tests; tests should be able to import any module without touching real files.

## 5. Typed settings
**What:** one object holds all configuration, validated at startup.
**How:** `pydantic-settings`:
`class Settings(BaseSettings): server_host: str = "0.0.0.0"; server_port: int = 8000; agent_port: int = 8080; ...` and `settings = Settings()` loaded from `.env`. Replace `validate_env_variable` and `LISTEN_TO_ALL_DEVICES`.
**When:** now — it removes two bugs.

## 6. Shared contracts
**What:** one definition per data shape, used by every component that speaks it.
**How:** move pydantic schemas (`OSEventSchema`, `BrowserEventSchema`) to `shared/schemas.py` and use them in the Windows agent too. For features, one `build_features()` used by both the notebook and the server. For Android, keep a short `API.md` listing each endpoint's JSON (fields, types, nullability) and keep the Kotlin DTO and pydantic model in sync with it. **Optional later:** FastAPI already serves `/openapi.json`; you can generate the Kotlin DTO from it.
**When:** at the next schema change.

## 7. Tests (start small)
**What:** `pytest` tests for pure logic — no DB, no network.
**Start with:**
- `EventFeatureExtractor`: an OS event with 5 previous events → assert `previous_event_1_executable == "<exe of first>"` (catches bug #3).
- `PhoneMapper` / `from_schema`: field mapping and timestamp conversion.
- `EventFilter`: ignored processes/URLs, case.
- `EventProcessor.add_class` with a fake classifier that raises / returns `None` (catches bug #7).
- One API test with FastAPI `TestClient` and an in-memory SQLite (`:memory:`) — needs practice 4 first. Include a phone payload with `null` description (catches bug #4).
**Android:** unit-test the session-building logic after extracting it from `Worker.doWork` (pure function: list of usage events → list of sessions). Un-ignore `src/test/` in `.gitignore` first.
**When:** whenever you fix one of the bugs above — write the test that would have caught it, then fix.

## 8. Linting & formatting
**What:** tools enforce style so reviews focus on logic.
**How:** `ruff` (lint + format) in `pyproject.toml`; enable rules `E, F, I, B, UP`. It flags: unused imports (many files), duplicate `import logging`, bare `except` (`E722`), mutable default args (`B006`), import order. Add `pre-commit` to run it on commit. JS: Prettier. Kotlin: ktlint or Android Studio's formatter.
**When:** now; 15 minutes of setup, then automatic.

## 9. Error handling rules
- Never bare `except:`; catch the specific exception or `Exception`.
- Log with `logger.exception(...)` inside `except` (keeps the traceback). No `print(e)`.
- A function annotated `-> bool` returns `True`/`False` on every path.
- Background threads (`__monitor_queue`, uvicorn thread) wrap their loop body in `try/except Exception` + log, so one bad event doesn't kill the thread silently.
- Use transactions (`with conn:`) when one logical write touches two tables.

## 10. Network calls
- Every call has a timeout (`requests.post(..., timeout=(3, 10))`).
- Every client that can't reach the server buffers locally (Windows ✅, Android ✅, browser ❌ → `chrome.storage`).
- Retries use backoff with a cap (Windows ✅) and stop on non-retryable errors (Android retries 422 forever ❌).

---

## Things deliberately **not** recommended
To keep it simple for a single-user project:
- No ORM (SQLAlchemy) — raw SQL with migrations is enough here.
- No message broker (Kafka/RabbitMQ) — the SQLite queue already does the job.
- No DI framework (Hilt, dependency-injector) — a manual container is enough.
- No Docker/Kubernetes until you deploy the server somewhere other than your PC.
- No microservice split — the monorepo layout is fine.
