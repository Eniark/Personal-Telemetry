package com.example.personaltelemetry.app.repository

import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.jsoup.HttpStatusException
import org.jsoup.Jsoup
import kotlin.random.Random
import kotlin.time.Duration.Companion.milliseconds

class GooglePlayScraper {
    suspend fun getAppInformation(packageName: String): Triple<String, String, Boolean> {
        var appName = packageName
        var description = "No description found"
        var isSystem: Boolean = false;
        try {
            delay(Random.nextLong(1_000, 3_000).milliseconds)  // Add a random delay between requests
            val body = withContext(Dispatchers.IO) { // withContext switches the thread from main thread to a different one and returns result to the main thread.
                Jsoup.connect(
                    "https://play.google.com/store/apps/details?id=${packageName}"
                )
                    .userAgent("Mozilla/5.0")
                    .get()
            }

            appName = body.title()
            description = body.selectFirst("div[data-g-id=description]")?.text() ?: description
            isSystem = false
        } catch (e: HttpStatusException)
        {
            if (e.statusCode == 404) {
                appName = packageName
                isSystem = true
            }
            Log.e("SCRAPER", "Failed", e)
        }
        return Triple(appName, description, isSystem)
    }

}