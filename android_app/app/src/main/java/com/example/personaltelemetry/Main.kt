package com.example.personaltelemetry

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.personaltelemetry.app.ui.TelemetryApp

class Main: ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            TelemetryApp()
        }
    }
}

