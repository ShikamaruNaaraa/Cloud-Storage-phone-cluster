package com.phonecluster.app.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.phonecluster.app.storage.PreferencesManager
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.DisposableEffect
import com.phonecluster.app.utils.heartbeat.HeartbeatManager
import com.phonecluster.app.utils.websocket.WebSocketManager

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StorageModeScreen(onBackClick: () -> Unit = {}) {
    val context = LocalContext.current
    val deviceId = PreferencesManager.getDeviceId(context) ?: -1

    LaunchedEffect(Unit) {
        if (deviceId != -1) {
            HeartbeatManager.start(
                serverBaseUrl = "http://10.0.2.2:8000",
                deviceId = deviceId
            )
            WebSocketManager.connect(
                context = context,
                serverIp = "10.124.156.168"
            )
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            HeartbeatManager.stop()
            WebSocketManager.disconnect()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Storage Mode") }
            )
        }
    ) { padding ->
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                // Device ID Badge
                Surface(
                    shape = MaterialTheme.shapes.small,
                    color = MaterialTheme.colorScheme.primaryContainer,
                    modifier = Modifier.padding(bottom = 16.dp)
                ) {
                    Text(
                        text = "Device ID: $deviceId",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                    )
                }

                Text(
                    text = "Storage Mode Active",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.primary
                )

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "This device is now acting as a storage node",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(modifier = Modifier.height(32.dp))

                // Placeholder for future functionality
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.secondaryContainer
                    )
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Status",
                            style = MaterialTheme.typography.titleMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Waiting for chunks...",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer
                        )
                    }
                }
            }
        }
    }
}