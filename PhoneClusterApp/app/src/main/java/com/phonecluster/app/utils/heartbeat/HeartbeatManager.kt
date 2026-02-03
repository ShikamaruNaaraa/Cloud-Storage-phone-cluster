package com.phonecluster.app.utils.heartbeat

import com.phonecluster.app.utils.DeviceInfoProvider
import kotlinx.coroutines.*

object HeartbeatManager {

    private const val HEARTBEAT_INTERVAL_MS = 10_000L

    private var job: Job? = null

    fun start(serverBaseUrl: String, deviceId: Int) {
        if (job != null) return // already running

        job = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                val availableStorage = DeviceInfoProvider.getAvailableStorageBytes()

                HeartbeatHttpClient.sendHeartbeat(
                    serverBaseUrl = serverBaseUrl,
                    deviceId = deviceId,
                    availableStorage = availableStorage
                )

                delay(HEARTBEAT_INTERVAL_MS)
            }
        }
    }

    fun stop() {
        job?.cancel()
        job = null
    }
}
