package com.example.personaltelemetry.app.database

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface ActivityEventDao {

    @Upsert
    suspend fun upsert(events: List<ActivityEvent>)

    @Query("SELECT * FROM ActivityEvent WHERE isVerified=0")
    suspend fun getUnverifiedEvents(): List<ActivityEvent>

    @Query("SELECT * FROM ActivityEvent WHERE sentToApi=0")
    suspend fun getUnsentEvents(): List<ActivityEvent>


    @Query("UPDATE ActivityEvent SET sentToApi = 1 WHERE id in (:ids)")
    suspend fun markAsSent(ids: List<Long>)

    @Query("DELETE FROM ActivityEvent")
    suspend fun clearTable();

    @Query("DELETE FROM ActivityEvent WHERE isSystemEvent=1")
    suspend fun removeSystemEvents();

    @Query("SELECT COUNT(*) FROM ActivityEvent WHERE isSystemEvent=0")
    fun getStoredEventsCount(): Flow<Int>

    @Query("SELECT COUNT(*) FROM ActivityEvent where sentToApi = 1")
    fun getSentEventsCount(): Flow<Int>

}