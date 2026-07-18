package com.example.personaltelemetry.app.backgroundWorker

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.app.usage.UsageStatsManager
import android.content.pm.ApplicationInfo
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.AndroidApps
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.GooglePlayScraper
import com.example.personaltelemetry.app.repository.TelemetryRepository
import com.example.personaltelemetry.app.system.ConnectivityService

class CustomWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("APP-LOGS:WORKER", "===WORKER STARTING===")
            val db = getDatabase(applicationContext)
            val repository = TelemetryRepository(
                db.activityEventDao(),
                db.androidAppsDao(),
                ApiClient.api,
                GooglePlayScraper()
            )

            val connectivityService = ConnectivityService(applicationContext)
            var collectedEvents = getMostRecentActivities()

            var allApps = repository.getAndroidApps()
            // fetch events which were not enriched yet
            val unverifiedEvents = repository.getUnverifiedEvents()

            val verifiedSystemPackages = allApps
                .filter { it.isVerified && it.isSystem }
                .map { it.packageName }
                .toSet()
            val nonSystemEvents = collectedEvents.filter { it.packageName !in verifiedSystemPackages }
            // Load known apps from local DB
            val knownAppsMap = allApps.associateBy { it.packageName }

            var (knownEvents, newEvents) = splitIntoKnownAndUnknown(knownAppsMap, nonSystemEvents)
            var newApps = newEvents.map {
                AndroidApps(
                    packageName = it.packageName,
                    appName = it.appName,
                    description = it.description,
                    isSystem = false,
                    isVerified = false
                )
            }.distinct()
            val unverifiedApps = allApps.filter { !it.isVerified }
            val verifiedApps = allApps.filter { it.isVerified }
            val appsThatRequireEnrichment = (newApps + unverifiedApps).distinct() // add apps from the database
            val eventsThatRequireEnrichment = newEvents + unverifiedEvents
            var enrichedEvents = listOf<ActivityEvent>();
            var enrichedApps = listOf<AndroidApps>();

            // Scrape metadata for unknown apps
            if (connectivityService.isConnectedToNetwork()) {
                enrichedApps = enrichApps(
                    appsThatRequireEnrichment,
                    repository
                )
            }
            else {
                enrichedApps = appsThatRequireEnrichment
            }
            allApps = verifiedApps + enrichedApps // reassemble all apps collection
            collectedEvents = knownEvents + eventsThatRequireEnrichment // reassemble all collected events collection
            enrichedEvents = enrichEvents(collectedEvents, allApps) // pass all collected events to enrich them
            repository.saveAndroidAppsToLocalDb(enrichedApps)

            // send events to the DB
            // =============================
            Log.d("All Apps", allApps.toString())
            Log.d("All Events", collectedEvents.toString())
            Log.d("Enriched Events", enrichedEvents.toString())
            repository.saveEventsToLocalDb(enrichedEvents)
            repository.removeSystemEvents() // Clean up system events
            // =============================

            // send events to the API
            // =============================
            val apiHealthy = repository.getAPIHealth()

            if (apiHealthy && enrichedEvents.size > 5) {
                // fetch events which were not sent yet
                val pendingEvents = repository.getUnsentEvents()
                enrichedEvents += pendingEvents;
                repository.sendEventsToAPI(enrichedEvents)
                Log.d("APP-LOGS:SentToAPI", "${enrichedEvents.size}, $enrichedEvents")
            }
            // =============================



            Log.d("APP-LOGS:WORKER", "===WORKER SUCCESSFULY FINISHED===")
            Result.success()
        } catch (e: Exception) {
            Log.e("APP-LOGS:WORKER", "Failed", e)
            Result.retry()
        }
    }

    fun splitIntoKnownAndUnknown(knownAppsMap: Map<String, AndroidApps>, nonSystemEvents: List<ActivityEvent>): Pair<List<ActivityEvent>, List<ActivityEvent>> {
        val knownPackages = knownAppsMap.keys
        // Split events into known and new
        // =======================
        var newEvents = nonSystemEvents.filter {
            it.packageName !in knownPackages
        }

        val knownEvents = nonSystemEvents.filter {
            it.packageName !in newEvents.map { unknown -> unknown.packageName }
        }
        // =======================
        return knownEvents to newEvents
    }

    suspend fun enrichApps(apps: List<AndroidApps>, repository: TelemetryRepository): List<AndroidApps> {
        val enrichedApps = apps.map {
            val (appName, description, isSystemEvent) = repository.getAppInformation(it.packageName)

            it.copy(
                appName = appName,
                description = description,
                isVerified = true,
                isSystem = isSystemEvent
            )

        }
        return enrichedApps

    }
    suspend fun enrichEvents(events: List<ActivityEvent>, enrichedApps: List<AndroidApps>): List<ActivityEvent> {
        val appsThatRequireEnrichmentMap = enrichedApps.associateBy { it.packageName }

        val enrichedEvents = events
            .map { event ->
                val enrichedApp = appsThatRequireEnrichmentMap[event.packageName]
                if (enrichedApp != null) {
                    event.copy(
                        appName = enrichedApp.appName,
                        description = enrichedApp.description,
                        isVerified = enrichedApp.isVerified,
                        isSystemEvent = enrichedApp.isSystem
                    )
                }
                else {
                    event
                }
            }

        return enrichedEvents
    }
    fun getMostRecentActivities(): List<ActivityEvent> {
        val usageStatsManager =
            applicationContext.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager

        val endTime = System.currentTimeMillis()
        val startTime = endTime - 1000 * 60 * TRACKING_WINDOW_MINUTES // last 10 minutes
        val stats = usageStatsManager
            .queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY,
                startTime,
                endTime
            )

        val pm = applicationContext.packageManager
        // Filter the apps to non-system apps and apps whose last activity falls between during the time window as usageStatsManager provides aggregated information
        val activityEvents: List<ActivityEvent> = stats.filter {
            val isSystem = try {
                val appInfo = pm.getApplicationInfo(it.packageName, 0)
                (appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0 ||
                        (appInfo.flags and ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0

            }
            catch (e: Exception) {
                false
            }

            it.lastTimeUsed in startTime..endTime && !isSystem
        }.map {
            val appName = try {
                val appInfo = pm.getApplicationInfo(it.packageName, 0)
                pm.getApplicationLabel(appInfo).toString()
            }
            catch (e: Exception) {
                null
            }

            ActivityEvent(
                appName = appName,
                packageName = it.packageName,
                usedAtTimestamp = it.lastTimeUsed
            )
        }

        return activityEvents
    }

    companion object {
        const val TRACKING_WINDOW_MINUTES: Long = 15; // Check every 15 minutes the past 15 minutes. Rolling window.
    }
}


