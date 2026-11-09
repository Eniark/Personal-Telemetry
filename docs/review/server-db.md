# Server — Database (`server/db/`)

Score: **3/10** — the schema in git no longer matches the database you run.

---

## `init_db.py`
- **[Bug]** Generated columns reference `start_timestamp` / `end_timestamp` — table creation fails. Critical bug #1.
- **[Bug]** `model_confidence` column missing. Critical bug #2.
- **[Bug]** Line 52: `REFERENCES os_event(event_id)` — the table is `os_events` (plural). Also `event_id` is not `UNIQUE`; SQLite requires the parent key to be unique, so the FK can never be satisfied once enforcement is on.
- **[Bug]** Line 6: `PRAGMA foreign_keys = ON` is **per connection**. It's set only on this short-lived init connection; the API's connection never enables it. **How:** set the pragma inside `create_db_connection()`.
- **[Info]** The last commit message says views were created for duration distributions; no `CREATE VIEW` exists in the repo. They seem to live only in your local DB. Commit them as SQL.
- **[Risk]** Runs at import (`repository.py:10` imports it for the side effect). Importing the repository from the UI or a test creates/touches the real DB. **How:** wrap in `def init_db(conn)` and call it from the entry points.
- **[Improve]** No migration story. Every schema change so far was done by hand on the live DB. **How (minimal, no new library):** keep numbered SQL files (`migrations/001_init.sql`, `002_add_confidence.sql`) and track the version with `PRAGMA user_version`. On start: apply files with number > `user_version`. ~20 lines of Python. **When:** now — you already have drift.
- **[Improve]** Timestamps are `TEXT` in local time without offset. `unixepoch()` treats them as UTC; durations are still right, but DST changes and cross-device comparisons (phone vs PC) won't be. Store UTC (ISO-8601 with `Z`, or integer epoch) and convert in the UI.
- **[Improve]** `BOOL` isn't a SQLite type (stored as NUMERIC). Use `INTEGER NOT NULL DEFAULT 0` and say so.
- **[Improve]** No `NOT NULL` anywhere, no indexes. Add an index on `browser_events(os_event_id)` (used by the UI join) and `os_events(classification_approved, event_start_time)` (UI list query). **When:** at a few tens of thousands of rows; cheap to add now.
- **[Improve]** `os_events.event_id` should be `UNIQUE NOT NULL` — it's what makes idempotent inserts possible (`INSERT ... ON CONFLICT(event_id) DO NOTHING`).

## `repository.py`
- **[Bug]** Lines 19-63: `executemany` calls are outside the `try`; only `commit()` is protected. An insert error raises past the handler. If the first `executemany` succeeds and the second fails, the OS rows stay in the open transaction and are committed later together with other data.
  **How:** `with self.db:` (sqlite3's context manager commits on success and rolls back on exception) around both inserts.
- **[Bug]** On error the function returns `None` (implicit), not `False`, and uses `print(e)` instead of logging. Use `logger.exception(...)` and `return False`.
- **[Improve]** Line 65: return annotation `tuple[list|None, list[Any]]` is wrong; it returns `list[tuple]`. Set `row_factory = sqlite3.Row` and return rows the UI can address by name, so `table_widgets.py` doesn't depend on column positions.
- **[Improve]** Line 15: `batch_size` is a repository attribute but only the processor uses it. It's policy, not storage — move it out (or remove buffering, see `server-processing.md`).
- **[Improve]** Line 34: `bool(...)` to work around numpy bools. Convert numpy types once, at the classifier boundary (`float(confidence)`, `str(predicted_class)`), so the rest of the code never sees numpy.
- **[Improve]** Line 9: `import json, sqlite3` on one line, and `Connection` is imported separately. PEP 8: one import per line; let ruff's isort rule (`I`) sort them.
- **[Risk]** `update_classification` formats the table name into SQL — validate against an allow-list (see `server-processing.md`).
