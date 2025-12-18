package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "pm_tasks",
    indices = [
        Index("status"),
        Index("machineId"),
        Index("nextScheduled")
    ]
)
data class PMTaskEntity(
    @PrimaryKey val id: Int,
    val machineId: Int,
    val machineName: String?,
    val taskName: String,
    val description: String?,
    val frequency: String,
    val lastExecuted: Long?,
    val nextScheduled: Long,
    val status: String,
    val assignedToUserId: Int?,
    val assignedToUsername: String?,
    val priority: String?,
    val estimatedDuration: Int?,
    val createdAt: Long,
    val updatedAt: Long?
)
