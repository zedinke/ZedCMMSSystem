package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "worksheets",
    indices = [
        Index("status"),
        Index("priority"),
        Index("machineId")
    ]
)
data class WorksheetEntity(
    @PrimaryKey val id: Int,
    val machineId: Int?,
    val assignedToUserId: Int?,
    val title: String,
    val description: String?,
    val status: String,
    val priority: String?,
    val createdAt: Long,
    val updatedAt: Long?
)
