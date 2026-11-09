# Server — Desktop UI (`server/event_classifier/frontend/`)

Score: **6/10** — well-split small widgets; a few Qt-specific bugs.

---

## `tables/table_widgets.py`
- **[Bug]** Line 172: `self.itemClicked.connect(self.show_events_table)` runs on every `populate_table()` call, i.e. every Refresh. After N refreshes one click fires the handler N times. **How:** connect once in `__init__`.
- **[Bug]** Lines 83-84: "Apply" triggers both `update_classification` and `_delete_record`. The row is removed from the UI even if the DB update raises. **How:** one handler that updates, then removes the row only on success.
- **[Bug]** Lines 161-162: `self.item(row, 1)` / `self.item(row, 2)` hard-code column positions, while `get_column_idx()` exists for exactly this. Use `get_column_idx("event_id")`, `get_column_idx("type")`.
- **[Bug]** Line 98: `classified_at = datetime.datetime.now()` passes a `datetime` to sqlite. Python 3.12+ deprecates the default datetime adapter (DeprecationWarning), and it's a different format from the strings the processor writes. Use the same format everywhere (see timestamps in `best-practices.md`).
- **[Bug]** Line 100: user confidence `100` vs model `0..1`. Use `1.0`.
- **[Improve]** Line 65: fetches all unapproved rows and slices to 20 in Python. Push the limit into SQL.
- **[Improve]** Line 75: `setCurrentText(None)` when `class` is NULL. Guard with a default (`EventCategory.OTHER.value` or an empty "—" item).
- **[Improve]** Line 91: `get_column(self, idx: str)` — `idx` is an `int`.
- **[Improve]** `COLUMN_CONFIGS` is declared only in subclasses, while the base class uses it. Declare `COLUMN_CONFIGS: dict[str, Column]` (and `TABLE_NAME: str`) on `TelemetryTable` so the contract is visible.
- **[Improve]** Rebuilding widgets cell by cell is fine at 20 rows. **When** you need more (sorting, paging, thousands of rows): switch to `QTableView` + `QAbstractTableModel`, with a delegate for the combo box.
- **[Improve]** UI imports SQL constants and calls `repository.get_events(query=...)`. Give the repository named methods (`get_unapproved_os_events(limit)`, `get_browser_events(os_event_id)`) so SQL never leaves the DB layer.

## `draggable_button.py`
- **[Bug]** Lines 68-72 (comment: "this got broken"): the release compares the mouse position with `_last_mouse_y`, which `mouseMoveEvent` updates on every move. The difference at release is ~0, so `is_dragged` becomes `False` and a drag also counts as a click → the panel slides. **Cause:** `_drag_start_y` is declared (line 19) but never set. **How:** set `_drag_start_y` in `mousePressEvent` and compare against it on release.
- **[Improve]** `slide()` imports `TelemetryPanel` only to call `panel.slide(...)`. The button knows the panel's geometry and controls it. Emitting a signal (`slide_requested(strategy)`) and letting `screen.py` coordinate both widgets removes the coupling.
- **[Improve]** Magic `- 50` (line 95) and `+ 1` (lines 105-106). Name them (`PANEL_MARGIN`, ...).
- **[Improve]** Line 124: `self._original_icon.pixmap(self.iconSize())` depends on icon size at call time; create the rotated variants once in `__init__`.

## `telemetry_panel.py`
- **[Bug]** Line 13: assigns the instance's computed width to the **class** attribute `TelemetryPanel.PANEL_WIDTH`. Every panel instance shares (and overwrites) it. Use `self._panel_width`.
- **[Risk]** Line 13: `screen_size * 0.7` is a float; `setFixedWidth` expects `int`. Wrap in `int(...)`.
- **[Improve]** `__SIZE_PERCENTAGE` uses name mangling for no reason; a single underscore is the convention for "private".
- **[Improve]** `screen_size` is actually screen *width*. Name it so.

## `screen.py`
- **[Improve]** Clean composition-root style (`create_*`, `connect_signals`, `main`). Good.
- **[Improve]** Line 45: "temp" Exit button. The tray icon was meant for this — wire tray "Exit" to `QApplication.quit` and remove the button. Use `QSystemTrayIcon` (Qt already provides it) instead of `pystray`, so the tray runs on the Qt event loop.
- **[Improve]** Dashboard tab is empty — hide it until it has content.
- **[Improve]** Opens its own connection to the server DB file while the API writes to it. Enable WAL once (`PRAGMA journal_mode=WAL`) so readers don't block the writer.

## `tray_icon.py`
- **[Bug]** Line 4: `from ..configs import MEDIA_FOLDER` — there is no `event_classifier/configs.py`. Import fails. `MEDIA_FOLDER` is in `shared.configs`.
- **[Bug]** Line 24: `icon.run()` at module level blocks forever on import.
- **[Improve]** `pystray`, `Pillow` are not in requirements. See `screen.py` note: use `QSystemTrayIcon` and drop both deps.

## `tables/column.py`, `enums.py`
- **[Improve]** `hidden: bool|None = False` — `None` has no meaning here; use `bool`.
- **[Improve]** `text_alignment: str` → use an enum or `Qt.AlignmentFlag` directly to avoid string typos (`"centre"`).
