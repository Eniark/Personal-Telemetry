package com.example.personaltelemetry.app.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Dao
interface SystemAppCollectionDao {

    @Query("SELECT packageName FROM SystemAppCollection WHERE packageName IN (:packageNames)")
    suspend fun getSystemApps(packageNames: List<String>): List<String>

    @Insert
    suspend fun insertSystemApps(systemEvents: List<ActivityEvent>)
}