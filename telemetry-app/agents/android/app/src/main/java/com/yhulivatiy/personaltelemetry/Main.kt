package com.yhulivatiy.personaltelemetry

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import com.yhulivatiy.personaltelemetry.app.backgroundWorker.WorkerManager
import com.yhulivatiy.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.yhulivatiy.personaltelemetry.app.repository.ApiClient
import com.yhulivatiy.personaltelemetry.app.repository.GooglePlayScraper
import com.yhulivatiy.personaltelemetry.app.repository.TelemetryRepository
import com.yhulivatiy.personaltelemetry.app.ui.AppTheme
import com.yhulivatiy.personaltelemetry.app.ui.TelemetryApp
import com.yhulivatiy.personaltelemetry.app.viewModel.TelemetryViewModel
import com.yhulivatiy.personaltelemetry.app.viewModel.TelemetryViewModelFactory

class Main : ComponentActivity() {
    private val viewModel: TelemetryViewModel by viewModels {
        val database = getDatabase(applicationContext)
        val scraper = GooglePlayScraper()
        val repository = TelemetryRepository(
            database.activityEventDao(),
            database.androidAppsDao(),
            ApiClient.api,
            scraper
        )
//        lifecycleScope.launch {
//            database.activityEventDao().clearTable()
//            database.androidAppsDao().clearTable()
//        }
        val workerManager = WorkerManager(applicationContext)
        TelemetryViewModelFactory(workerManager, repository)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)


        setContent {
            AppTheme {
                TelemetryApp(viewModel)
            }
        }
    }
}

