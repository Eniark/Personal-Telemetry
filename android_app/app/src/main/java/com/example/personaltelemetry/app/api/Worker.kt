package com.example.personaltelemetry.app.api

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

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