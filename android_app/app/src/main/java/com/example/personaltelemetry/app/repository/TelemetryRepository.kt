package com.example.personaltelemetry.app.repository

import android.R
import android.util.Log
import com.example.personaltelemetry.BuildConfig
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.ActivityEventDao
import kotlinx.coroutines.flow.Flow
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

class TelemetryRepository(
    private val dao: ActivityEventDao,
    private val api: TelemetryApi,
    private val scraper: GooglePlayScraper
) {

    val eventsStoredCount: Flow<Int> = dao.getStoredEventsCount();
    val eventsSentCount: Flow<Int> = dao.getSentEventsCount();
    suspend fun saveEventsToLocalDb(events: List<ActivityEvent>): Unit {
        dao.insert(events)
    }

    suspend fun sendEventsToAPI(events: List<ActivityEvent>): Unit {
        var pendingEvents = dao.getPending()
        pendingEvents = events + pendingEvents
        Log.d("pendingEvents", pendingEvents.toString())

        if (pendingEvents.size > 5) {
            api.sendEvents(pendingEvents)
            dao.markAsSent(pendingEvents.map { it.id })
        }
    }

    suspend fun getAppInformation(packageName: String): Triple<String, String, Boolean> {
        return scraper.getAppInformation(packageName)
    }
}

interface TelemetryApi {

    @POST("phone_event")
    suspend fun sendEvents( // suspend = async
        @Body events: List<ActivityEvent>
    ): Response<Unit>
}



object ApiClient {
    val URL: String = BuildConfig.API_BASE_URL;
    private val retrofit = Retrofit.Builder() // Retrofit is used to make HTTP calls
        .baseUrl(URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: TelemetryApi = retrofit.create(TelemetryApi::class.java) // class attribute
}