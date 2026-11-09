# Browser extension (`agents/browser/`)

Score: **5/10** — compact and readable; MV3 service-worker lifecycle is not taken into account.

---

## `main.js`
- **[Bug]** Lines 68-75: when the browser loses focus, `currentTab` is set to `null` **without sending it**. The time on the last active tab before switching to another app is lost every time.
  **How:** call `saveCurrentSession(currentTab)` before clearing it.
- **[Bug]** Lines 60-66: on focus return, `userTracked` becomes `true` but no tab is registered. Nothing is recorded until the next tab switch or page load. **How:** query the active tab and `registerTab()` it here.
- **[Improve]** Lines 60-63: `windowId === -1` (`chrome.windows.WINDOW_ID_NONE`) is the exact "browser lost focus" signal, but it's ignored and replaced by polling every 4 s. Handle focus loss here and remove the interval.
- **[Risk]** Line 5: `setInterval` in an MV3 service worker. Chrome terminates idle service workers after ~30 s; timers and in-memory state (`tabTracker`) are lost. **How:** event-driven only (the listeners already restart the worker), and keep `currentTab` in `chrome.storage.session` so a restarted worker can close the previous segment.
- **[Improve]** Lines 7-27: `onStartup` and `onInstalled` handlers are identical — extract `registerActiveTab()`.
- **[Improve]** Line 46: `chrome.tabs.query` with a callback while everything else uses `await`. Use one style.
- **[Improve]** `console.log` debug lines left in the hot path; remove or gate behind a `DEBUG` flag.

## `TabTracker.js`
- **[Risk]** Line 13: if the Windows agent isn't running (or restarting), the event is dropped — no retry, no buffer. The `storage` permission is declared but unused. **How:** append to a small queue in `chrome.storage.local`, flush on next successful POST.
- **[Bug]** Line 40: `chrome.tabs.get()` **throws** for a closed tab id; it doesn't return `undefined`. The `else` branch (lines 48-51) is unreachable and the exception is unhandled. Wrap in `try/catch`.
- **[Improve]** Line 44: `{...this.currentTab}` turns `null` into `{}`, which is why `saveCurrentSession` needs the `Object.keys(...).length === 0` check. Keep `null` and check `if (!tab)`.
- **[Improve]** Line 13: URL hard-coded (`http://127.0.0.1:8080`). Put it in one constant at the top of the file (it's also in `manifest.json`).
- **[Improve]** Titles are taken on `status === "complete"`; SPAs (YouTube, Gmail) change title later. Listening to `changeInfo.title` gives correct titles — useful, since title is the strongest feature in your model.
- **[Info]** Privacy: full URLs (including query strings with tokens/search terms) are sent and stored. If you only need the domain + path for classification, strip query and fragment in the extension.

## `Tab.js`
- **[Improve]** Missing semicolons on two lines while the rest of the file uses them. Add Prettier (zero-config) to settle style.

## `manifest.json`
- **[Improve]** `idle` permission is declared but unused. Either remove it or use `chrome.idle.onStateChanged` to close the current tab segment when the user is AFK — same problem as the Windows agent's idle time.
- **[Improve]** `name` is "Minimal Tab Time Tracker" — rename to match the project so it's identifiable in `chrome://extensions`.
