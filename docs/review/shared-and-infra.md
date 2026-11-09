# Shared code & infrastructure

Score: **4/10** — small and readable, but several import-time side effects and a broken launcher.

---

## `requirements.txt` — 3/10
- **[Bug]** Missing runtime deps the code imports: `pandas`, `numpy`, `scikit-learn`, `joblib` (classifier.py), `pystray`, `Pillow` (tray_icon.py). A clean `pip install -r` cannot start the server.
- **[Bug]** The notebook also needs `catboost`, `xgboost`. Put them in a separate `requirements-dev.txt` (or `[project.optional-dependencies]`), because the server doesn't need them.
- **[Improve]** Both `dotenv==0.9.9` and `python-dotenv==1.2.4` are listed. `dotenv` is a shim that pulls `python-dotenv`; keep only `python-dotenv`.
- **[Risk]** `pywin32` breaks install on Linux/macOS. Use a marker: `pywin32==312; sys_platform == "win32"`.
- **[Improve]** The file is a full `pip freeze` (transitive deps mixed with direct ones). **When:** as soon as you have more than ~10 deps. **How:** keep direct deps in `requirements.in` / `pyproject.toml` and generate the lock with `pip-tools` or `uv`.
- **[Risk]** `scikit-learn` version must match the one used to dump `event_classifier.joblib`, or loading may fail/warn. Pin it explicitly.

## `startup.bat`
- **[Bug]** Wrong module paths — see critical bug #5.
- **[Improve]** Opening an interactive `sqlite3` shell at startup holds a connection open; it's a debugging aid, not a service. Move it to a separate `dev-db.bat`.
- **[Improve]** `exit` at the end is unnecessary; `start` already detaches.

## `.env.example`
- **[Bug]** `TELEMETRY_SERVER_PORT` is empty and the Windows agent requires `WINDOWS_AGENT_SERVER_PORT` / `WINDOWS_AGENT_SERVER_HOST`, which are not listed. A new setup fails with no hint.
- **[Improve]** Use `KEY=value` without spaces; it's the format every tool (Docker, shells) accepts, not only python-dotenv.
- **How:** list every variable any component reads, with a working default and a one-line comment.

## `.gitignore`
- **[Risk]** `app/src/test/` and `app/src/androidTest/` are ignored — any test you write for Android will never be committed. Remove those lines.
- **[Improve]** Add `*.joblib` once the model moves out of git (see classifier review), and `.ipynb_checkpoints/`.

## `shared/configs.py`
- **[Risk]** `LOGS_FILE_NAME` (line 14) is computed once at import. A server running past midnight keeps writing to yesterday's file. Use `logging.handlers.TimedRotatingFileHandler(when="midnight")` instead of a date in the file name.
- **[Improve]** `TIMESTAMP_FORMAT.split(" ")[0]` (line 8) is clever but fragile; write `"%Y-%m-%d"` directly.
- **[Improve]** `LISTEN_TO_ALL_DEVICES = True` silently overrides `TELEMETRY_SERVER_HOST` from `.env` (`api.py:70`). Two sources of truth for one value. Keep only the env var.
- **[Improve]** Data (DB, logs, traces) lives inside the source tree. **When:** before you package or share it. **How:** use a data dir (e.g. `%LOCALAPPDATA%/PersonalTelemetry`, or `platformdirs.user_data_dir`) configurable by env var.

## `shared/utils.py`
- **[Bug]** `validate_env_variable`, line 12: `var = os.getenv(var)` overwrites the name, so the error on line 14 prints `"None" must be defined` instead of the variable name.
- **[Bug]** Line 17-19: `int("localhost")` raises `ValueError`, not `TypeError`. Any non-numeric required var crashes here.
- **[Improve]** Mutable default argument (`REQUIRED_ENV_VARS = [...]`), and the function both validates and converts. **How:** replace with a typed settings object — `pydantic-settings` `BaseSettings` (you already use pydantic). You get validation, types, defaults and `.env` loading in ~10 lines, and no positional `validated_env_vars[0]` indexing.
- **[Improve]** `convert_date_to_readable_format` creates naive local-time strings. See "timestamps" in `best-practices.md`.
- **[Risk]** `check_same_thread=False` disables SQLite's safety check without adding a lock. Fine only while one thread uses the connection. See `server-api.md`.

## `shared/enums.py`
- **[Improve]** `EventType` (`browser/os/phone_os`) is the *source* of an event, while `EventCategory` is the *class*. But the field holding `EventType` is named `category` (`event.py:16`) and the DB column is `type`. Pick one name per concept everywhere (e.g. `source` and `category`).

## `server/logs/logger.py`
- **[Improve]** `import logging` twice (lines 1 and 6).
- **[Risk]** Creates folders and file handlers at import time. Any module that imports the logger (including the UI and tests) creates log files. **How:** expose `setup_logging()` and call it once from each entry point; elsewhere use `logging.getLogger(__name__)`.
- **[Improve]** Across the codebase log calls use f-strings (`logger.info(f"...")`). Prefer `logger.info("x=%s", x)`: formatting is skipped when the level is disabled, and log aggregators can group by template.

## `server/logs/tracing.py`
- **[Risk]** Configured as an import side effect (`api.py:3` imports it just for that). Same fix as the logger: `setup_tracing()` called from `main`.
- **[Risk]** `BatchSpanProcessor` buffers spans; without `provider.shutdown()` on exit, the last batch is lost. Register it in FastAPI's lifespan shutdown.
