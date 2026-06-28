package com.example.personaltelemetry.app.database

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(entities = [ActivityEvent::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun activityEventDao(): ActivityEventDao
}