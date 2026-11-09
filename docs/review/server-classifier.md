# Server — Event classifier backend & training (`server/event_classifier/backend/`)

Score: **5/10** — good modelling instincts; the train/serve boundary is where it breaks.

---

## `classifier.py`
- **[Bug]** Bare `except:` + implicit `None` return → crash in caller. Critical bug #7.
- **[Bug]** `HardCodedClassifier` returns an enum, `MLClassifier` a string → insert fails. Critical bug #8.
- **[Bug]** `HardCodedClassifier` returns confidence `100`; ML returns `0..1`. The UI also writes `100` for user labels (`table_widgets.py:100`). One column, two scales. Use `1.0`.
- **[Bug]** `HardCodedClassifier.activity_map` uses `"Code.exe"`, `"Steam.exe"`; the notebook data uses lowercase (`code.exe`, `steam.exe`). Normalize with `.lower()` on both sides.
- **[Improve]** `LLMClassifier` is a stub with a hard-coded prompt that returns `None`. Either finish it or remove it, along with the top-level `from ollama import chat` that makes `ollama` a hard dependency.
- **[Risk]** `MLClassifier.__init__` loads a pickle (`joblib.load`). Pickles execute code on load and break across sklearn versions. Fine for your own file — but record the sklearn version next to the model (e.g. `event_classifier.meta.json`) and check it on load.
- **[Improve]** `Classification.classified_at` is annotated `datetime` but receives a string from the processor and a `datetime` from the UI. Pick one (datetime) and format in the repository.
- **[Improve]** `Classification` lives in the classifier module but is imported by event, processing, repository and UI. It's a shared domain type; move it to a `domain`/`models` module to avoid the import web (and the `TYPE_CHECKING` workarounds).
- **[Improve]** `_classify(self, event = None)` — the default `None` is never valid. Remove it.
- **[Improve]** Convert numpy types here: `return float(confidence), str(predicted_class)`.

## `pipeline.py`
- **[Bug]** Return annotation `-> "Event"`; it returns `(confidence, class)`. Fix the annotation.
- **[Improve]** Each `ClassifierPipeline` gets its own `EventFeatureExtractor()` (`api.py:30-32`), so features are computed once per classifier. Extract once in the processor and pass the result to each classifier.

## `event_feature_extractor.py`
- **[Bug]** Swapped tuple unpacking — critical bug #3.
- **[Bug]** Line 96: format string is hard-coded (`"%Y-%m-%d %H:%M:%S"`) instead of `TIMESTAMP_FORMAT`. One config change and only half the code follows.
- **[Improve]** 10 numbered fields + a 13-value tuple + 19 keyword assignments. **How:** build the features as a `dict` in a loop (`for i in range(1, 6): features[f"previous_event_{i}_executable"] = ...`) and return the dict. `MLClassifier` turns it into a one-row DataFrame directly. This removes ~60 lines and the whole class of order bugs.
- **[Improve]** `get_time_info` accepts both `Event` and `dict` via `isinstance`. Normalize previous events into one type when parsing the request instead.
- **[Improve]** Line 117-130: `try/except IndexError` as loop control. `previous = event.previous_events[i] if i < len(event.previous_events) else None` is clearer.
- **[Improve]** `-> tuple[any]`: `any` is the builtin function, not `typing.Any`. Use `Any` (or the dict return above).

## Train/serve skew (cross-file)
- **[Risk]** The same features are implemented twice: pandas code in the notebook and Python code in `EventFeatureExtractor`. Bug #3 is exactly the result of two implementations drifting.
  **How:** make the notebook call `EventFeatureExtractor` (or a shared `build_features(df)` function) to create the training frame. One implementation, used by both.
  **When:** before the next retrain.
- **[Risk]** Browser events are filtered with `executable NOT IN ('chrome.exe')` in the notebook; the agent recognizes 6 browsers (`agent.py:72-79`). Use the same constant in both.

## `classifier_training.ipynb`
- **[Bug]** Training labels include AI predictions — critical bug #6.
- **[Risk]** Random `train_test_split` on time-series data. Neighbouring events share `previous_event_*` features and titles, so near-duplicates land in both train and test and accuracy looks better than it is. **How:** split by time (train on older, test on newest 20%), or `GroupKFold` grouped by day.
- **[Improve]** Hyperparameters are tuned with CV on train, then each config is compared on the same test set several times (cells 42, 50, 52, 54). The test set becomes part of model selection. Keep test for the single final evaluation.
- **[Improve]** Report `f1_macro` (already used in grid search) next to accuracy everywhere — classes are imbalanced (`value_counts` in cell 5).
- **[Improve]** Cells 36-40: manual example rows use `'week_day': 'Saturday'` while training uses integers 0-6, and include columns the model doesn't use (`num_unique_urls`, …). These checks don't test what the model sees. Remove or build them with the feature extractor.
- **[Improve]** `models` is redefined as a list then dict; `perform_grid_search` reads the global. Pass arguments explicitly.
- **[Improve]** The final pipeline is fit on `X_train` only. After selection, refit on all labelled data before `joblib.dump`.
- **[Improve]** `pd.read_sql_query("../../db/telemetry.db")` — relative path breaks when the notebook is opened from another directory. Use `shared.configs.DB_PATH`.
- **[Improve]** Commit notebooks without outputs (`nbstripout`) to keep diffs reviewable. **When:** as long as the notebook is in git.
- **[Improve]** Once the pipeline is stable, move training into `train.py` (load → features → fit → evaluate → dump with metadata). The notebook stays for exploration. **When:** when you retrain regularly.

## `event_classifier.joblib` (2.4 MB in git)
- **[Improve]** Every retrain adds another 2.4 MB to the repo history permanently. **How:** Git LFS, or a GitHub release asset, with the path in config. **When:** before the second retrain is committed.
