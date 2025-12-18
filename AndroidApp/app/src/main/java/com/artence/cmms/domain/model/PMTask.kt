package com.artence.cmms.domain.model

import java.text.SimpleDateFormat
import java.util.*

data class PMTask(
    val id: Int,
    val machineId: Int,
    val machineName: String?,
    val taskName: String,
    val description: String?,
    val frequency: String, // Daily, Weekly, Monthly, Quarterly, Annually
    val lastExecuted: Long?,
    val nextScheduled: Long,
    val status: String, // Scheduled, Overdue, In Progress, Completed
    val assignedToUserId: Int?,
    val assignedToUsername: String?,
    val priority: String?, // Low, Medium, High, Critical
    val estimatedDuration: Int?, // in minutes
    val createdAt: Long,
    val updatedAt: Long?
) {
    val nextScheduledFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(nextScheduled))

    val lastExecutedFormatted: String?
        get() = lastExecuted?.let { SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date(it)) }

    val isOverdue: Boolean
        get() = status == "Overdue"

    val isCompleted: Boolean
        get() = status == "Completed"

    val daysUntilDue: Int
        get() {
            val now = System.currentTimeMillis()
            val daysMs = (nextScheduled - now) / (1000 * 60 * 60 * 24)
            return daysMs.toInt().coerceAtLeast(-999)
        }
}

