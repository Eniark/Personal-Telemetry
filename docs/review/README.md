# Personal-Telemetry — Code Review

Commit reviewed: `6bfce47` (2026-11-08). Paths are relative to `telemetry-app/` unless noted.

## How to read this

| File | Covers |
|---|---|
| [00-critical-bugs.md](00-critical-bugs.md) | Verified bugs that break data or startup. Fix these first. |
| [shared-and-infra.md](shared-and-infra.md) | `shared/`, logging, tracing, `requirements.txt`, `startup.bat`, `.env.example`, `.gitignore` |
| [server-api.md](server-api.md) | `server/api/*` |
| [server-processing.md](server-processing.md) | `server/processing_layer/*` |
| [server-db.md](server-db.md) | `server/db/*`, SQL queries |
| [server-classifier.md](server-classifier.md) | `event_classifier/backend/*`, training notebook, `.joblib` |
| [server-frontend.md](server-frontend.md) | PySide6 panel, tables, tray icon |
| [agent-windows.md](agent-windows.md) | `agents/windows/*` |
| [agent-browser.md](agent-browser.md) | Chrome extension |
| [agent-android.md](agent-android.md) | Android app |
| [best-practices.md](best-practices.md) | Cross-cutting practices: what, how, when to apply |
| [additional-comments.md](additional-comments.md) | Senior-level critique: architecture, data/ML, code quality, deps, security, process |
| [roast.md](roast.md) | The same findings, with no mercy |

Labels used in every file:

- **[Bug]** — wrong behavior today, verified by reading or running the code.
- **[Risk]** — works now, breaks under a realistic condition (restart, outage, new install).
- **[Improve]** — style, structure, maintainability.

## Scores

Scores are out of 10 and judge the code for what it is: a personal, single-user, LAN-only project. They are not enterprise standards.

| Area | Score | One-line reason |
|---|---|---|
| Architecture / idea | **8** | Clear agent → API → classifier → review-UI loop. Durable queue on the Windows agent is a good call. |
| Server API | **6** | Small and readable; blocking DB calls inside `async` endpoints, no idempotency. |
| Processing layer | **5** | Works for the happy path; type annotations don't match the data, error path crashes. |
| Database | **3** | Fresh install fails (`CREATE TABLE` errors, missing column). No migrations, broken FK. |
| Classifier | **5** | Sensible sklearn pipeline; feature order swapped at inference, model trains on its own predictions. |
| Desktop UI | **6** | Clean split into small widgets; signal leak on refresh, drag detection broken. |
| Windows agent | **6** | Good durable queue + backoff; relies on globals, no request timeout, no dedup. |
| Browser extension | **5** | Simple and readable; loses the last tab on focus loss, MV3 lifecycle not handled. |
| Android app | **6** | Good MVVM/Room/WorkManager structure; payload rejected by server on nulls, duplicate sends. |
| Tooling (deps, tests, scripts) | **3** | `startup.bat` points to modules that don't exist, missing deps, no tests. |
| **Overall** | **5.5** | Solid design and learning trajectory; data correctness needs a pass before the dataset grows. |

## Top 10 actions (in order)

1. Fix the DB schema: generated column names + add `model_confidence` (see critical bugs #1, #2).
2. Fix swapped executable/publisher features in `event_feature_extractor.py` (critical #3).
3. Make `PhoneEventSchema` fields nullable to match Android (critical #4).
4. Fix `startup.bat` module paths (critical #5).
5. Train only on user-approved labels (critical #6).
6. Make ingestion idempotent: send the client-generated `id` and use it as a unique key on the server.
7. Add the missing dependencies to `requirements.txt` and split runtime vs dev.
8. Replace "run on import" modules (`init_db`, `tracing`, `tray_icon`) with explicit `init()` calls.
9. Add a `timeout=` to every HTTP call (`requests.post` in the Windows agent).
10. Add a handful of tests for the pure functions (feature extractor, event mapping, filter). See `best-practices.md`.

## What is already good

- Layered server: API → processor → repository → SQL constants. Easy to follow.
- Windows agent stores events in a local SQLite queue before sending and uses exponential backoff — the right pattern for an unreliable link.
- OpenTelemetry tracing with trace IDs in log lines — uncommon in a personal project and useful.
- Android uses Room + WorkManager + ViewModel factory correctly; comments show the reasoning.
- The notebook compares several models with grid search and stratified split instead of picking one blindly.
- Small, focused frontend classes (`DraggableButton`, `TelemetryPanel`, `Column` dataclass).
