package com.artence.cmms.domain.model

import java.text.SimpleDateFormat
import java.util.*

data class Inventory(
    val id: Int,
    val assetId: Int?,
    val assetName: String?,
    val partId: Int?,
    val partName: String?,
    val quantity: Int,
    val minQuantity: Int,
    val maxQuantity: Int,
    val location: String?,
    val lastUpdated: Long,
    val createdAt: Long
) {
    // Helper to check if stock is low
    fun isLow(): Boolean = quantity <= minQuantity

    // Helper to check if stock is high
    fun isHigh(): Boolean = quantity >= maxQuantity

    // Helper to get status
    fun getStatus(): String = when {
        quantity == 0 -> "Out of Stock"
        quantity <= minQuantity -> "Low Stock"
        quantity >= maxQuantity -> "Overstocked"
        else -> "Normal"
    }

    val createdAtFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(createdAt))

    val lastUpdatedFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(lastUpdated))
}

