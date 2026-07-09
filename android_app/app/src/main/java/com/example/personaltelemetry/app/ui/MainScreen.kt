package com.example.personaltelemetry.app.ui

import android.Manifest
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
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
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
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
import com.example.personaltelemetry.app.backgroundWorker.CustomWorker
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.AppDatabase.Companion.getDatabase
import com.example.personaltelemetry.app.system.ConnectivityService
import com.example.personaltelemetry.app.system.PermissionsService
import com.example.personaltelemetry.app.viewModel.TelemetryViewModel
import kotlinx.coroutines.launch

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
fun TelemetryApp(viewModel: TelemetryViewModel) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val permissionsService = PermissionsService(context);
    val numberOfStoredEvents by viewModel.numberOfStoredEvents.collectAsState(0);
    val numberOfSentEvents by viewModel.numberOfSentEvents.collectAsState(0);

    DisposableEffect(lifecycleOwner) { // Tracks when app becomes active again
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                viewModel.updateUsageStatsPermissions(permissionsService.hasUsageStatsPermissions())
                viewModel.updateLocationPermissions(permissionsService.hasLocationPermissions())
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
        !viewModel.hasUsageStatsPermissions || !viewModel.hasLocationPermissions -> {
            statusText = "Permissions Required"
            statusColor = MaterialTheme.colorScheme.warning
        }

        !viewModel.isTracking -> {
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
                        MaterialTheme.colorScheme.primary,
                        MaterialTheme.colorScheme.secondary
                    )
                )
            )
    ) {
        HeaderSection()
        BodySection(
            viewModel.hasLocationPermissions,
            setLocationPermissions = viewModel::updateLocationPermissions,
            isTracking = viewModel.isTracking,
            onToggleTracking = viewModel::onToggleTracking
        )
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
        hasLocationPermission: Boolean,
        setLocationPermissions: (Boolean) -> Unit,
        isTracking: Boolean,
        onToggleTracking: () -> Unit) {

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
        StartTrackingButton(
            isTracking = isTracking,
            onToggleTracking = onToggleTracking
        )
    }

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
        isTracking: Boolean,
        onToggleTracking: () -> Unit,
    ) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
//    val db = getDatabase(context)
    val cs = ConnectivityService(context)
    Button(
        onClick = {
//            scope.launch {
//                db.activityEventDao().clearTable()
//            }
//                onToggleTracking()
                Log.d("Network",cs.isConnectedToNetwork().toString())
        },
        shape = RectangleShape,
        modifier = Modifier
            .height(100.dp)
            .fillMaxWidth()
    ) {
        Text(
            text = if (!isTracking) "Start Tracking" else "Stop Tracking",
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
            text = "WiFi Access",
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold
        )
    }
}