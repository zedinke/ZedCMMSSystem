package com.artence.cmms.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "inventory")
data class InventoryEntity(
    @PrimaryKey val id: String,
    val name: String,
    val description: String? = null,
    val quantity: Int,
    val minQuantity: Int,
    val maxQuantity: Int,
    val unit: String,
    val location: String,
    val partNumber: String? = null,
    val costPerUnit: Double,
    val supplier: String? = null,
    val lastRestockDate: Date? = null,
    val status: String, // "IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"
    val createdAt: Date,
    val updatedAt: Date,
    val isDeleted: Boolean = false
)

