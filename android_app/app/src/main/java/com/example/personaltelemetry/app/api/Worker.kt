package com.example.personaltelemetry

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.personaltelemetry.app.api.ActivityEvent
import com.example.personaltelemetry.app.api.ApiClient

class MyWorker(appContext: Context, params: WorkerParameters) :
    CoroutineWorker(appContext, params) { // Android can run this piece of code in the background asynchronously

    override suspend fun doWork(): Result {
        return try {

            Log.d("WORKER", "Running background task")

            val event = ActivityEvent(
                packageName = "com.whatsapp",
                timestamp = System.currentTimeMillis()
            )

            ApiClient.api.sendEvent(event)

            Result.success()

        } catch (e: Exception) {
            Log.e("WORKER", "Failed", e)
            Result.retry()
        }
    }
}