# Windows agent (`agents/windows/`)

Score: **6/10** — the durable local queue with backoff is the right architecture. Execution details need work.

---

## `client/agent.py`
- **[Bug]** Lines 108-149: `__monitor_queue` uses `event_queue`, `repository`, `TELEMETRY_SERVER_HOST`, `TELEMETRY_SERVER_PORT` as **module globals** defined under `if __name__ == "__main__"`. It works only when run as a script; importing the class anywhere else raises `NameError`. **How:** use `self.event_queue`, `self.repository`, and pass the server URL into `__init__`.
- **[Bug]** Lines 197-205: variable names are crossed. `WINDOWS_AGENT_SERVER_HOST` holds the agent **port**; `TELEMETRY_SERVER_HOST` reads `WINDOWS_AGENT_SERVER_HOST`; the local agent server binds to that host and the agent also posts to it. It only works because everything runs on one machine. A settings object (see `shared-and-infra.md`) with named fields removes this class of bug.
- **[Risk]** Line 122: `requests.post(...)` without `timeout`. If the server accepts the connection but hangs, the sender thread blocks forever and nothing is sent again. Always pass `timeout=(3, 10)` (connect, read).
- **[Risk]** Retry happens only when a **new** window event arrives (`event_queue.get()` blocks). After an outage, pending events wait until you switch windows. Use `event_queue.get(timeout=self.retry_delay)` and treat `Empty` as "time to retry pending".
- **[Risk]** Idempotency: the agent sends `id`, but the server ignores it and creates a new UUID. If the server stored the batch but the response was lost, the retry duplicates it. Fix on the server side (`server-api.md`).
- **[Bug]** Line 127: on success `retry_delay` is reset to `60`, but the initial value is `5` (line 37). Reset to the initial value (store it as a constant).
- **[Risk]** Lines 64-69: only `psutil.NoSuchProcess` is caught. Elevated processes (Task Manager, admin terminals) raise `psutil.AccessDenied` on `.exe()`. An exception in a ctypes callback is printed and swallowed — the window switch is silently lost, and the previous event never gets queued. Catch `(psutil.NoSuchProcess, psutil.AccessDenied)`.
- **[Risk]** Lines 163-192: the WinEvent hook callback does process lookup, file-version reads and queueing on the message-pump thread. Slow work here delays the hook. Keep the callback minimal (capture `hwnd`, title, timestamp → queue) and enrich in the worker thread.
- **[Risk]** Idle time isn't tracked: leaving the PC on one window for 3 hours is recorded as 3 hours of activity. **How:** `GetLastInputInfo` (user32) polled every ~30 s; close the current event when idle > N minutes. This matters for the duration views you just added.
- **[Risk]** The current event (`self.event`) is never flushed on shutdown/sleep. Handle `WM_POWERBROADCAST` / exit to close it.
- **[Improve]** `__callback`, `__monitor_queue` use double underscore (name mangling). Single underscore is enough.
- **[Improve]** `__callback(..., time)` shadows the `time` module inside the function.
- **[Improve]** `browser_event_queue: list` — it's a `Queue`.
- **[Improve]** `print()` everywhere; use the logger (with a file handler) — the agent runs unattended, so prints are lost when the console closes.
- **[Improve]** Lines 114-116 and 133-136 duplicate "mark unsent and store". Extract a `_store_pending(data)` helper.
- **[Improve]** Event dicts are built ad hoc in three places (callback, repository, request). A small `@dataclass` (or reuse the server's pydantic schema in `shared/`) gives one definition of an OS event.

## `client/api.py`
- **[Improve]** `receive_browser_event(event: dict)` accepts any JSON. Reuse `BrowserEventSchema` from the server (move it to `shared/`) to validate at the edge.
- **[Improve]** The port is duplicated: env var here, hard-coded `8080` in the extension (`TabTracker.js:13`, `manifest.json:18`). Note it in `.env.example` at least.

## `db/init_db.py`, `db/repository.py`, `db/sql_queries.py`
- **[Risk]** Same import-time side effect as the server (`repository.py:4`).
- **[Risk]** Acknowledged events are never deleted; the queue DB grows forever. Delete (or archive) rows with `acknowledged = 1` older than N days.
- **[Bug]** `upsert_events` has no error handling and no transaction context; a failure in `__monitor_queue` kills the sender thread (it's not inside the `try`), and the daemon thread dies silently. Wrap with `with self.db:` and catch/log in the loop.
- **[Improve]** `UPSERT_EVENTS_QUERY` updates only `acknowledged` on conflict, not `sent_at`. Either update both or drop `sent_at`.
- **[Improve]** `get_pending_events` re-reads all unacknowledged rows on every event. With a long outage that is thousands of rows per window switch. Add `ORDER BY id LIMIT 500` and send in chunks.
- **[Improve]** Upsert returns `-> bool` but returns nothing.
