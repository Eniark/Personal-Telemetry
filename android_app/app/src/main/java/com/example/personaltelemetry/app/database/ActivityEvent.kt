package com.example.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey
import kotlinx.serialization.descriptors.SerialDescriptor

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    val appName: String?,
    val description: String? = null,
    val usedAtTimestamp: Long,
    val sentToApi: Boolean = false,
    val isVerified: Boolean = false,
    val isSystemEvent: Boolean = false


) {
    override fun toString(): String {
        return "ActivityEvent(id=$id, packageName=$packageName"
    }

}


