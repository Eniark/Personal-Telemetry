# The Roast 🔥

*A summary of the review, written for people who find the other 13 files too polite.*

Every claim below is a real finding from this review. Nothing is invented. Sadly, nothing had to be.

---

## Welcome to Personal-Telemetry

The project that answers one question: *"What if you built a full surveillance system on yourself, and then made sure the data couldn't be trusted?"*

Four components, three languages, two databases, one machine learning model and zero tests. Ambitious. Very ambitious. Like trying to build a house by starting with the smart doorbell.

---

## 🗄️ The Database: Schrödinger's Schema

The schema in git **cannot create a database**. The `duration_seconds` column confidently does math on `start_timestamp` and `end_timestamp`, two columns that exist only in the author's imagination. The real ones are called `event_start_time` and `event_end_time`. Close, but SQLite doesn't do "close."

How does it work on your machine, then? Easy: your actual database was edited by hand, live, like a surgeon operating on himself with a mirror. The schema in the repo is fan fiction about the real one.

Bonus round: the `INSERT` writes to `model_confidence`, a column no `CREATE TABLE` has ever heard of. The foreign key points at `os_event`, a table that doesn't exist (it's `os_events`, plural, a detail as minor as a house number). And `PRAGMA foreign_keys = ON` is set on a connection that closes three lines later, which is like locking the door of a building you're demolishing.

The latest commit message proudly says *"Created views for aggregating the data."* The views are not in the commit. They're not anywhere in the repo. They are in the same place as the `start_timestamp` column: in your heart.

---

## 🤖 The Machine Learning: An AI That Grades Its Own Homework

Let's walk through the ML pipeline, slowly, because it clearly hasn't been walked through before.

1. The model predicts a category for every event.
2. If it's more than 90% sure, it gets **auto-approved**, so a human never looks at it.
3. The training query then takes every event with a label, **including the AI's own guesses**.
4. Retrain. The model learns from itself. Repeat.

This isn't machine learning. It's a confidence spiral. It's a student who writes the exam, grades it, gives himself an A, then studies his own answers for the next exam. In a year it will be 100% accurate and 100% wrong.

And that's when the features are right. They aren't. `get_previous_events_info` returns `(executable, publisher, executable, publisher…)`, and the caller unpacks it as `(publisher, executable, publisher, executable…)`. Thirteen values in a positional tuple, and the author got the order backwards. So in production, the model trained on "previous app was `code.exe`" is being told "previous app was `Microsoft Corporation`." It's still predicting with 0.9 confidence, though. Love the attitude.

Then there's the train/test split: random, on time-series data where neighbouring rows share the same features. That's not a test set, it's an answer key with the questions shuffled. And the test set gets evaluated four times during model selection, until it stops being a test and becomes a long-term relationship.

The result is a three-model soft-voting ensemble of Logistic Regression, SVC and Random Forest, weighing 2.4 MB, committed straight into git, to tell apart **five categories**. Nobody has checked whether it beats "`steam.exe` means gaming." My money's on the lookup table.

Special mention to the `LLMClassifier`, which imports `ollama`, builds a lovely prompt and returns `None`. It's not a classifier, it's a mood. When enabled, the caller tries to unpack that `None` into two variables and the request dies. The bare `except:` around it catches every exception in the known universe and then does nothing useful with any of them.

---

## 📱 The Android App: Quantum Sessions

The phone tracks app sessions by storing them in a map keyed by package name. Use Instagram three times in 15 minutes and you get **one** session: it starts at your last open and ends at your last close. If you reopened it after your last close, congratulations, your session has a **negative duration**. You have used Instagram for minus four minutes. Physicists are on their way.

Sessions crossing the 15-minute window boundary are simply deleted. The longest sessions, the only ones that matter, are the ones that get lost. It's a fitness tracker that only counts steps shorter than one metre.

Every new event is also sent **twice**: once from the "just saved" list and once from the "unsent events" list it was just saved into. The duplicates have `id = 0`, so they can never be marked as sent. Some of them never arrive anyway, because the server requires `description`, `developer` and `appName` to be non-null, the phone happily sends `null`, and the server answers `422`. The worker's response to a permanent validation error is `Result.retry()`. Forever. Every 15 minutes. Like a pigeon pecking a button that has never once dispensed food.

On Android 11+, the app can't even see other apps' info without a `<queries>` block in the manifest. There isn't one. So most app names come back `null`, which helps cause the 422, which feeds the infinite retry. It's not a bug, it's an ecosystem.

The release build doesn't compile, because `API_BASE_URL` only exists in `debug`. Nobody has ever built a release. Nobody has ever needed one. That's fine. It's the most honest thing in the repo.

And the cherry on top: the MAC address and LAN IP of your PC are hard-coded in `MainScreen.kt`, in a **public GitHub repository**. To send a Wake-on-LAN packet to a unicast address of a machine that's asleep and has no ARP entry. It's a doorbell wired to a house that's been demolished, and the address is on a billboard.

The app also asks for **fine location permission** to start tracking. It never uses location. The only class that would, `WifiService`, is called by nothing. Asking for GPS access to do nothing with it is the most Big Tech thing in the entire codebase.

---

## 🪟 The Windows Agent: It Works If You Never Look At It

Credit where it's due: there's a local SQLite queue with exponential backoff. That is a genuinely good idea. Enjoy this compliment; it's the last one.

The sender loop uses `event_queue`, `repository` and the server URL as **module globals** defined under `if __name__ == "__main__"`. It works perfectly, as long as nobody imports it, tests it, or looks at it funny.

The env var names are crossed like wires in a homemade bomb: `WINDOWS_AGENT_SERVER_HOST` holds a **port**, and `TELEMETRY_SERVER_HOST` reads `WINDOWS_AGENT_SERVER_HOST`. It works only because everything runs on one computer, where host and port confusion can't hurt you. Yet.

`requests.post` has no timeout. If the server ever accepts a connection and hangs, the sender thread waits forever, like a dog at the train station. And retries only happen when you switch windows. Watch a two-hour movie after an outage and nothing gets sent for two hours, because the retry logic is waiting for you to alt-tab.

The retry delay starts at 5 seconds and "resets" to 60 on success. Reset is a strong word for "changes to a different number."

There's no idle detection either. Leave your PC on a YouTube tab overnight and the telemetry records an eight-hour deep-focus session. According to this data you are the most productive human alive. The data is not to be trusted.

---

## 🌐 The Browser Extension: Selective Amnesia

When Chrome loses focus, the extension sets `currentTab = null` **without saving it first**. Every time you switch from the browser to another app, the last tab's time is thrown away. When focus returns, nothing is registered until you switch tabs. The extension tracks your browsing the way a goldfish tracks its laps.

It polls every 4 seconds with `setInterval` in a Manifest V3 service worker, which Chrome kills after 30 seconds of idling. So the timer is a timer the way a sandcastle is a house.

The `chrome.windows.WINDOW_ID_NONE` event, the exact signal for "browser lost focus", is received and **explicitly ignored**, then rebuilt badly with polling. That's like getting a text saying "I'm outside" and then checking the window every 4 seconds.

If the Windows agent is down, events are dropped. The `storage` permission that would fix this is declared in the manifest and never used. The `idle` permission that would fix the AFK problem is also declared and never used. The manifest is a wishlist.

---

## 🖥️ The Desktop UI: Click Once, Fire Many

Every press of Refresh connects the click handler **again**. Refresh ten times and one click fires ten handlers. It's not a UI, it's a multiplayer game where every player is you.

The draggable button has a comment that says, and I quote, `# this got broken.` It did. The variable meant to fix it, `_drag_start_y`, is declared and never set. You found the bug, wrote a comment about it, and then left. Like noticing a gas leak and putting up a sticky note.

The tray icon module imports from `..configs`, a file that does not exist, and then calls `icon.run()` at module level, which would block forever anyway. It is a module that can't be imported, and if it could, you'd regret it.

User-approved labels get confidence `100`. The model gives `0.0`–`1.0`. Same column. So the database believes human certainty is a hundred times stronger than machine certainty, which, given everything above, is the most accurate number in the project.

---

## 🧰 Tooling: The "It Works on My Machine" Starter Pack

- `startup.bat` launches `server.api.main` and `agents.windows.main`. **Neither exists.** The launcher has never launched.
- `requirements.txt` is a full `pip freeze` with ~80 packages that somehow **misses** `pandas`, `numpy`, `scikit-learn`, `joblib`, `pystray` and `Pillow`, the ones the code actually imports. It does include gRPC, protobuf, PySide6 WebEngine and PDF support for a UI that uses neither the web nor PDFs. It's a suitcase packed for the wrong country.
- It also installs both `dotenv` and `python-dotenv`. Belt and suspenders, for a library you then use wrong.
- `validate_env_variable` overwrites the variable's name with its value, so its only job, telling you which variable is missing, prints `"None" must be defined`. The validator needs a validator.
- `.env.example` lists one variable, empty, and omits the ones the agent requires to start.
- `.gitignore` excludes `src/test/` and `src/androidTest/`. Not that there were tests to protect. It's a bouncer guarding an empty club.
- Zero tests. Zero CI. Zero linting. The bugs above were found by reading the code, which is apparently a technique nobody had tried yet.

---

## 📝 Code Style: Lies, Damned Lies and Type Annotations

- `event_start_time: int`, always assigned a string.
- `self.events: list[Event]`, assigned a dict.
- `-> "Event"`, returns a tuple.
- `-> bool`, returns `None`.
- `-> tuple[any]`, where `any` is the built-in **function**, not `typing.Any`. The type hint is technically a hint that the return value is a tuple of a function.

These types aren't annotations. They're horoscopes.

Comments include gems like `// suspend = async` and `// ?: if (INSTANCE==true)`. This isn't documentation, it's a Kotlin tutorial written in the margins of the production code. Meanwhile the parts that actually need explaining, like why a 13-value tuple is ordered the way it is, have no comment at all. That one would have helped.

The same "OS event" exists in roughly **eight** shapes: an agent dict, a queue-DB row, a pydantic schema, a dataclass, an `EnrichedEvent`, a server-DB row, a notebook DataFrame and a UI tuple. Each conversion between them is another chance to swap two fields, and the codebase takes those chances enthusiastically.

---

## 🔒 Privacy: You've Built Spyware. On Yourself. Badly Secured.

Every window title, every URL with full query strings and every app you open is sent over **plain HTTP** to a server on `0.0.0.0` with **no authentication**, so anyone on your Wi-Fi can post events into your life. Window titles and URLs are also logged at `INFO` level into plain-text files with no rotation, so you have a second, unindexed copy of your browsing history. The Android DB goes into Google Drive backups via `allowBackup="true"`. And it all lives inside the repo folder, one `git add -f` away from being public, next to your MAC address.

The NSA would never. Mostly because they'd be embarrassed.

---

## 🏁 Final Score: 5.5/10

That's not a typo, and that's not pity. Under all of this is a genuinely good design: agents feeding a server, a durable queue with backoff, OpenTelemetry tracing that most professional teams don't bother with, a clean MVVM Android app, and a notebook that at least *tried* grid search before picking a model. The architecture diagram is better than the code. That's rare, and it's fixable.

So here's the deal. Fix the schema so it runs on a clean machine. Unswap the features. Stop training the model on its own hallucinations. Add a timeout. Write five tests. Then come back, and this roast will have to find new material.

Right now, the most accurate telemetry this project produces is how much time you spent writing it.

— *Your reviewer, who read every line so you'd have to fix every one*
