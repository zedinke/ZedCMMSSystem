package com.artence.cmms.domain.model

import java.util.Date

data class Inventory(
    val id: String,
    val name: String,
    val description: String?,
    val quantity: Int,
    val minQuantity: Int,
    val maxQuantity: Int,
    val unit: String,
    val location: String,
    val partNumber: String?,
    val costPerUnit: Double,
    val supplier: String?,
    val lastRestockDate: Date?,
    val status: String,
    val createdAt: Date,
    val updatedAt: Date
)

