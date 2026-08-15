package com.yhulivatiy.personaltelemetry.app.database
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity
data class ActivityEvent(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    var appName: String? = null,
    val description: String? = null,
    val developer: String? = null,
    var eventStartTime: Long? = null,
    var eventEndTime: Long? = null,
    val sentToApi: Boolean = false,
    val isVerified: Boolean = false,
    val isSystemEvent: Boolean = false


) {
    override fun toString(): String {
        return "ActivityEvent(id=$id, packageName=$packageName, eventStartTime=$eventStartTime, eventEndTime=$eventEndTime"
    }

}


