package com.example.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey
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
    val packageName: String?,
    val timestamp: Long,
    val sent: Boolean
)

