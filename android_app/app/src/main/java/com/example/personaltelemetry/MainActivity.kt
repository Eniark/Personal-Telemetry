package com.example.personaltelemetry

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
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
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import android.provider.Settings
import androidx.compose.ui.platform.LocalContext

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            TelemetryApp()
        }
    }
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
            fontSize = 35.sp,
            fontWeight = FontWeight.Bold,
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
            .background(Color.Green),

        verticalArrangement = Arrangement.spacedBy(20.dp),
        horizontalAlignment = Alignment.CenterHorizontally

    ) {
        PermissionAccessButton()
        StartTrackingButton(running) {
            running = it
        }

        Text(
            text = "Sent events: <Amount>",
            fontSize = 32.sp
        )

    }

}
@Composable
fun StartTrackingButton(running: Boolean, onToggle: (Boolean) -> Unit) {
    Button(
        onClick = {
            onToggle(!running);
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