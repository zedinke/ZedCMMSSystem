package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "assets",
    indices = [
        Index("status"),
        Index("name"),
        Index("assetTag")
    ]
)
data class AssetEntity(
    @PrimaryKey val id: Int,
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
)

