# Android app (`agents/android/`)

Score: **6/10** — good structure (Room, WorkManager, ViewModel factory, Flows). Data collection and sync have correctness gaps.

Kotlin paths below are relative to `app/src/main/java/com/yhulivatiy/personaltelemetry/`.

---

## `app/backgroundWorker/Worker.kt`
- **[Bug]** Lines 178-195: sessions are keyed by `packageName` in a map, so an app used several times in the 15-minute window keeps only one entry: start = **last** RESUMED, end = **last** PAUSED. If the app was resumed again after its last pause, `end < start` (negative duration). **How:** append a new `ActivityEvent` on each RESUMED→PAUSED pair instead of overwriting.
- **[Bug]** Sessions crossing the window boundary are dropped: still-open at the end → filtered out (`eventEndTime == null`, line 210); in the next run the PAUSED has no RESUMED → `continue` (line 191). Long sessions — the most important ones — are lost. **How:** persist a watermark (last processed timestamp + open session) in `SharedPreferences`/DataStore and query from the watermark, not "now − 15 min".
- **[Bug]** `PeriodicWorkRequest` isn't exact (Doze, flex window). Windows overlap or leave gaps, and overlapping events are re-inserted as new rows because `id = 0` → `@Upsert` always inserts. **How:** the watermark above, plus a unique index on `(packageName, eventStartTime)`.
- **[Bug]** Lines 93-98: `enrichedEvents` were just saved and are also returned by `getUnsentEvents()`, so each new event is sent **twice**. The `enrichedEvents` copies have `id = 0`, so `markAsSent` can't mark them. **How:** send only `repository.getUnsentEvents()` after saving.
- **[Bug]** Lines 202-217: on Android 11+ `getApplicationInfo()` for other apps throws `NameNotFoundException` unless the app declares package visibility (`<queries>` or `QUERY_ALL_PACKAGES`). The manifest has neither, so `isSystem` is `false` and `appName` is `null` for most apps. Add a `<queries>` block (or `QUERY_ALL_PACKAGES` for a personal, non-Play app).
- **[Improve]** `getApplicationInfo` is called twice per package; call it once.
- **[Improve]** `enrichedEvents.size > 5` (line 97): magic number, and also counts the duplicates above. Name it (`MIN_BATCH_SIZE`).
- **[Improve]** `removeSystemEvents()` deletes right after saving. Filter before saving instead.
- **[Improve]** `doWork` is ~90 lines mixing collection, enrichment, persistence and sync. Split into `collect()`, `enrich()`, `sync()`; the worker just calls them. Makes unit tests possible.
- **[Improve]** `catch (e: Exception) → Result.retry()` retries forever on permanent errors (e.g. 422). Return `Result.failure()` for non-retryable errors, `retry()` only for I/O.
- **[Improve]** `TRACKING_WINDOW_MINUTES: Long = 15;` — Kotlin doesn't need the `;`.

## `app/repository/TelemetryRepository.kt`
- **[Bug]** `sendEventsToAPI` serializes `ActivityEvent` directly. Nullable fields → server 422. Critical bug #4.
- **[Improve]** Sending the Room entity couples DB schema and API contract. Map to a `PhoneEventDto` with only the fields the server needs.
- **[Improve]** `getAPIHealth()` before every send costs a round trip and can still race. Just send and handle failure.
- **[Improve]** `private val AndroidAppsDao: AndroidAppsDao` — property names are lowerCamelCase (`androidAppsDao`).
- **[Improve]** `TelemetryApi` and `ApiClient` live in the repository file. Move to `network/`.
- **[Risk]** No OkHttp timeouts configured (defaults are 10 s, fine) but no logging interceptor either — add one in debug to see 422 bodies.

## `app/repository/GooglePlayScraper.kt`
- **[Risk]** Scraping Play Store HTML: selectors break whenever Google changes markup, and it's against Play's ToS. Acceptable for a personal tool; isolate it behind an interface so it can be replaced.
- **[Bug]** Only `HttpStatusException` is caught. Timeouts / `UnknownHostException` propagate and fail the whole worker run.
- **[Bug]** On failure the app is still returned with `isVerified = true` (`Worker.kt:131`), so it's never retried. Return a result type (`AppInfo?` or sealed class) and mark verified only on success.
- **[Improve]** `statusCode == -1` never happens for `HttpStatusException`. Remove.

## `app/database/Database.kt`
- **[Risk]** `version = 14` with `fallbackToDestructiveMigration(true)`: every schema change wipes the DB, including **unsent events**. **How:** `exportSchema = true` + `room.schemaLocation`, and `AutoMigration` for simple changes. **When:** now — it's real data loss on the next schema change.
- **[Improve]** Singleton is correct. The comments explaining `@Volatile`/`synchronized` are good for learning; trim later.

## `app/database/ActivityEvent.kt`, `AndroidApps.kt`, DAOs
- **[Improve]** `ActivityEvent` uses `var` for `appName`, `eventStartTime`, `eventEndTime` because the worker mutates them while building sessions. Entities should be immutable; build a local mutable session object and convert to the entity at the end.
- **[Improve]** `AndroidApps` (plural) is one app — `AndroidApp`.
- **[Improve]** `clearTable();` — trailing semicolons; and `clearTable()` is only used in commented-out code in `Main.kt`.
- **[Improve]** Add an index on `sentToApi` once the table grows (queried every run).

## `Main.kt`
- **[Improve]** Dependencies (DB, repository, scraper, WorkerManager) are constructed in the Activity and again in the Worker. **How:** a simple `AppContainer` created in a custom `Application` class; Activity and Worker both read from it. No Hilt needed at this size.
- **[Improve]** Remove the commented-out `clearTable` block.

## `app/viewModel/ViewModel.kt`
- **[Improve]** `var numberOfSentEvents`, `var numberOfStoredEvents` → `val`.
- **[Improve]** `isTracking` is a public `MutableStateFlow`; anyone can set it. Expose `StateFlow` with a private mutable backing field. Also mixes `mutableStateOf` and `StateFlow` for the same kind of state — pick one (StateFlow is preferred in ViewModels).
- **[Improve]** `public val workerManager` — make it private.
- **[Bug]** `onToggleTracking` requires location permission. Usage tracking doesn't need location; location is only for `WifiService`, which nothing calls. Drop the requirement (and the `ACCESS_FINE_LOCATION` permission) until a feature uses it.

## `app/ui/MainScreen.kt`
- **[Bug]** Lines 365-369: the permission launcher callback ignores the result and writes the **old** value: `setLocationPermissions(hasLocationPermission)`. Use the lambda parameter: `{ granted -> setLocationPermissions(granted) }`.
- **[Risk]** Lines 153-156: MAC address and target IP of your PC are hard-coded in source (and now public on GitHub). `192.168.0.106` is a unicast address — WoL to unicast relies on a cached ARP entry, which usually expires while the PC sleeps. Use the subnet broadcast (`192.168.0.255`) and move both values to `local.properties` → `BuildConfig`.
- **[Improve]** `PermissionsService(context)` (line 69) and `ConnectivityService(context)` (line 325) are re-created on every recomposition. `remember { }` them, or move the checks into the ViewModel.
- **[Improve]** Unused: `scope`, `cs` in `StartTrackingButton`; commented `getDatabase`.
- **[Improve]** Hard-coded colors (`Color(0xFF8e94f2)`) next to a theme; put it in the color scheme.
- **[Improve]** `ui/theme/` (Color.kt, Theme.kt, Type.kt — `PersonalTelemetryTheme`) is the Android Studio template and is unused; `app/ui/` has the real theme. Delete the template.

## `app/utils/WoL.kt`
- **[Improve]** `suspend fun` but does blocking socket I/O; it relies on the caller using `Dispatchers.IO`. Wrap the body in `withContext(Dispatchers.IO)` so the function is safe to call from anywhere.
- **[Improve]** `require(mac.length == 12)` without a message; add one (`"Invalid MAC: $macAddress"`).

## `app/system/WifiService.kt`, `ConnectivityService.kt`
- **[Improve]** `WifiService` is unused. `wifiManager.connectionInfo` is deprecated since API 31. Delete until needed.
- **[Improve]** `ConnectivityService` excludes Ethernet/VPN transports; `NET_CAPABILITY_VALIDATED` is the usual check. Better: let WorkManager handle it with `Constraints(requiredNetworkType = NetworkType.CONNECTED)` on the request.

## `app/build.gradle.kts`, `AndroidManifest.xml`
- **[Bug]** `API_BASE_URL` is defined only for `debug`. `assembleRelease` fails to compile (`BuildConfig.API_BASE_URL` unresolved). Define it in `defaultConfig`, override in `debug`.
- **[Risk]** `usesCleartextTraffic="true"` app-wide. **How:** a `network_security_config.xml` allowing cleartext only for your LAN IP.
- **[Risk]** `allowBackup="true"` with untouched template backup rules: your usage history goes to Google Drive backup. Exclude the DB or set `allowBackup="false"`.
- **[Improve]** Room, Retrofit, jsoup versions are inline strings while the rest uses the version catalog (`libs.*`). Move them to `libs.versions.toml`.
- **[Improve]** `JavaVersion.VERSION_11`; current AGP templates use 17. Low priority.
