package com.example.personaltelemetry.app.ui

import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.provider.Settings
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.personaltelemetry.app.api.ActivityEvent
import com.example.personaltelemetry.app.api.MyWorker
import com.example.personaltelemetry.app.api.TelemetryRepository
import com.example.personaltelemetry.app.api.hasUsageAccessPermission
import kotlinx.coroutines.launch
import java.security.Permission
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

    Column( // Vertical layout of child elements
        modifier = Modifier
            .fillMaxSize()
            .height(300.dp)
    ) {
        HeaderSection()
        BodySection()
    }
}


@Composable
fun HeaderSection() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .height(200.dp)
            .background(Color.Yellow),
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
fun BodySection() {
    var running by remember { mutableStateOf(false) } // "by remember" - allows the UI to react to the state of a variable
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),

        verticalArrangement = Arrangement.spacedBy(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally

    ) {
        PermissionAccessButton()
        StartTrackingButton(running) {
            running = it
        }
        statusRow()
        Text(
            text = "Sent events: <Amount>",
            style = MaterialTheme.typography.bodyLarge,
        )

    }

}

fun startTracking(context: Context) {
    val request = PeriodicWorkRequestBuilder<MyWorker>(
        15, TimeUnit.MINUTES
    ).build()

    WorkManager.getInstance(context).enqueue(request)

}

@Composable
fun statusRow() {
    val context = LocalContext.current

    Row (
        modifier = Modifier
            .fillMaxWidth()
    ) {
        Text(
            text = "Status",
            style = MaterialTheme.typography.bodyLarge,
        )
        Text(
            text = if (hasUsageAccessPermission(context)) "Status" else "test",
            style = MaterialTheme.typography.bodyLarge,
        )
    }
}
@Composable
fun StartTrackingButton(running: Boolean, onToggle: (Boolean) -> Unit) {
    val context = LocalContext.current

    val usageStatsManager =
        context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager

    val endTime = System.currentTimeMillis()
    val startTime = endTime - 1000 * 60 * 10 // last 10 minutes

    val stats = usageStatsManager.queryUsageStats(
        UsageStatsManager.INTERVAL_DAILY,
        startTime,
        endTime
    )

    val scope = rememberCoroutineScope()


    Button(
        onClick = {
            onToggle(!running);
            val recentApp = stats
                .maxByOrNull { it.lastTimeUsed }

            val packageName = recentApp?.packageName
            val event = ActivityEvent(
                packageName = packageName,
                timestamp = System.currentTimeMillis()
            )
            scope.launch {
                TelemetryRepository().sendEvent(event)
            }
//            startTracking(context)



        },
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
            .padding(
                top = 50.dp
            )
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