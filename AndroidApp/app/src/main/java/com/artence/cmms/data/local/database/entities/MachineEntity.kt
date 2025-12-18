package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "machines",
    indices = [
        Index("status"),
        Index("productionLineId")
    ]
)
data class MachineEntity(
    @PrimaryKey val id: Int,
    val productionLineId: Int,
    val name: String,
    val serialNumber: String?,
    val model: String?,
    val manufacturer: String?,
    val status: String,
    val assetTag: String?,
    val createdAt: Long,
    val updatedAt: Long?
)
