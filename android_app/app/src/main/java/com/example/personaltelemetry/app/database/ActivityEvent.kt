package com.example.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String?,
    val usedAtTimestamp: Long,
    val sentToApi: Boolean
)

@Entity
data class SystemAppCollection(
    @PrimaryKey(autoGenerate = true)
    val packageName: String
)

