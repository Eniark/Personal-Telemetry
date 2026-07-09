package com.example.personaltelemetry.app.backgroundWorker

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.content.pm.ApplicationInfo
import android.os.Process
import androidx.room.Room
import androidx.work.WorkManager
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.AppDatabase
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.GooglePlayScraper
import com.example.personaltelemetry.app.repository.TelemetryApi
import com.example.personaltelemetry.app.repository.TelemetryRepository
import com.example.personaltelemetry.app.system.ConnectivityService
import com.example.personaltelemetry.app.system.WifiService
import kotlinx.coroutines.launch

class CustomWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("WORKER", "Running background task")
            var activityEvents = getMostRecentActivities()
            val db = getDatabase(applicationContext)
            val scraper = GooglePlayScraper()
            val repository = TelemetryRepository(db.activityEventDao(), db.systemAppCollectionDao(), ApiClient.api, scraper)
            val wifiService = WifiService(applicationContext)
            val connectivityService = ConnectivityService(applicationContext)

            if (connectivityService.isConnectedToNetwork()) {
                activityEvents = postProcessEvents(activityEvents, repository)
            }
            val packageNames: List<String> = activityEvents.map { it.appName }
            val systemApps = repository.getSystemApps(packageNames)
            activityEvents = activityEvents.filter { it.appName !in systemApps }
            val (systemEvents, nonSystemEvents) = separateSystemVsNonSystemEvents(events = activityEvents)
            Log.d("INFO", "Sent message to the API")

            repository.saveSystemEvents(systemEvents)
            repository.saveEventsToLocalDb(nonSystemEvents)
            if (wifiService.isConnectedToHomeWifi()) {
                repository.sendEventsToAPI(nonSystemEvents)
            }

            nonSystemEvents.forEach {
                Log.d("Sending to DB/API", it.toString())
            }

            Result.success()
        } catch (e: Exception) {
            Log.e("WORKER", "Failed", e)
            Result.retry()
        }
    }


    fun separateSystemVsNonSystemEvents(events: List<ActivityEvent>): Pair<List<ActivityEvent>, List<ActivityEvent>> {
        val systemEvents = events.filter { it.isSystemEvent }
        val nonSystemEvents = events.filter { !it.isSystemEvent }

        return systemEvents to nonSystemEvents
    }


    suspend fun postProcessEvents(events: List<ActivityEvent>, repository: TelemetryRepository): List<ActivityEvent> {
        val postProcessedEvents = events.map {
            val (appName, description, isSystemEvent) = repository.getAppInformation(it.appName)

            ActivityEvent(
                id = it.id,
                appName = appName,
                description = description,
                usedAtTimestamp = it.usedAtTimestamp,
                isSystemEvent = isSystemEvent
            )

        }

        return postProcessedEvents
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
                it.packageName // fall back to package name
            }

            ActivityEvent(
                appName = appName,
                usedAtTimestamp = it.lastTimeUsed
            )
        }

        return activityEvents
    }

    companion object {
        const val TRACKING_WINDOW_MINUTES: Long = 15; // Check every 15 minutes the past 15 minutes. Rolling window.
    }
}


