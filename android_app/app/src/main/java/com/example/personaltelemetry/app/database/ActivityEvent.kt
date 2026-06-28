package com.example.personaltelemetry.app.processingLayer
import androidx.room.vo.Entity
import com.example.personaltelemetry.BuildConfig
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    val timestamp: Long
)

interface TelemetryApi {

    @POST("os_event")
    suspend fun sendEvent( // suspend = async
        @Body event: ActivityEvent
    ): Response<Unit>
}



object ApiClient {
   val URL: String = BuildConfig.API_BASE_URL;
    private val retrofit = Retrofit.Builder()
        .baseUrl(URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: TelemetryApi = retrofit.create(TelemetryApi::class.java) // class attribute
}