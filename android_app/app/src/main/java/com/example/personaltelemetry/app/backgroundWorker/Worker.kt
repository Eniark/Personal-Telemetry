package com.example.personaltelemetry.app.processingLayer

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.app.AppOpsManager
import android.app.usage.UsageStatsManager
import android.os.Process
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.ApiClient

class TelemetryRepository {
    suspend fun sendEvent(event: ActivityEvent) {
        ApiClient.api.sendEvent(event)
    }
}

class CustomWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("WORKER", "Running background task")
            val usageStatsManager =
                applicationContext.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager

            val endTime = System.currentTimeMillis()
            val startTime = endTime - 1000 * 60 * CustomWorker.TRACKING_WINDOW_MINUTES // last 10 minutes

            val stats = usageStatsManager.queryUsageStats(
                UsageStatsManager.INTERVAL_DAILY,
                startTime,
                endTime
            )

            val recentApp = stats
                .maxByOrNull { it.lastTimeUsed }

            val packageName = recentApp?.packageName
            val event = ActivityEvent(
                packageName = packageName,
                timestamp = System.currentTimeMillis()
            )

            TelemetryRepository().sendEvent(event)
            Log.d("INFO", "Sent message to the API")

            Result.success()
        } catch (e: Exception) {
            Log.e("WORKER", "Failed", e)
            Result.retry()
        }
    }

    companion object {
        const val TRACKING_WINDOW_MINUTES: Long = 15; // Check every 15 minutes the past 15 minutes. Rolling window.
    }
}


fun checkAccessPermission(context: Context): Boolean {
    val appOps = context.getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager

    val mode = appOps.checkOpNoThrow(
        AppOpsManager.OPSTR_GET_USAGE_STATS,
        Process.myUid(),
        context.packageName
    )

    return mode == AppOpsManager.MODE_ALLOWED
}