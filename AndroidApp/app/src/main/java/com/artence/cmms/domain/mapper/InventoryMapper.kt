package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.database.entities.InventoryEntity
import com.artence.cmms.data.remote.dto.InventoryDto
import com.artence.cmms.domain.model.Inventory
import com.artence.cmms.util.toTimestamp

object InventoryMapper {

    fun fromEntity(entity: InventoryEntity): Inventory {
        return Inventory(
            id = entity.id,
            assetId = entity.assetId,
            assetName = null,
            partId = entity.partId,
            partName = null,
            quantity = entity.quantity,
            minQuantity = entity.minQuantity,
            maxQuantity = entity.maxQuantity,
            location = entity.location,
            lastUpdated = entity.lastUpdated,
            createdAt = entity.createdAt
        )
    }

    fun toEntity(inventory: Inventory): InventoryEntity {
        return InventoryEntity(
            id = inventory.id,
            assetId = inventory.assetId,
            partId = inventory.partId,
            quantity = inventory.quantity,
            minQuantity = inventory.minQuantity,
            maxQuantity = inventory.maxQuantity,
            location = inventory.location,
            lastUpdated = inventory.lastUpdated,
            createdAt = inventory.createdAt
        )
    }

    fun fromDto(dto: InventoryDto): Inventory {
        return Inventory(
            id = dto.id,
            // Map from new AssetResponse structure
            assetId = dto.machineId, // Use machine_id as asset_id
            assetName = dto.name, // Use name as asset_name
            partId = dto.id, // Use id as part_id
            partName = dto.name, // Use name as part_name
            quantity = dto.quantity ?: 0, // Default to 0 if null
            minQuantity = dto.minQuantity ?: 0,
            maxQuantity = dto.maxQuantity ?: 0,
            location = dto.location,
            lastUpdated = dto.updatedAt?.toTimestamp() ?: dto.lastUpdated?.toTimestamp() ?: dto.createdAt.toTimestamp(),
            createdAt = dto.createdAt.toTimestamp()
        )
    }

    fun dtoToEntity(dto: InventoryDto): InventoryEntity {
        return InventoryEntity(
            id = dto.id,
            assetId = dto.machineId, // Use machine_id as asset_id
            partId = dto.id, // Use id as part_id
            quantity = dto.quantity ?: 0, // Default to 0 if null
            minQuantity = dto.minQuantity ?: 0,
            maxQuantity = dto.maxQuantity ?: 0,
            location = dto.location,
            lastUpdated = dto.updatedAt?.toTimestamp() ?: dto.lastUpdated?.toTimestamp() ?: dto.createdAt.toTimestamp(),
            createdAt = dto.createdAt.toTimestamp()
        )
    }
}

