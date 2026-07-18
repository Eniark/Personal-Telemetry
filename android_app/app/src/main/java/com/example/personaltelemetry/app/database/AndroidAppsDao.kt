package com.example.personaltelemetry.app.database

import android.text.BoringLayout
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Dao
interface AndroidAppsDao {

    @Query("SELECT * FROM AndroidApps WHERE packageName IN (:packageNames) AND isSystem=:isSystem")
    suspend fun getAndroidApps(packageNames: List<String>, isSystem: Boolean): List<AndroidApps>

    @Insert
    suspend fun insertAndroidApps(systemEvents: List<ActivityEvent>)
}