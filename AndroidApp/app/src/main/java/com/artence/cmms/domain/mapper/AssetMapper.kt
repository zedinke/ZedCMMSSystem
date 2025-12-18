package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.database.entities.AssetEntity
import com.artence.cmms.data.remote.dto.AssetDto
import com.artence.cmms.domain.model.Asset
import java.text.SimpleDateFormat
import java.util.Locale

private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())

fun AssetDto.toDomain(): Asset {
    return Asset(
        id = id,
        name = name,
        category = assetType,
        assetTag = assetTag,
        serialNumber = null,
        manufacturer = null,
        model = null,
        location = null,
        status = status,
        purchaseDate = null,
        purchasePrice = null,
        warrantyExpiry = null,
        description = null,
        createdAt = dateFormat.parse(createdAt)?.time ?: 0L,
        updatedAt = updatedAt?.let { dateFormat.parse(it)?.time }
    )
}

fun AssetEntity.toDomain(): Asset {
    return Asset(
        id = id,
        name = name,
        category = category,
        assetTag = assetTag,
        serialNumber = serialNumber,
        manufacturer = manufacturer,
        model = model,
        location = location,
        status = status,
        purchaseDate = purchaseDate,
        purchasePrice = purchasePrice,
        warrantyExpiry = warrantyExpiry,
        description = description,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
}

fun Asset.toEntity(): AssetEntity {
    return AssetEntity(
        id = id,
        name = name,
        category = category,
        assetTag = assetTag,
        serialNumber = serialNumber,
        manufacturer = manufacturer,
        model = model,
        location = location,
        status = status,
        purchaseDate = purchaseDate,
        purchasePrice = purchasePrice,
        warrantyExpiry = warrantyExpiry,
        description = description,
        createdAt = createdAt,
        updatedAt = updatedAt
    )
}

fun Asset.toDto(): AssetDto {
    return AssetDto(
        id = id,
        name = name,
        assetType = category ?: "component",
        assetTag = assetTag,
        machineId = null,
        status = status,
        createdAt = dateFormat.format(createdAt),
        updatedAt = updatedAt?.let { dateFormat.format(it) }
    )
}
