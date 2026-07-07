package com.example.personaltelemetry.app.backgroundWorker

import android.content.Context
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkInfo
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

class WorkerManager (
    private val context: Context
) {
    val UNIQUE_WORKER_NAME = "Personal Telemetry Worker"

    fun isWorkerRunning(): Boolean {
        val workInfos = WorkManager.getInstance(context)
            .getWorkInfosForUniqueWork(UNIQUE_WORKER_NAME)
            .get()

        return workInfos.any { it.state == WorkInfo.State.RUNNING }
    }


    fun startTracking() {
        val request = PeriodicWorkRequestBuilder<CustomWorker>(
            CustomWorker.TRACKING_WINDOW_MINUTES, TimeUnit.MINUTES
        )
            .build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(UNIQUE_WORKER_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request)
    }

    fun stopTracking() {
        WorkManager
            .getInstance(context)
            .cancelUniqueWork(UNIQUE_WORKER_NAME)
    }

}