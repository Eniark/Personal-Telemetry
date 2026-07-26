package com.yhulivatiy.personaltelemetry.app.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(entities = [ActivityEvent::class, AndroidApps::class], version = 11)
abstract class AppDatabase : RoomDatabase() {
    abstract fun activityEventDao(): ActivityEventDao
    abstract fun androidAppsDao(): AndroidAppsDao

    // singleton pattern:
    companion object {
        @Volatile // guarantees that the database is instantly visible to all threads, so no other thread would create a 2nd database
        private var INSTANCE: AppDatabase? = null;

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {  // ?: if (INSTANCE==true) -> return INSTANCE. synchronized = guarantees only 1 thread will execute the method
                INSTANCE ?:
                    Room.databaseBuilder(
                        context.applicationContext,
                        AppDatabase::class.java,
                        "telemetry.db"
                    )
                    .fallbackToDestructiveMigration(true)
                    .build().also {
                    INSTANCE = it // sets the database into the INSTANCE attribute
                }
            }
        }
    }
}