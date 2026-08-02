package com.yhulivatiy.personaltelemetry.app.repository

import android.util.Log
import com.yhulivatiy.personaltelemetry.BuildConfig
import com.yhulivatiy.personaltelemetry.app.database.ActivityEvent
import com.yhulivatiy.personaltelemetry.app.database.ActivityEventDao
import com.yhulivatiy.personaltelemetry.app.database.AndroidApps
import com.yhulivatiy.personaltelemetry.app.database.AndroidAppsDao
import kotlinx.coroutines.flow.Flow
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

class TelemetryRepository(
    private val activityEventDao: ActivityEventDao,
    private val AndroidAppsDao: AndroidAppsDao,
    private val api: TelemetryApi,
    private val scraper: GooglePlayScraper
) {

    val eventsStoredCount: Flow<Int> = activityEventDao.getStoredEventsCount();
    val eventsSentCount: Flow<Int> = activityEventDao.getSentEventsCount();
    suspend fun saveEventsToLocalDb(events: List<ActivityEvent>): Unit {
        activityEventDao.upsert(events)
    }

    suspend fun getUnverifiedEvents(): List<ActivityEvent> {
        return activityEventDao.getUnverifiedEvents()
    }

    suspend fun getUnsentEvents(): List<ActivityEvent> {
        return activityEventDao.getUnsentEvents()
    }

    suspend fun saveAndroidAppsToLocalDb(apps: List<AndroidApps>): Unit {
        AndroidAppsDao.upsertApps(apps)
    }

    suspend fun getAndroidApps(): List<AndroidApps> {
        return AndroidAppsDao.getApps()
    }


    suspend fun sendEventsToAPI(events: List<ActivityEvent>): Unit {
        api.sendEvents(events)
        activityEventDao.markAsSent(events.map { it.id })
    }

    suspend fun getAppInformation(packageName: String): Triple<String, String, Boolean> {
        return scraper.getAppInformation(packageName)
    }
    suspend fun removeSystemEvents(): Unit {
        activityEventDao.removeSystemEvents()
    }


    suspend fun getAPIHealth(): Boolean {
        return try {
                    val response = api.isAvailable()
                    Log.d("APP-LOGS:API-Health", response.toString())
                    response.isSuccessful
                }
                catch (e: Exception) {
                    Log.e("APP-LOGS:API-Health", e.toString())
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