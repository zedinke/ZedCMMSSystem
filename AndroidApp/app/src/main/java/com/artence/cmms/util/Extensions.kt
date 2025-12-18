package com.artence.cmms.util

import java.text.SimpleDateFormat
import java.util.*

// Date Extensions
fun Long.toDateString(format: String = "yyyy-MM-dd HH:mm"): String {
    val sdf = SimpleDateFormat(format, Locale.getDefault())
    return sdf.format(Date(this))
}

fun String.toTimestamp(format: String = "yyyy-MM-dd HH:mm"): Long {
    val sdf = SimpleDateFormat(format, Locale.getDefault())
    return sdf.parse(this)?.time ?: 0L
}

// String Extensions
fun String?.orEmpty(): String = this ?: ""

fun String?.isNotNullOrEmpty(): Boolean = !this.isNullOrEmpty()

// Status Color Helper
fun String.getStatusColor(): androidx.compose.ui.graphics.Color {
    return when (this.lowercase()) {
        Constants.MACHINE_STATUS_OPERATIONAL -> androidx.compose.ui.graphics.Color.Green
        Constants.MACHINE_STATUS_MAINTENANCE -> androidx.compose.ui.graphics.Color.Yellow
        Constants.MACHINE_STATUS_BREAKDOWN -> androidx.compose.ui.graphics.Color.Red
        Constants.MACHINE_STATUS_OFFLINE -> androidx.compose.ui.graphics.Color.Gray
        else -> androidx.compose.ui.graphics.Color.Gray
    }
}

fun String.getPriorityColor(): androidx.compose.ui.graphics.Color {
    return when (this.lowercase()) {
        Constants.PRIORITY_LOW -> androidx.compose.ui.graphics.Color.Green
        Constants.PRIORITY_MEDIUM -> androidx.compose.ui.graphics.Color.Yellow
        Constants.PRIORITY_HIGH -> androidx.compose.ui.graphics.Color(0xFFFFA500) // Orange
        Constants.PRIORITY_URGENT -> androidx.compose.ui.graphics.Color.Red
        else -> androidx.compose.ui.graphics.Color.Gray
    }
}

