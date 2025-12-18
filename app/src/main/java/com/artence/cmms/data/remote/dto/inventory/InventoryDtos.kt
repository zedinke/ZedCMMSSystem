package com.artence.cmms.data.remote.dto.inventory

import com.google.gson.annotations.SerializedName
import java.util.Date

data class InventoryDto(
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

data class CreateInventoryDto(
    val name: String,
    val description: String?,
    val quantity: Int,
    val minQuantity: Int,
    val maxQuantity: Int,
    val unit: String,
    val location: String,
    val partNumber: String?,
    val costPerUnit: Double,
    val supplier: String?
)

data class UpdateInventoryDto(
    val name: String?,
    val description: String?,
    val quantity: Int?,
    val minQuantity: Int?,
    val maxQuantity: Int?,
    val unit: String?,
    val location: String?,
    val partNumber: String?,
    val costPerUnit: Double?,
    val supplier: String?
)

