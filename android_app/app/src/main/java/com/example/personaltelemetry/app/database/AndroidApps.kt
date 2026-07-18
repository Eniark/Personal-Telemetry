package com.example.personaltelemetry.app.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity
data class AndroidApps(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    val appName: String,
    val description: String,
    val isSystem: Boolean
)
