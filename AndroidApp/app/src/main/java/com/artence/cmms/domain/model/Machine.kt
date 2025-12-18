package com.artence.cmms.domain.model

import java.text.SimpleDateFormat
import java.util.*

data class Machine(
    val id: Int,
    val productionLineId: Int,
    val productionLineName: String?,
    val name: String,
    val serialNumber: String?,
    val model: String?,
    val manufacturer: String?,
    val status: String,
    val assetTag: String?,
    val description: String?,
    val installDate: Long?,
    val createdAt: Long,
    val updatedAt: Long?
) {
    val createdAtFormatted: String
        get() = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(createdAt))

    val updatedAtFormatted: String?
        get() = updatedAt?.let { SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date(it)) }

    val installDateFormatted: String?
        get() = installDate?.let { SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date(it)) }
}

