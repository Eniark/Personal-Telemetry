package com.example.personaltelemetry.app.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Dao
interface ActivityEventDao {

    @Insert
    suspend fun insert(event: ActivityEvent)

    @Query("SELECT * FROM ActivityEvent WHERE sent = 0")
    suspend fun getPending(): List<ActivityEvent>

    @Query("UPDATE ActivityEvent SET sent = 1 WHERE id in (:sentIds)")
    suspend fun markAsSent(sentIds: List<Long>)
}