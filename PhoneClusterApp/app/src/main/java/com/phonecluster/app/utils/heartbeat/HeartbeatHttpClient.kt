package com.phonecluster.app.utils.heartbeat

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

object HeartbeatHttpClient {

    private const val JSON = "application/json"

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(5, TimeUnit.SECONDS)
        .build()

    fun sendHeartbeat(
        serverBaseUrl: String,
        deviceId: Int,
        availableStorage: Long?
    ) {
        val payload = JSONObject().apply {
            put("device_id", deviceId)
            availableStorage?.let {
                put("available_storage", it)
            }
        }

        val body = payload.toString()
            .toRequestBody(JSON.toMediaType())

        val request = Request.Builder()
            .url("$serverBaseUrl/devices/heartbeat")
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                // intentionally ignored
            }

            override fun onResponse(call: Call, response: Response) {
                response.close()
            }
        })
    }
}
