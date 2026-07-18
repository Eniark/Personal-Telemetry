package com.yhulivatiy.personaltelemetry.app.viewModel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.yhulivatiy.personaltelemetry.app.backgroundWorker.WorkerManager
import com.yhulivatiy.personaltelemetry.app.repository.TelemetryRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch

class TelemetryViewModel(
    private val repository: TelemetryRepository,
    public val workerManager: WorkerManager
): ViewModel()  {

    var hasUsageStatsPermissions by mutableStateOf(false)
        private set // anyone can read this attribute but only TelemetryViewModel can modify it
    var hasLocationPermissions by mutableStateOf(false)
        private set
    var numberOfSentEvents = repository.eventsSentCount;
    var numberOfStoredEvents = repository.eventsStoredCount;

    val isTracking = MutableStateFlow(false) //
    init { // is run only on object creation
        viewModelScope.launch {
            isTracking.value = workerManager.isWorkerActive()
        }
    }

    fun updateLocationPermissions(value: Boolean) {
        hasLocationPermissions = value
    }

    fun updateUsageStatsPermissions(value: Boolean) {
        hasUsageStatsPermissions = value
    }
    fun onToggleTracking() {
        if (!hasUsageStatsPermissions || !hasLocationPermissions) {
            return
        }

        if (isTracking.value) {
            workerManager.stopTracking()
            isTracking.value = false
        } else {
            workerManager.startTracking()
            isTracking.value = true
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