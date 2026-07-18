package com.yhulivatiy.personaltelemetry.app.database

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    indices = [
        Index(value = ["packageName"], unique = true)
    ]
)
data class AndroidApps(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val packageName: String,
    val appName: String?,
    val description: String?,
    val isSystem: Boolean,
    val isVerified: Boolean

) {
    override fun toString(): String {
        return "AndroidApp(id=$id, packageName=$packageName, isSystem=$isSystem)"
    }
}
