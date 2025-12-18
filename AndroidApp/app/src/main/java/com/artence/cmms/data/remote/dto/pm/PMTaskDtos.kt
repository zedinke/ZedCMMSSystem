package com.artence.cmms.data.remote.dto.pm

import com.google.gson.annotations.SerializedName
import java.util.Date

data class PMTaskDto(
    val id: Int,
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

data class CreatePMTaskDto(
    val machineId: Int,
    val taskName: String,
    val description: String?,
    val frequency: String,
    val nextScheduled: Long,
    val assignedToUserId: Int?,
    val priority: String?,
    val estimatedDuration: Int?
)

data class UpdatePMTaskDto(
    val taskName: String?,
    val description: String?,
    val frequency: String?,
    val nextScheduled: Long?,
    val status: String?,
    val assignedToUserId: Int?,
    val priority: String?,
    val estimatedDuration: Int?
)

data class ExecutePMTaskDto(
    val status: String = "Completed",
    val lastExecuted: Long = System.currentTimeMillis(),
    val notes: String?
)

