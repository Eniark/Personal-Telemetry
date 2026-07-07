package com.example.personaltelemetry.app.viewModel

import android.content.Context
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.example.personaltelemetry.app.backgroundWorker.WorkerManager
import com.example.personaltelemetry.app.database.ActivityEventDao
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.TelemetryRepository

class TelemetryViewModel(
    private val repository: TelemetryRepository,
    private val workerManager: WorkerManager
): ViewModel()  {

    var hasUsageStatsPermissions by mutableStateOf(false)
        private set // anyone can read this attribute but only TelemetryViewModel can modify it
    var hasLocationPermissions by mutableStateOf(false)
        private set
    var numberOfSentEvents = repository.eventsSentCount;
    var numberOfStoredEvents = repository.eventsStoredCount;

    var isTracking by mutableStateOf(workerManager.isWorkerRunning())
        private set

    fun updateLocationPermissions(value: Boolean) {
        hasLocationPermissions = value
    }

    fun updateUsageStatsPermissions(value: Boolean) {
        hasUsageStatsPermissions = value
    }
    fun onToggleTracking() {
        if (hasUsageStatsPermissions && hasLocationPermissions) {
            isTracking = !isTracking
            if (isTracking) {
                workerManager.startTracking()
            }
            else {
                workerManager.stopTracking()
            }
        }



    }

}


class TelemetryViewModelFactory( // the factory was created because Android specifically manages the viewModel. When creating manually a new TelemetryViewModel -> Android stops managing it, so when a screen rotates -> the TelemetryViewModel is recreated and all state is lost.
    private val workerManager: WorkerManager,
    private val repository: TelemetryRepository
) : ViewModelProvider.Factory {

    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(TelemetryViewModel::class.java)) { // Checks is TelemetryViewModel inherits from ViewModel class
            return TelemetryViewModel(repository, workerManager) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}