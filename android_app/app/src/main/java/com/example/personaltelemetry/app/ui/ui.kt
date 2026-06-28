package com.example.personaltelemetry.app.ui

import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.provider.Settings
import android.util.Log
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.example.personaltelemetry.app.api.ActivityEvent
import com.example.personaltelemetry.app.api.CustomWorker
import com.example.personaltelemetry.app.api.TelemetryRepository
import com.example.personaltelemetry.app.api.checkAccessPermission
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit

@Composable
fun AppTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = AppTypography,
        content = content
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TelemetryApp() {
    var running by remember { mutableStateOf(false) } // "by remember" - allows the UI to automatically react to the state of a variable
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    var hasAccessPermission by remember { // Allows the UI to track this variable and adjust itself
        mutableStateOf(checkAccessPermission(context))
    }

    DisposableEffect(lifecycleOwner) { // Tracks when app becomes active again
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                hasAccessPermission = checkAccessPermission(context)
            }
        }

        lifecycleOwner.lifecycle.addObserver(observer)

        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    val statusText: String
    val statusColor: Color

    when {
        !hasAccessPermission -> {
            statusText = "Permissions Required"
            statusColor = MaterialTheme.colorScheme.warning
        }
        !running -> {
            statusText = "Inactive"
            statusColor = MaterialTheme.colorScheme.onError
        }
        else -> {
            statusText = "Active"
            statusColor = MaterialTheme.colorScheme.success
        }
    }
    Column( // Vertical layout of child elements
        modifier = Modifier
            .fillMaxSize()
            .background(
                brush = Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF8E94F2),
                        Color(0xFFFA824C)
                    )
                )
            )
    ) {
        HeaderSection()
        BodySection(running, hasAccessPermission) {
            if (hasAccessPermission) {
                running = it
            }
        }
        StatusSection(statusText, statusColor)

    }
}


@Composable
fun HeaderSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            modifier = Modifier.padding(
                top = 70.dp
            ),
            text = "Personal Telemetry",
            style = MaterialTheme.typography.headlineLarge,
            letterSpacing = 1.8.sp,
        )
    }
}

@Composable
fun BodySection(running: Boolean, hasAccessPermission: Boolean, onRunningChange: (Boolean) -> Unit) {

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
            .padding(50.dp, 50.dp, 50.dp, 0.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally

    ) {
        PermissionAccessButton()
        StartTrackingButton(running, hasAccessPermission) {
            onRunningChange(it)
        }


    }

}

fun startTracking(context: Context) {
    val request = PeriodicWorkRequestBuilder<CustomWorker>(
        CustomWorker.TRACKING_WINDOW_MINUTES, TimeUnit.MINUTES
    ).build()

    WorkManager.getInstance(context).enqueue(request)

}

@Composable
fun StatusSection(
    statusText: String,
    statusColor: Color
) {
    var numberOfSentEvents = 0
    var numberOfStoredEvents = 0

    Column(
        modifier = Modifier
            .padding(horizontal = 50.dp)
            .fillMaxWidth()
    ) {

        TableRow("Status:", statusText, statusColor)
        Spacer(modifier = Modifier.height(16.dp))

        TableRow("Stored events:", numberOfStoredEvents.toString())
        Spacer(modifier = Modifier.height(16.dp))

        TableRow("Sent events:", numberOfSentEvents.toString())
    }
}

@Composable
fun TableRow(
    label: String,
    value: String,
    valueColor: Color = Color.Unspecified
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {

        Text(
            text = label,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall
        )

        Text(
            text = value,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall,
            color = valueColor
        )
    }
}
@Composable
fun StartTrackingButton(running: Boolean, hasAccessPermission: Boolean, onToggle: (Boolean) -> Unit) {
    val context = LocalContext.current

    Button(

        onClick = {
            val newValue = !running;
            onToggle(newValue);

            if (newValue && hasAccessPermission) {
                startTracking(context)
            }


        },
        shape = RectangleShape,
        modifier = Modifier
            .height(100.dp)
            .width(300.dp)
    ) {
        Text(
            text = if (!running) "Start Tracking" else "Stop Tracking",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
    }
}


@Composable
fun PermissionAccessButton() {
    val context = LocalContext.current


    Button(
        onClick = {
            val intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
            context.startActivity(intent)
        },
        shape = RectangleShape,
        modifier = Modifier
            .height(50.dp)
            .width(300.dp)
    ) {
        Text(
            text = "Grant Permission Access",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
    }
}