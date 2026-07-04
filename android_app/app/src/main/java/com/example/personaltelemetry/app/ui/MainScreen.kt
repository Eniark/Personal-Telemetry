package com.example.personaltelemetry.app.ui

import android.Manifest
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.provider.Settings
import android.util.Log
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.runtime.mutableIntStateOf
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
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.backgroundWorker.CustomWorker
import com.example.personaltelemetry.app.database.ActivityEventDao
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.repository.ApiClient
import com.example.personaltelemetry.app.repository.TelemetryApi
import com.example.personaltelemetry.app.repository.TelemetryRepository
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit
import com.example.personaltelemetry.app.system.PermissionsService
import com.example.personaltelemetry.app.system.WifiService
import kotlin.collections.plusAssign
import java.time.Instant

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
    val permissionsService = PermissionsService(context);
    var hasUsageStatsPermission by remember { // Allows the UI to track this variable and adjust itself
        mutableStateOf(permissionsService.hasUsageStatsPermissions())
    }
    var hasLocationPermissions by remember {
        mutableStateOf(permissionsService.hasLocationPermissions())
    }

    var numberOfSentEvents by remember {
        mutableIntStateOf(0)
    }
    var numberOfStoredEvents by remember {
        mutableIntStateOf(0)
    }

    DisposableEffect(lifecycleOwner) { // Tracks when app becomes active again
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                hasUsageStatsPermission = permissionsService.hasUsageStatsPermissions()
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
        !hasUsageStatsPermission || !hasLocationPermissions -> {
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
        BodySection(
            running,
            hasUsageStatsPermission,
            hasLocationPermissions,
            setLocationPermissions = {
                hasLocationPermissions = it
            },
            onRunningChange = {
                if (hasUsageStatsPermission && hasLocationPermissions) {
                    running = it
                }
            },
            onNewEventsStored = {
                numberOfStoredEvents += it
            },
            onNewEventsSent = {
                numberOfSentEvents += it
            })
        StatusSection(statusText, statusColor, numberOfSentEvents, numberOfStoredEvents)
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
fun BodySection(
        running: Boolean,
        hasUsageStatsPermission: Boolean,
        hasLocationPermission: Boolean,
        setLocationPermissions: (Boolean) -> Unit,
        onRunningChange: (Boolean) -> Unit,
        onNewEventsStored: (Int) -> Unit,
        onNewEventsSent: (Int) -> Unit,) {

    val context = LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp)
            .padding(50.dp, 50.dp, 50.dp, 0.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally

    ) {
        Row (
            modifier = Modifier
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            PermissionUsageStatsButton(context, Modifier.weight(0.8f))
            PermissionWifiAccessButton(hasLocationPermission,setLocationPermissions,Modifier.weight(0.8f))
        }
        StartTrackingButton(running,
            hasUsageStatsPermission,
            onToggle = {
                onRunningChange(it)
            },
            onNewEventsStored,
            onNewEventsSent)


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
    statusColor: Color,
    numberOfSentEvents: Int,
    numberOfStoredEvents: Int,
) {
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
fun StartTrackingButton(
        running: Boolean,
        hasUsageStatsPermission: Boolean,
        onToggle: (Boolean) -> Unit,
        onNewEventsStored: (Int) -> Unit,
        onNewEventsSent: (Int) -> Unit,
        ) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val db = getDatabase(context)
    Button(

        onClick = {
            val newValue = !running;
            onToggle(newValue);
            scope.launch {
                db.activityEventDao().clearTable()
            }

//            if (newValue && hasUsageStatsPermission) {
////                startTracking(context)
//                val usageStatsManager =
//                    context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
//
//                val endTime = System.currentTimeMillis()
//                val startTime = endTime - 1000 * 60 * CustomWorker.TRACKING_WINDOW_MINUTES // last 10 minutes
//
//                var stats = usageStatsManager.queryUsageStats(
//                    UsageStatsManager.INTERVAL_DAILY,
//                    startTime,
//                    endTime
//                )
//
//                var events: List<ActivityEvent> = stats.filter {
//                    it.lastTimeUsed > 0 // get apps with > 0 time usage
//                }.map {
//                    val pm = context.packageManager
//                    val appName = try {
//                        val appInfo = pm.getApplicationInfo(it.packageName, 0)
//                        pm.getApplicationLabel(appInfo).toString()
//                    }
//                    catch (e: Exception) {
//                        it.packageName
//                    }
//
//                    ActivityEvent(
//                        packageName = appName,
//                        timestamp = it.lastTimeUsed,
//                        sent = false
//                    )
//                }
//                val db = getDatabase(context)
//
//                scope.launch {
//                    TelemetryRepository(
//                        db.activityEventDao(),
//                        ApiClient.api
//                    ).saveEventsToLocalDb(events)
//                }
//                Log.d("Events:", events.size.toString())
//                onNewEventsStored(events.size)
//                scope.launch {
//                    var eventsStored: List<ActivityEvent> = db.activityEventDao().getPending()
//                    eventsStored.forEach {
//                        Log.d("Database", it.toString())
//                    }
//                }

//            }


        },
        shape = RectangleShape,
        modifier = Modifier
            .height(100.dp)
            .fillMaxWidth()
    ) {
        Text(
            text = if (!running) "Start Tracking" else "Stop Tracking",
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
    }
}


@Composable
fun PermissionUsageStatsButton(context: Context, modifier: Modifier) {
    Button(
        onClick = {
            val intent = Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS)
            context.startActivity(intent)
        },
        shape = RectangleShape,
        modifier = modifier
            .height(50.dp)
    ) {
        Text(
            text = "Usage Access",
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun PermissionWifiAccessButton(hasLocationPermission: Boolean, setLocationPermissions: (Boolean) -> Unit, modifier: Modifier) {
    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) {
        setLocationPermissions(hasLocationPermission)
    }
    Button(
        onClick = {
            launcher.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        },
        shape = RectangleShape,
        modifier = modifier
            .height(50.dp)
    ) {
        Text(
            text = "Wifi Access",
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold
        )
    }
}