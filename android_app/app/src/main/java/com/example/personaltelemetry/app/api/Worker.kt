package com.example.personaltelemetry.app.api

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.app.AppOpsManager
import android.os.Process
class TelemetryRepository {
    suspend fun sendEvent(event: ActivityEvent) {
        ApiClient.api.sendEvent(event)
    }
}

class MyWorker(appContext: Context, params: WorkerParameters) : CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("WORKER", "Running background task")

            val event = ActivityEvent(
                packageName = "com.whatsapp",
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
}


fun checkAccessPermission(context: Context): Boolean {
    val appOps = context.getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager

    val mode = appOps.checkOpNoThrow(
        AppOpsManager.OPSTR_GET_USAGE_STATS,
        Process.myUid(),
        context.packageName
    )

    Log.d("PERMISSIONS STATUS", mode.toString())

    return mode == AppOpsManager.MODE_ALLOWED
}