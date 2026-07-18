package com.example.personaltelemetry.app.backgroundWorker

import android.content.Context
import android.util.Log
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class WorkerManager (
    private val context: Context
) {
    val UNIQUE_WORKER_NAME = "Personal Telemetry Worker"

    suspend fun isWorkerActive(): Boolean =
        withContext(Dispatchers.IO) {
            val workInfos = WorkManager.getInstance(context)
                .getWorkInfosForUniqueWork(UNIQUE_WORKER_NAME)
                .get()
            Log.d("APP-Logs:Worker", "${workInfos.size}, ${workInfos.toString()}")

            workInfos.any { !it.state.isFinished }
        }


    fun startTracking() {
//        val request = PeriodicWorkRequestBuilder<CustomWorker>(
//            CustomWorker.TRACKING_WINDOW_MINUTES, TimeUnit.MINUTES
//        )
//        .build()

        val request = OneTimeWorkRequestBuilder<CustomWorker>(
        )
            .build()
        WorkManager.getInstance(context).enqueueUniqueWork(UNIQUE_WORKER_NAME, ExistingWorkPolicy.REPLACE, request)

//        WorkManager.getInstance(context).enqueueUniquePeriodicWork(UNIQUE_WORKER_NAME,
//            ExistingPeriodicWorkPolicy.UPDATE,
//            request)
    }

    fun stopTracking() {
        WorkManager
            .getInstance(context)
            .cancelUniqueWork(UNIQUE_WORKER_NAME)
    }

}