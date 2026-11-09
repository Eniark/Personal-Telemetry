# Server — API (`server/api/`)

Score: **6/10**

---

## `api.py`
- **[Risk]** Lines 43, 52: endpoints are `async def`, but everything inside is blocking (sqlite, sklearn `predict_proba`). Blocking code in an `async` endpoint freezes the whole event loop, so `/health` and other requests wait.
  **How:** declare them as plain `def`. FastAPI then runs them in a thread pool. **But** then the shared sqlite connection (`check_same_thread=False`, line 34) is used from several threads. Either guard writes with a `threading.Lock`, or open a connection per request via a dependency (`Depends(get_db)`). For a single-user app, the lock is the simpler choice.
- **[Risk]** Lines 30-40: all classifiers, the DB connection and the model are created at import time. Import errors (missing model file, ollama not installed) crash startup with an unclear traceback, and tests can't import `app` without a real DB.
  **How:** move creation into a FastAPI `lifespan` function and store them on `app.state`. **When:** the moment you write the first API test.
- **[Improve]** Line 32: `LLMClassifier` is instantiated even though it's disabled. Only build what's in the list.
- **[Risk]** Line 74: `reload=True` in the production entry point. It spawns a watcher process and restarts on any file change (including writes to `logs/` inside the watched tree). Make it an env flag that defaults to `False`.
- **[Risk]** Server listens on `0.0.0.0` with no authentication; anyone on the LAN (guest Wi-Fi, other devices) can post events. **How (minimal):** a shared secret header (`X-API-Key`) checked in one dependency; key in `.env`, also set on the agents. **When:** before the server runs on any network you don't fully control.
- **[Improve]** Lines 47, 56: manual spans `handle_os_event` duplicate what `FastAPIInstrumentor` already creates per request. Keep them only if you add attributes (`span.set_attribute("event.process", ...)`); otherwise remove.
- **[Improve]** Both endpoints share the same loop; only the mapper differs. A small helper `_ingest(events)` removes the duplication.
- **[Improve]** Return `202`/`{"accepted": n}` instead of `{"ok": True}` so clients can verify how many events were processed.

## `middleware.py`
- **[Improve]** Duplicates the request span the instrumentor already records. If you keep it, log something the span doesn't give you on the console: status code and duration in ms. Remove the `\n` from the log message — it breaks one-event-per-line log parsing.

## `models.py`
- **[Bug]** `PhoneEventSchema` nullability — see critical bug #4.
- **[Improve]** Field names mix camelCase (`eventStartTime`) and snake_case (`event_start_time`) because they mirror each client. **How:** use snake_case in Python and `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)` for the camelCase clients.
- **[Improve]** Timestamps arrive in three formats: ms epoch (browser, phone) and local-time string (Windows). Pick one wire format — epoch ms or ISO-8601 with offset — for all agents.
- **[Improve]** `recent_windows: list` is untyped; define a `RecentWindowSchema` so the feature extractor can rely on its keys.
- **[Improve]** `sentToApi`, `isVerified`, `id` (phone) are client-internal state; the server ignores them. Don't require them in the schema.
- **[Risk]** `OSEventSchema` has no `id`, although the agent sends one (`agent.py:191`). The server generates a new UUID (`event.py:67`), so a retried batch is stored twice. See "idempotency" in `best-practices.md`.
