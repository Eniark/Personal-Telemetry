package com.example.personaltelemetry.app.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface ActivityEventDao {

    @Insert
    suspend fun insert(events: List<ActivityEvent>)

    @Query("SELECT * FROM ActivityEvent WHERE sentToApi = 0")
    suspend fun getPending(): List<ActivityEvent>

    @Query("UPDATE ActivityEvent SET sentToApi = 1 WHERE id in (:ids)")
    suspend fun markAsSent(ids: List<Long>)

    @Query("DELETE FROM ActivityEvent")
    suspend fun clearTable();

    @Query("SELECT COUNT(*) FROM ActivityEvent")
    fun getStoredEventsCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM ActivityEvent where sentToApi = 1")
    fun getSentEventsCount(): Flow<Int>

}