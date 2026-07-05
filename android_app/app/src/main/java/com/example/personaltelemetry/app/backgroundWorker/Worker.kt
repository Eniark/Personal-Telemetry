package com.example.personaltelemetry.app.backgroundWorker

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.os.Process
import androidx.room.Room
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.AppDatabase
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.TelemetryApi
import com.example.personaltelemetry.app.repository.TelemetryRepository
import com.example.personaltelemetry.app.system.WifiService

class CustomWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("WORKER", "Running background task")
            val events = getMostRecentActivities()

            val db = getDatabase(applicationContext)
            val repository = TelemetryRepository(db.activityEventDao(), ApiClient.api)
            val wifiService = WifiService(applicationContext)

            repository.saveEventsToLocalDb(events)
            Log.d("INFO", "Sent message to the API")

            if (wifiService.isConnectedToHomeWifi()) {
                repository.sendEventsToAPI(events)
            }
            Result.success()
        } catch (e: Exception) {
            Log.e("WORKER", "Failed", e)
            Result.retry()
        }
    }

    fun getMostRecentActivities(): List<ActivityEvent> {
        val usageStatsManager =
            applicationContext.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager

        val endTime = System.currentTimeMillis()
        val startTime = endTime - 1000 * 60 * TRACKING_WINDOW_MINUTES // last 15 minutes

        val stats = usageStatsManager.queryUsageStats(
            UsageStatsManager.INTERVAL_DAILY,
            startTime,
            endTime
        )

        val events: List<ActivityEvent> = stats.filter {
            it.lastTimeUsed > 0 // get apps with > 0 time usage
        }.map {
            val pm = applicationContext.packageManager
            val appName = try {
                val appInfo = pm.getApplicationInfo(it.packageName, 0)
                pm.getApplicationLabel(appInfo).toString()
            } catch (e: Exception) {
                it.packageName
            }

            ActivityEvent(
                name = appName,
                usedAtTimestamp = System.currentTimeMillis(),
                sentToApi = false
            )
        }

        return events
    }

    companion object {
        const val TRACKING_WINDOW_MINUTES: Long = 15; // Check every 15 minutes the past 15 minutes. Rolling window.
    }
}


