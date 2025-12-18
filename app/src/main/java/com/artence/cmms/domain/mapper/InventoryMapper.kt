package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.entity.InventoryEntity
import com.artence.cmms.data.remote.dto.inventory.InventoryDto
import com.artence.cmms.domain.model.Inventory
import java.util.Date

object InventoryMapper {
    fun entityToDomain(entity: InventoryEntity): Inventory = Inventory(
        id = entity.id,
        name = entity.name,
        description = entity.description,
        quantity = entity.quantity,
        minQuantity = entity.minQuantity,
        maxQuantity = entity.maxQuantity,
        unit = entity.unit,
        location = entity.location,
        partNumber = entity.partNumber,
        costPerUnit = entity.costPerUnit,
        supplier = entity.supplier,
        lastRestockDate = entity.lastRestockDate,
        status = entity.status,
        createdAt = entity.createdAt,
        updatedAt = entity.updatedAt
    )

    fun dtoToDomain(dto: InventoryDto): Inventory = Inventory(
        id = dto.id,
        name = dto.name,
        description = dto.description,
        quantity = dto.quantity,
        minQuantity = dto.minQuantity,
        maxQuantity = dto.maxQuantity,
        unit = dto.unit,
        location = dto.location,
        partNumber = dto.partNumber,
        costPerUnit = dto.costPerUnit,
        supplier = dto.supplier,
        lastRestockDate = dto.lastRestockDate,
        status = dto.status,
        createdAt = dto.createdAt,
        updatedAt = dto.updatedAt
    )

    fun dtoToEntity(dto: InventoryDto): InventoryEntity = InventoryEntity(
        id = dto.id,
        name = dto.name,
        description = dto.description,
        quantity = dto.quantity,
        minQuantity = dto.minQuantity,
        maxQuantity = dto.maxQuantity,
        unit = dto.unit,
        location = dto.location,
        partNumber = dto.partNumber,
        costPerUnit = dto.costPerUnit,
        supplier = dto.supplier,
        lastRestockDate = dto.lastRestockDate,
        status = dto.status,
        createdAt = dto.createdAt,
        updatedAt = dto.updatedAt
    )

    fun domainToEntity(domain: Inventory): InventoryEntity = InventoryEntity(
        id = domain.id,
        name = domain.name,
        description = domain.description,
        quantity = domain.quantity,
        minQuantity = domain.minQuantity,
        maxQuantity = domain.maxQuantity,
        unit = domain.unit,
        location = domain.location,
        partNumber = domain.partNumber,
        costPerUnit = domain.costPerUnit,
        supplier = domain.supplier,
        lastRestockDate = domain.lastRestockDate,
        status = domain.status,
        createdAt = domain.createdAt,
        updatedAt = domain.updatedAt
    )
}

