package com.artence.cmms.domain.model

import java.text.SimpleDateFormat
import java.util.*

data class Worksheet(
    val id: Int,
    val machineId: Int?,
    val machineName: String?,
    val assignedToUserId: Int?,
    val assignedToUsername: String?,
    val title: String,
    val description: String?,
    val status: String,
    val priority: String?,
    val workType: String?,
    val estimatedTime: Int?,
    val actualTime: Int?,
    val notes: String?,
    val createdAt: Long,
    val updatedAt: Long?,
    val completedAt: Long?
) {
    val createdAtFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(createdAt))

    val updatedAtFormatted: String?
        get() = updatedAt?.let { SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(it)) }
}

