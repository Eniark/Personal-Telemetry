package com.example.personaltelemetry

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.TelemetryRepository
import com.example.personaltelemetry.app.ui.AppTheme
import com.example.personaltelemetry.app.ui.TelemetryApp
import com.example.personaltelemetry.app.viewModel.TelemetryViewModel
import com.example.personaltelemetry.app.viewModel.TelemetryViewModelFactory

class Main : ComponentActivity() {

    private val viewModel: TelemetryViewModel by viewModels {
        val database = getDatabase(applicationContext)
        val repository = TelemetryRepository(
            database.activityEventDao(),
            ApiClient.api
        )
        TelemetryViewModelFactory(repository)
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

