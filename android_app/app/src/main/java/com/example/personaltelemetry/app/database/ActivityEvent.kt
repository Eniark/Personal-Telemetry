package com.example.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String?,
    val timestamp: Long,
    val sent: Boolean
)

