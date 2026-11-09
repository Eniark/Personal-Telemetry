# Critical bugs (fix first)

Each item was verified by reading the code; #1 and #2 were also confirmed by running the SQL against SQLite 3.53.

---

## 1. Fresh database cannot be created
**Where:** `server/db/init_db.py:28-30` and `:49-51`
**What:** The generated column uses `unixepoch(end_timestamp) - unixepoch(start_timestamp)`. Those columns don't exist; the real names are `event_start_time` / `event_end_time`. SQLite fails with `no such column: start_timestamp` on both `CREATE TABLE` statements.
**Why you didn't notice:** `CREATE TABLE IF NOT EXISTS` is skipped on your existing DB, so only a new install (or a deleted DB) hits it.
**How:** Use the real column names. Then test on an empty DB every time you change the schema (see "migrations" in `best-practices.md`).

## 2. Inserts fail on a fresh database
**Where:** `server/processing_layer/sql_queries.py:14, 36` vs `server/db/init_db.py`
**What:** `INSERT_*` and `SELECT_*` queries use `model_confidence`, but neither `CREATE TABLE` defines it. Result: `table os_events has no column named model_confidence`.
**How:** Add the column to both tables. Your local DB was probably altered by hand — that is the exact drift a migration file prevents.

## 3. Executable and publisher features are swapped at inference
**Where:** `server/event_classifier/backend/event_feature_extractor.py:38-52` vs `:133-138`
**What:** `get_previous_events_info` returns `(exe_1, pub_1, exe_2, pub_2, …)`. The caller unpacks it as `(pub_1, exe_1, pub_2, exe_2, …)`. Every `previous_event_N_executable` gets the publisher and vice versa. The model was trained on the correct order in the notebook, so live predictions use mismatched features.
**How:** Don't return a 13-item positional tuple. Return a `dict` keyed by feature name and pass it with `EnrichedEvent(**features)`. Positional tuples of this size are exactly where order bugs hide.

## 4. Android batches with missing metadata are rejected forever
**Where:** `server/api/models.py:4-14` vs Android `ActivityEvent.kt:10-12`
**What:** Android sends `appName`, `description`, `developer` as nullable. The server schema declares them `str` (required, non-null). Pydantic returns HTTP 422 for the whole batch if any event has `null` (e.g. an app whose Play Store page failed to scrape). The app only marks events as sent on success, so the same failing batch is resent every 15 minutes.
**How:** Declare them `str | None = None` on the server. Rule of thumb: the server schema must be at least as permissive as every client that sends to it.

## 5. `startup.bat` runs modules that don't exist
**Where:** `startup.bat:3-4`
**What:** `python -m server.api.main` — the file is `server/api/api.py`. `python -m agents.windows.main` — the entry point is `agents/windows/client/agent.py`.
**How:** Point to `server.api.api` and `agents.windows.client.agent`, or add thin `main.py` entry points so the names are stable.

## 6. The model is trained on its own predictions
**Where:** notebook cell 2 (`WHERE ... class IS NOT NULL`)
**What:** `class` is filled by the AI for every event, and auto-approved when confidence > 0.9 (`processing_layer/main.py:78`). The training query takes all of them, so each retrain reinforces the previous model's mistakes (feedback loop).
**How:** Train on `classified_by = 'user'` only, or at least `classification_approved = 1 AND classified_by = 'user'`. Keep AI labels for evaluation, not training.

## 7. Classifier failure crashes the request
**Where:** `event_classifier/backend/classifier.py:19-25` → `processing_layer/main.py:70`
**What:** `classify()` catches every exception with a bare `except:` and implicitly returns `None`. The caller does `confidence, class_ = ...`, which raises `TypeError: cannot unpack NoneType`. Also, if the classifiers list is empty, `confidence` is never defined (`NameError`). `LLMClassifier._classify` always returns `None`, so enabling it triggers this path every time.
**How:** Return an explicit "no prediction" value (e.g. `(0.0, None)`) on failure, use `except Exception`, and log with `logger.exception(...)` so the traceback is kept.

## 8. `HardCodedClassifier` results can't be saved
**Where:** `classifier.py:33-40` → `db/repository.py:31`
**What:** It returns an `EventCategory` enum; the ML model returns a plain string. `sqlite3` cannot bind an `Enum` and raises on insert. It's currently commented out in `api.py:37`, so it's latent.
**How:** Pick one type for `Classification.class_` (enum is better) and convert with `.value` in exactly one place — the repository.
