package com.artence.cmms.domain.model

import java.text.SimpleDateFormat
import java.util.*

data class Asset(
    val id: Int,
    val name: String,
    val category: String?,
    val assetTag: String?,
    val serialNumber: String?,
    val manufacturer: String?,
    val model: String?,
    val location: String?,
    val status: String,
    val purchaseDate: Long?,
    val purchasePrice: Double?,
    val warrantyExpiry: Long?,
    val description: String?,
    val createdAt: Long,
    val updatedAt: Long?
) {
    val createdAtFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(createdAt))

    val updatedAtFormatted: String?
        get() = updatedAt?.let { SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(it)) }
}

