package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Index

@Entity(
    tableName = "inventory",
    indices = [
        Index("location")
    ]
)
data class InventoryEntity(
    @PrimaryKey val id: Int,
    val partId: Int?,
    val assetId: Int?,
    val quantity: Int,
    val minQuantity: Int,
    val maxQuantity: Int,
    val location: String?,
    val lastUpdated: Long,
    val createdAt: Long
)
