# Additional comments — senior pass

The earlier files go file by file. This one steps back. It is blunt on purpose: the criticism targets the code, not you. For a personal project this is a decent amount of working software, and that is exactly why it's worth holding to a higher bar.

Nothing here asks for more infrastructure. Most of it asks for **less**: fewer representations, fewer moving parts, fewer things that only work on your machine.

---

## The verdict in five lines

1. **It works on your machine, and only there.** Fresh DB fails, the launcher points at missing modules, deps are missing, and the env vars aren't documented. Nobody, including you in six months, can set it up from the repo.
2. **Data correctness is an afterthought.** Swapped features, duplicates on retry, lost sessions, naive local timestamps, AI labels used as training labels. A telemetry project whose telemetry isn't trustworthy has no foundation.
3. **The same thing is defined three to five times.** An "OS event" exists as an agent dict, a queue-DB row, a pydantic schema, a dataclass, an `EnrichedEvent`, a server-DB row, a notebook DataFrame and a UI tuple. Every boundary is a place for drift — and drift is what produced most of the bugs.
4. **Annotations lie.** `int` holding strings, `list` holding dicts, `-> bool` returning `None`, `-> "Event"` returning a tuple. Wrong types are worse than no types, because readers trust them.
5. **There is no feedback loop on quality.** No tests, no CI, no type checker, no linter, no measure of how good the classifier is in production. You discover bugs by staring at the database.

---

## 1. Architecture

**[Arch] The dependency direction is inverted.**
`processing_layer/event.py` (the domain) imports `server.api.models` (the HTTP layer). `classifier.py` imports from `processing_layer`, and `processing_layer` imports from `classifier`. The `TYPE_CHECKING` imports exist to dodge circular imports. That's a symptom, not a fix.
**Rule:** the domain (events, classification, categories) imports nothing from the project. The API, DB, classifier and UI import the domain. One `server/domain.py` holding `Event`, `Classification`, `EventCategory` and `EventSource` untangles the whole graph.

**[Arch] The folder layout doesn't match what the things are.**
- The desktop review UI lives in `server/event_classifier/frontend/`. It isn't part of the server and isn't part of the classifier; it's a separate app reading the DB.
- `server/logs/` is a Python package **and** the output folder for log and trace files. Code and runtime data share a directory.
- `processing_layer/sql_queries.py` is DB code living in the processing layer.

Suggested layout (a move, not a rewrite):
```
server/   api/  domain.py  processing.py  classifier/  db/ (schema, migrations, queries, repository)
desktop/  (the PySide6 review app)
agents/   windows/  browser/  android/
shared/   settings.py  schemas.py
data/     (gitignored: dbs, logs, traces, model)
```

**[Arch] The browser↔OS correlation is by arrival, not by time.**
Browser events are attached to whichever OS event is *closed next* (`collect_browser_events` drains the queue at window switch). An extension event that arrives late, or after focus moved to another app, gets glued to the wrong window. You already store start and end times for both. Correlate on the server by **time overlap** (`browser.start BETWEEN os.start AND os.end`). That's simpler and correct, and lets the agent drop the coupling.

**[Arch] There is no device identity.**
Events don't say which machine or phone they came from. A second PC, a laptop or a reinstall makes the data ambiguous. Add `device_id` (a UUID generated once per agent install) to every event. It's one column and one config value, and impossible to add retroactively.

**[Arch] Run the agent's local HTTP server only because it is the simplest bridge — and say so.**
Running FastAPI and uvicorn inside the Windows agent to receive one POST from Chrome is heavy, but it's the simplest option (native messaging is worse). Keep it. Just bind it to `127.0.0.1` explicitly, never from an env var that can become `0.0.0.0`.

---

## 2. Data & ML — where it actually matters

**[Data] Decide the questions before collecting more data.**
The Dashboard tab is empty, the views aren't committed, and the model predicts five categories. What are the three questions this project answers? For example: "hours studying per week", "what kills my evenings", "phone vs PC split". Write them in the README and build those three queries first. They tell you which data must be exact (durations, idle time, timezones) and which features are noise.

**[Data] Auto-approving at 0.9 removes the only ground truth you have.**
Anything above 0.9 never reaches you, so you never find out the model's confident mistakes. Those are the expensive ones. At minimum, sample 5–10% of auto-approved events into the review queue. Track **AI vs user agreement rate** on reviewed events per week. That is your real production accuracy; the notebook's test-set number isn't.

**[Data] Idle time is missing, so durations are fiction.**
Covered per agent earlier, but the impact is global: the duration views you just added sum AFK time as activity. Fix collection before building more analytics on top of it.

**[ML] Five categories and ~2.4 MB of ensemble.**
A three-model soft-voting ensemble (LogReg + SVC + RandomForest) over TF-IDF, for five classes where `executable` + `domain` alone probably decide most of it. Before tuning further, report a **baseline**: majority class, and a lookup table "most common user label per executable/domain". If the ensemble doesn't clearly beat the lookup, ship the lookup and the hard-coded rules. Simpler, explainable, no pickle.

**[ML] Version the model with its data.**
Save next to the model: training date, row count, label source query, sklearn version and test metrics. Without this you can't tell whether a retrain helped.

---

## 3. Code quality

**[Code] Comments teach the language instead of explaining the code.**
Examples: `// suspend = async`, `// ?: if (INSTANCE==true)`, `// withContext switches the thread…`, `# Converts Unix-style timestamp…`. These are personal study notes. Move them to your own notes. In code, comment only on *why* something non-obvious is done — the existing `# sqlite does not recognize numpy's bool type` is a good example of that.

**[Code] Commented-out code and "temp" markers.**
`api.py:37-39`, `Main.kt:27-30`, `WorkerManager.kt:42-45`, `temp_quit_btn`, `// this got broken.`, the `LLMClassifier` stub. Git remembers deleted code. Delete it, or turn it into a config flag or an issue.

**[Code] Three ways to hold one record.**
In Python, pick: **pydantic at the edges** (HTTP in), **one dataclass in the middle**, **`sqlite3.Row` from the DB**. No ad-hoc dicts passed between functions (`agent.py`), and no positional tuples read by index (`table_widgets.py`, `get_previous_events_info`).

**[Code] Logging volume and content.**
There are nine `logger.info` calls, mostly per-event, and they log window titles and URLs. The log files hold your browsing history in plain text with no rotation or retention. Log events at `DEBUG`, keep `INFO` for lifecycle (start, stop, batch sent, n rows), and never log titles or URLs above `DEBUG`.

**[Code] Naming is inconsistent across the stack.**
`category`, `type` and `EventType` mean "source". `class`, `class_` and `EventCategory` mean "label". `executable`, `process` and `packageName` mean "app". `AndroidApps` names a single app; `CustomWorker` and `WorkerManager` (next to Android's `WorkManager`) are generic. Write a 10-line glossary in the README and rename to it.

**[Code] No packaging.**
There's no `pyproject.toml`, no `__init__.py` anywhere (implicit namespace packages), no declared Python version, and everything has to run from `telemetry-app/` with `python -m`. A minimal `pyproject.toml` (name, `requires-python`, deps, ruff and pytest config) plus `pip install -e .` makes imports work from anywhere, including tests and the notebook.

---

## 4. Dependencies & footprint

**[Deps] You install far more than you use.**
- `PySide6`, `PySide6_Addons`, `PySide6_WebEngine` and `PySide6_Pdf`: the UI uses only widgets. `PySide6-Essentials` alone is enough and is several hundred MB smaller.
- `grpcio`, `protobuf` and all the OTLP gRPC and HTTP exporters: you use only `FileSpanExporter`. Drop the rest.
- `ollama` for a stub classifier.

**Rule:** every dependency must be imported somewhere. If it isn't, delete it.

---

## 5. Security & privacy (proportionate to a personal project)

This is a keylogger-adjacent dataset: every window title, URL and app you use, with timestamps.
- Plain HTTP on the LAN with no authentication, on `0.0.0.0`. One shared API key in a header is the whole fix.
- Your PC's MAC and LAN IPs are committed to a **public** repo (`MainScreen.kt`, `build.gradle.kts`). Low risk, but move them to `local.properties` and `.env`.
- Android `allowBackup="true"` sends the usage DB to cloud backup.
- Full URLs with query strings are stored, which can include tokens and search terms. Strip the query in the extension unless the model needs it.
- The DB, logs and traces sit inside the repo folder. One wrong `git add -f` publishes your life. Move them to a data directory outside the repo.

---

## 6. Process

**[Process] Make "it works from a clean clone" a check you run.**
Once a week, or before calling a feature done: clone into a new folder, create a venv, `pip install`, delete the DBs, run `startup.bat`. Every critical bug in `00-critical-bugs.md` except the ML ones would have failed this check.

**[Process] Minimal CI, one file.**
A GitHub Actions workflow running `ruff check`, `ruff format --check` and `pytest` on push. For Android, `./gradlew assembleRelease` would have caught the missing `API_BASE_URL` in release. That's about 30 lines of YAML. Don't add more than that.

**[Process] Commits should match their messages.**
The last commit says "Created views…", but no view is in the diff. Small commits that each leave the project runnable make bisecting possible when the data looks wrong.

**[Process] Add a real README.**
Currently it's three screenshots. Needed: what it does, the three questions it answers, the architecture diagram you already have, setup steps, env vars, how to retrain, and the glossary.

---

## Priority after the critical bugs

| Do | Skip for now |
|---|---|
| Domain module + fix import direction | Async rewrite, ORM, DI framework |
| `device_id`, UTC timestamps, idle detection | Kafka/queues, Docker |
| Baseline vs ensemble, sample auto-approved events | Hyperparameter tuning, LLM classifier |
| `pyproject.toml`, ruff, pytest, 30-line CI | Coverage targets, mypy strict mode |
| README + glossary + clean-clone check | Microservices, cloud deployment |

Fix the data, simplify the representations, and add the three checks (lint, test, clean clone). That covers about 80% of the value.
