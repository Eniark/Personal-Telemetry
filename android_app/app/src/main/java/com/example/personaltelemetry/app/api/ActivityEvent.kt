package com.example.personaltelemetry.app.api
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

data class ActivityEvent(
    val packageName: String?,
    val timestamp: Long
)

interface TelemetryApi {

    @POST("os_event")
    suspend fun sendEvent( // suspend = async
        @Body event: ActivityEvent
    ): Response<Unit>
}


object ApiClient {
    private val retrofit = Retrofit.Builder()
        .baseUrl("http://192.168.0.102:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: TelemetryApi = retrofit.create(TelemetryApi::class.java) // class attribute
}