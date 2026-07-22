# Code Review: Directory Structure (Python only)

# FIXME: Root directory pollution. Global modules like `configs.py` and `logger.py` sit at the root, making it unclear which parts of the app rely on them (Does the Windows tracker use it? The API? Both?).
# SUGGESTION: If shared by both the server and Python clients, move them to a `shared/` folder. If only used by the server, move them into a `server/` directory.

# FIXME: No separation between Server and Clients (Agents). The central backend (`api`, `processing_layer`, `db`) is mixed at the exact same level as the data-gathering clients (`win_tracker`, `tab_tracker`, `android_app`).
# SUGGESTION: Group by architectural role. Create a `server/` (or `backend/`) folder for the central brain, and an `agents/` (or `clients/`) folder for the trackers.

# FIXME: Vague module naming. `processing_layer` is overly academic and conceptually disconnected from the `api` directory it serves. `win_tracker` and `tab_tracker` use inconsistent naming conventions.
# SUGGESTION: Fold `processing_layer` into the server module as `core` or `services`. Standardize client names (e.g., `agent_windows`, `agent_browser`).

### Suggested Architecture Refactor

```text
.
├── agents/                  # All data-gathering clients
│   ├── windows/             # (Was win_tracker)
│   ├── browser/             # (Was tab_tracker)
│   └── android/             # (Was android_app)
├── server/                  # Central backend
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # (Was processing_layer)
│   ├── db/                  # db-init.py and schemas
│   ├── configs.py
│   └── logger.py
├── shared/                  # (Optional) If configs/logger are used by both server and windows agent
├── requirements.txt
└── README.md
```


---
# `TODO` Tree summary (install the extension for ease of use) `[auto-created by LLM]`

### Global / Architecture
* **TODO:** Restructure Directories: Separate into `server/` (backend) and `clients/`. Move `configs.py` and `logger.py` to `shared/` or `server/`.
* **TODO:** Rename Modules: Standardize agent folders (e.g., `agent_windows`, `agent_browser`). Fold `processing_layer` into `server/core`.
* **TODO:** `configs.py` (Line 17): Add a comment explaining the `-precision` logic.

### Server (`api/main.py`)
* **TODO:** Line 15: Fix global SQLite connection (Dependency injection or `aiosqlite`).
* **TODO:** Line 24: Rename duplicate `async def event` endpoints to unique names.
* **TODO:** Line 27: Replace `dict` payloads with Pydantic `BaseModel` schemas.
* **TODO:** Line 30: Validate `eventTime` before math operations to prevent `TypeError`.
* **TODO:** Line 62: Remove debug `print(payload)`.
* **TODO:** Line 76: Add safe defaults to `os.getenv` casting (e.g., `int(os.getenv("PORT", 8000))`).
* **TODO:** Line 81: Remove the `0.0.0.0` IP override hack.

### Database (`db/db-init.py`)
* **TODO:** Line 4: Use a context manager (`with sqlite3.connect...`) for safe commits/rollbacks.
* **TODO:** Line 8: Execute `PRAGMA foreign_keys = ON;` immediately after connection.
* **TODO:** Line 14: Rename `os_activity` column `event_time` to `started_at`.
* **TODO:** Line 27: Rename `browser_activity` column `event_time` to `started_at`.
* **TODO:** Line 30: Fix `duration_ms` (calculate in Python or use SQLite `GENERATED ALWAYS AS` column).

### Processing Layer (`processing_layer/`)
**`event.py`**
* **TODO:** Line 6: Add `frozen=True, slots=True` to dataclasses.
* **TODO:** Line 24: Fix type hint: `os_event_id: int | None = None`.
* **TODO:** Line 34: Add `@staticmethod` to `to_os_event`.
* **TODO:** Line 38: Add validation for `payload.get('usedAtTimestamp')`.

**`main.py`**
* **TODO:** Line 15: Change batch flush threshold to `>= self.batch_size`.
* **TODO:** Line 24: Move ID increment to execute *after* successful DB commits.
* **TODO:** Line 28: Decouple OS and Browser flush logic to prevent cross-domain race conditions.
* **TODO:** Line 48: Remove redundant parentheses around list comprehension.
* **TODO:** Line 64: Replace `print()` with standard logging.
* **TODO:** Line 67: Fix last ID fetching (use SQLite `RETURNING id` instead of `.lastrowid` on `executemany`).
* **TODO:** Line 72: Fix FK constraint errors (ensure OS events commit before browser events).
* **TODO:** Line 97: Replace `sqlite_sequence` lookup with `SELECT COALESCE(MAX(id), 0) FROM table`.
* **TODO:** Line 99: Remove f-string formatting in SQL execution.

### Windows Tracker (`win_tracker/main.py`)
* **TODO:** Line 14: Add fallback default values to `os.getenv()`.
* **TODO:** Line 31: Wrap `psutil.Process(pid)` in try/except for `AccessDenied` and `NoSuchProcess`.
* **TODO:** Line 37: Refactor `get_event_category` to accept `executable` string directly to skip duplicate queries.
* **TODO:** Line 58: Catch specific exceptions instead of a bare `except Exception:`.
* **TODO:** Line 83: Move the synchronous `requests.post` to a background worker queue to stop the hook from freezing.
* **TODO:** Line 106: Replace CPU-locking `while True` loop with `pythoncom.PumpMessages()`.

---
# Raw `TODO` tree
```
└─ Personal-Telemetry
   ├─ android_app
   │  └─ data_extraction_rules.xml
   │     └─ line 8: TODO : Use <include> and <exclude> to control what is backed up.
   ├─ api
   │  └─ main.py
   │     ├─ line 15: FIXME : Global SQLite connection shared across FastAPI's async worker threads is ANTI-pattern. It WILL lead to database locking and potential corruption.
   │     ├─ line 24: FIXME : All your POST endpoints are named `async def event`. In Python, the later definitions overwrite the earlier ones in the module namespace. While FastAPI routes might still technically fire, it ruins OpenAPI schema generation and internal references.
   │     ├─ line 27: FIXME : Typing payloads as `dict` defeats the core strength of FastAPI (auto-validation, 422 error handling, Swagger UI generation).
   │     ├─ line 30: FIXME : If `eventTime` is missing from the payload, `payload.get('eventTime')` returns `None`. `None / 1000` will crash the server with a TypeError.
   │     ├─ line 62: FIXME : Leftover debug print statement in an API endpoint. This will spam the production console.
   │     ├─ line 76: FIXME : `os.getenv` returns `None` if the variable is missing. `int(None)` will throw a TypeError and the app will completely fail to start.
   │     └─ line 81: FIXME : Weird hack to force 0.0.0.0.
   ├─ db
   │  └─ db-init.py
   │     ├─ line 4: FIXME : Manual commit() and close() leave the database prone to locking if an exception occurs mid-execution.
   │     ├─ line 8: FIXME : SQLite ignores foreign key constraints by default.
   │     ├─ line 14: FIXME : CRITICAL SCHEMA MISMATCH. You define `event_time` here, but in `main.py` your INSERT query uses `started_at`. This will immediately crash with an OperationalError.
   │     ├─ line 27: FIXME : CRITICAL SCHEMA MISMATCH again. `main.py` expects `started_at`, not `event_time`.
   │     └─ line 30: FIXME : `duration_ms` is defined here but completely ignored in the `main.py` INSERT query. It will always be NULL.
   ├─ processing_layer
   │  ├─ event.py
   │  │  ├─ line 6: FIXME : Add frozen=True and slots=True to @dataclass decorators for memory optimization and event immutability.
   │  │  ├─ line 24: FIXME : os_event_id: int = None violates type safety. Use os_event_id: int | None = None
   │  │  ├─ line 34: FIXME : Add @staticmethod decorator or convert to a standalone function since this holds no state and lacks 'self'.
   │  │  └─ line 38: FIXME : Fragile payload extraction. payload.get('usedAtTimestamp') can return None, polluting the integer event_time field without validation.
   │  └─ main.py
   │     ├─ line 15: FIXME : Using '>' instead of '>=' means you store batch_size + 1 items before flushing (e.g. 6 items for batch_size=5). Use '>=' or fix the batch threshold.
   │     ├─ line 24: FIXME : Incrementing this ID in-memory before DB commit guarantees your state will drift if a DB insert fails.
   │     ├─ line 28: FIXME : Fatal logic bug. Checking 'len(self.browser_activities)' inside an OS event handler creates cross-domain coupling and race conditions.
   │     ├─ line 48: FIXME : Redundant parentheses around the list comprehension: `( [ ... ] )`.
   │     ├─ line 64: FIXME : Remove print - Prefer logging instead for more control?
   │     ├─ line 67: FIXME : executemany() in sqlite3 returns None for cursor.lastrowid. Returning this will break or return incorrect batch ID tracking.
   │     ├─ line 72: FIXME : "not working properly" is likely a Foreign Key constraint failure?
   │     ├─ line 97: FIXME : Fragile table-driven ID lookup. Relying strictly on sqlite_sequence breaks if the table has no autoincrement or hasn't initialized yet. Fall back to SELECT MAX(id) FROM table.
   │     ├─ line 98: FIXME : Fragile table-driven ID lookup. Relying strictly on sqlite_sequence breaks if the table has no autoincrement or hasn't initialized yet. Fall back to SELECT MAX(id) FROM table.
   │     ├─ line 99: HACK : Never use f-strings for SQL query values, even with allowlists.
   │     └─ line 100: HACK : Never use f-strings for SQL query values, even with allowlists.
   ├─ win_tracker
   │  └─ main.py
   │     ├─ line 14: FIXME : os.getenv returning None will cause int(None) to throw a TypeError and crash on startup if the .env file is missing or incomplete.
   │     ├─ line 31: FIXME : psutil.Process(pid) will throw psutil.AccessDenied for elevated system processes, and psutil.NoSuchProcess if the window closes too quickly. This will crash the hook.
   │     ├─ line 37: FIXME : Performance issue. You already fetch process_info inside the callback, but you are re-fetching it here. psutil lookups are expensive on Windows.
   │     ├─ line 58: FIXME : Bare Exception catches can hide serious bugs (!!!!! like KeyboardInterrupt or SystemExit).
   │     ├─ line 83: FIXME : CRITICAL PERFORMANCE BLOCKER. requests.post is synchronous. Doing network I/O inside a Windows system event hook callback will freeze the hook loop, cause system-wide stutter, and Windows will likely silently drop your hook for taking too long to return.
   │     └─ line 106: FIXME : CRITICAL CPU SPIKE. A `while True` loop without any sleep or blocking wait will pin a CPU core to 100% usage indefinitely.
   ├─ REVIEW.md
   │  ├─ line 3: FIXME : Root directory pollution. Global modules like `configs.py` and `logger.py` sit at the root, making it unclear which parts of the app rely on them (Does the Windows tracker use it? The API? Both?).
   │  ├─ line 6: FIXME : No separation between Server and Clients (Agents). The central backend (`api`, `processing_layer`, `db`) is mixed at the exact same level as the data-gathering clients (`win_tracker`, `tab_tracker`, `android_app`).
   │  └─ line 9: FIXME : Vague module naming. `processing_layer` is overly academic and conceptually disconnected from the `api` directory it serves. `win_tracker` and `tab_tracker` use inconsistent naming conventions.
   ├─ STRUCTURE REVIEW.md
   │  ├─ line 3: FIXME : Root directory pollution. Global modules like `configs.py` and `logger.py` sit at the root, making it unclear which parts of the app rely on them (Does the Windows tracker use it? The API? Both?).
   │  ├─ line 6: FIXME : No separation between Server and Clients (Agents). The central backend (`api`, `processing_layer`, `db`) is mixed at the exact same level as the data-gathering clients (`win_tracker`, `tab_tracker`, `android_app`).
   │  ├─ line 9: FIXME : Vague module naming. `processing_layer` is overly academic and conceptually disconnected from the `api` directory it serves. `win_tracker` and `tab_tracker` use inconsistent naming conventions.
   │  └─ line 33: TODO Tree summary
   ├─ configs.py
   │  ├─ line 1: NOTE : move the application-related libraries to their respective directories
   │  ├─ line 16: NOTE : ambiguous logic (add a comment or make it explicit)
   │  └─ line 17: FIXME : ambiguous logic: why -precision? (add a comment or make it explicit)
   └─ logger.py
      └─ line 1: NOTE : move the application-related libraries to their respective directories

```