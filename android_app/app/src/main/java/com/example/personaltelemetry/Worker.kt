package com.example.personaltelemetry

import android.content.Context
import android.util.Log
import androidx.work.Worker
import androidx.work.WorkerParameters

class MyWorker(appContext: Context, params: WorkerParameters) :
    Worker(appContext, params) { // Android can run this piece of code in the background

    override fun doWork(): Result {

        // Your logic here
        Log.d("WORKER", "Running background task TEST")

        return Result.success()
    }
}