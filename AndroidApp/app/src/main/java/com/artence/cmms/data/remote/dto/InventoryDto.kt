package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * InventoryDto - Compatible with backend AssetResponse
 * Note: Backend uses Part model via /api/assets endpoint
 * The backend AssetResponse contains: id, name, asset_type, asset_tag, machine_id, status, created_at, updated_at
 */
data class InventoryDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("asset_type") val assetType: String,
    @SerializedName("asset_tag") val assetTag: String?,
    @SerializedName("machine_id") val machineId: Int?,
    @SerializedName("status") val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String?,
    // Legacy fields for backward compatibility (will be null from backend)
    @SerializedName("asset_id") val assetId: Int? = null,
    @SerializedName("asset_name") val assetName: String? = null,
    @SerializedName("part_id") val partId: Int? = null,
    @SerializedName("part_name") val partName: String? = null,
    @SerializedName("quantity") val quantity: Int? = null,
    @SerializedName("min_quantity") val minQuantity: Int? = null,
    @SerializedName("max_quantity") val maxQuantity: Int? = null,
    @SerializedName("location") val location: String? = null,
    @SerializedName("last_updated") val lastUpdated: String? = null
)

/**
 * CreateInventoryDto - Compatible with backend AssetCreate
 * Note: Backend expects: name, asset_type, asset_tag, machine_id, status, category, etc.
 */
data class CreateInventoryDto(
    @SerializedName("name") val name: String,
    @SerializedName("asset_type") val assetType: String? = "Spare",
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("machine_id") val machineId: Int? = null,
    @SerializedName("status") val status: String? = "active",
    @SerializedName("category") val category: String? = null,
    @SerializedName("description") val description: String? = null,
    // Legacy fields for backward compatibility
    @SerializedName("asset_id") val assetId: Int? = null,
    @SerializedName("part_id") val partId: Int? = null,
    @SerializedName("quantity") val quantity: Int? = null,
    @SerializedName("min_quantity") val minQuantity: Int? = null,
    @SerializedName("max_quantity") val maxQuantity: Int? = null,
    @SerializedName("location") val location: String? = null
)

/**
 * UpdateInventoryDto - Compatible with backend AssetUpdate
 */
data class UpdateInventoryDto(
    @SerializedName("name") val name: String? = null,
    @SerializedName("asset_type") val assetType: String? = null,
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("machine_id") val machineId: Int? = null,
    @SerializedName("status") val status: String? = null,
    @SerializedName("category") val category: String? = null,
    @SerializedName("description") val description: String? = null,
    // Legacy fields for backward compatibility
    @SerializedName("quantity") val quantity: Int? = null,
    @SerializedName("min_quantity") val minQuantity: Int? = null,
    @SerializedName("max_quantity") val maxQuantity: Int? = null,
    @SerializedName("location") val location: String? = null
)

