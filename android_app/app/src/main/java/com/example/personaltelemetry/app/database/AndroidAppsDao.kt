package com.example.personaltelemetry.app.database

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert

@Dao
interface AndroidAppsDao {

    @Query("SELECT * FROM AndroidApps") // I do not expect there to be many apps, hence doing a full scan
    suspend fun getApps(): List<AndroidApps>

    @Upsert
    suspend fun upsertApps(systemEvents: List<AndroidApps>)

    @Query("DELETE FROM AndroidApps")
    suspend fun clearTable();
}