package com.example.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String?,
    val usedAtTimestamp: Long,
    val sentToApi: Boolean
)

