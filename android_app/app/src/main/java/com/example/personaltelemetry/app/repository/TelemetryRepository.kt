package com.example.personaltelemetry.app.repository

import android.util.Log
import com.example.personaltelemetry.BuildConfig
import com.example.personaltelemetry.app.database.ActivityEvent
import com.example.personaltelemetry.app.database.ActivityEventDao
import com.example.personaltelemetry.app.database.SystemAppCollectionDao
import kotlinx.coroutines.flow.Flow
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

class TelemetryRepository(
    private val activityEventDao: ActivityEventDao,
    private val systemAppCollectionDao: SystemAppCollectionDao,
    private val api: TelemetryApi,
    private val scraper: GooglePlayScraper
) {

    val eventsStoredCount: Flow<Int> = activityEventDao.getStoredEventsCount();
    val eventsSentCount: Flow<Int> = activityEventDao.getSentEventsCount();
    suspend fun saveEventsToLocalDb(events: List<ActivityEvent>): Unit {
        activityEventDao.insert(events)
    }

    suspend fun saveSystemEvents(systemEvents: List<ActivityEvent>): Unit {
        systemAppCollectionDao.insertSystemApps(systemEvents)
    }

    suspend fun getSystemApps(packageNames: List<String>): Set<String> {
        return systemAppCollectionDao.getSystemApps(packageNames).toSet()
    }

    suspend fun sendEventsToAPI(events: List<ActivityEvent>): Unit {
        var pendingEvents = activityEventDao.getPending()
        pendingEvents = events + pendingEvents
        Log.d("APP-LOGS:pendingEvents", pendingEvents.toString())

        if (pendingEvents.size > 5) {
            api.sendEvents(pendingEvents)
            activityEventDao.markAsSent(pendingEvents.map { it.id })
        }
    }

    suspend fun getAppInformation(packageName: String): Triple<String, String, Boolean> {
        return scraper.getAppInformation(packageName)
    }

    suspend fun getAPIHealth(): Boolean {
        return try {
                    val response = api.isAvailable()
                    response.isSuccessful
                }
                catch (e: Exception) {
                    false
                }

    }

}

interface TelemetryApi {

    @POST("phone_event")
    suspend fun sendEvents( // suspend = async
        @Body events: List<ActivityEvent>
    ): Response<Unit>

    @GET("health")
    suspend fun isAvailable(): Response<Unit>
}



object ApiClient {
    val URL: String = BuildConfig.API_BASE_URL;
    private val retrofit = Retrofit.Builder() // Retrofit is used to make HTTP calls
        .baseUrl(URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val api: TelemetryApi = retrofit.create(TelemetryApi::class.java) // class attribute
}