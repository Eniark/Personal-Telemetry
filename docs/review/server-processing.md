# Server — Processing layer (`server/processing_layer/`)

Score: **5/10**

---

## `main.py` (EventProcessor)
- **[Improve]** File name: `main.py` usually means "entry point". It holds `EventProcessor`; rename to `event_processor.py`. `api.py:8` also imports `TelemetryRepository` *through* this module — import it from `server.db.repository` directly.
- **[Bug]** Line 25: annotated `list[Event]` but assigned a `dict[EventType, list]`. Type checkers (and readers) are misled. Annotate `dict[EventType, list[Event]]`.
- **[Bug]** Lines 67-79 (`add_class`): crashes if a classifier returns `None` or if `classifiers` is empty — see critical bug #7. Also, when no classifier returns a class, the loop falls through with the last `confidence` and `class_ = None`, and that is stored as an AI classification.
- **[Improve]** Line 75: every result is marked `ClassificationRole.AI`, even from `HardCodedClassifier` (the comment says so). **How:** let each classifier return the full `Classification` (it knows who it is), so the processor just takes the first non-empty one.
- **[Improve]** Line 78: `0.9` is a magic number that decides what the user never reviews. Move it to config as `AUTO_APPROVE_THRESHOLD`.
- **[Risk]** Lines 31-37: events are buffered in memory and flushed when `len > batch_size` (`batch_size = 1`, so after 2 OS events). A crash or restart loses the buffer, and the client already got `200`, so it won't resend. With `batch_size = 1` buffering has no benefit. **How:** write each request's events in one transaction before returning. Batch by request, not across requests.
- **[Risk]** If `insert_events` fails, the buffer is kept and retried on the next event, which re-inserts the rows that did succeed (no transaction around both tables; see `server-db.md`).
- **[Improve]** Flush only checks the OS list; browser events wait for an OS event. Fine today because they arrive together, but it's a hidden coupling.

## `event.py`
- **[Bug]** `Event.event_start_time: int` (line 14) but every constructor passes a formatted string. Fix the annotation or, better, store a `datetime` and format only at the edges (DB / UI).
- **[Improve]** `processing_time` is computed with `datetime.now().strftime(...)` in three places. One helper (or a `default_factory`) removes the repetition.
- **[Improve]** `previous_events: list`, `related_browser_events: list` — give them element types (`list[BrowserEventSchema]`).
- **[Improve]** `class_` naming is used to avoid the keyword; `category` would read better — but `category` is taken by `EventType` (see `shared-and-infra.md`, naming). Rename `category` → `source`, then `class_` → `category`.
- **[Improve]** `PhoneMapper` is a class with one static method. A module-level function `phone_to_os_event()` is simpler, or a `from_phone_schema` classmethod next to `from_schema` for consistency.
- **[Improve]** Custom `__repr__` hides fields that dataclass would show. Remove it, or use `field(repr=False)` on the noisy fields instead.

## `event_filter.py`
- **[Improve]** `IGNORED_PROCESSES` / `IGNORED_URLS` are lists; use `frozenset` (O(1) lookups, immutable).
- **[Risk]** Line 21: the `else` branch assumes anything not an OS event is a browser event. A third type would crash on `.url`. Use explicit `isinstance(event, BrowserEvent)` and raise for unknown types.
- **[Improve]** Process names are compared case-sensitively (`"explorer.exe"`); Windows names vary in case (`Explorer.EXE`). Compare `.lower()`.
- **[Improve]** The class has no state; module-level functions are enough. Move the ignore lists to config if you plan to edit them.

## `sql_queries.py`
- **[Bug]** Uses `model_confidence`, not present in the schema — critical bug #2.
- **[Risk]** `UPDATE_EVENT_CLASS_QUERY` uses `{table}` with `str.format` (line 71). Callers pass constants today, but the repository accepts any string. Validate against an allow-list (`{"os_events", "browser_events"}`) inside the repository.
- **[Improve]** `SELECT_OS_EVENTS_QUERY` has no `LIMIT`; the UI fetches everything and slices to 20 in Python (`table_widgets.py:65`). Add `LIMIT ?`.
- **[Improve]** This file belongs to the DB layer, not processing. Move it to `server/db/`.

## `enums.py`
- **[Improve]** Mixed quote styles (`"..."` and `'...'`). Let a formatter (ruff/black) decide — see `best-practices.md`.
- **[Improve]** `EventCategory` is the label set of the model. If you add a category, the trained model doesn't know it. Note this next to the enum.
