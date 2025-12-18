package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

data class AssetDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("asset_type") val assetType: String,
    @SerializedName("asset_tag") val assetTag: String?,
    @SerializedName("machine_id") val machineId: Int?,
    @SerializedName("status") val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String?,
    @SerializedName("category") val category: String? = null,
    @SerializedName("serial_number") val serialNumber: String? = null,
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("model") val model: String? = null,
    @SerializedName("location") val location: String? = null,
    @SerializedName("purchase_date") val purchaseDate: String? = null,
    @SerializedName("purchase_price") val purchasePrice: Double? = null,
    @SerializedName("warranty_expiry") val warrantyExpiry: String? = null,
    @SerializedName("description") val description: String? = null
)

data class CreateAssetDto(
    @SerializedName("name") val name: String,
    @SerializedName("asset_type") val assetType: String? = "Spare",
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("machine_id") val machineId: Int? = null,
    @SerializedName("status") val status: String? = "active",
    @SerializedName("category") val category: String? = null,
    @SerializedName("serial_number") val serialNumber: String? = null,
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("model") val model: String? = null,
    @SerializedName("location") val location: String? = null,
    @SerializedName("purchase_date") val purchaseDate: String? = null,
    @SerializedName("purchase_price") val purchasePrice: Double? = null,
    @SerializedName("warranty_expiry") val warrantyExpiry: String? = null,
    @SerializedName("description") val description: String? = null
)

data class UpdateAssetDto(
    @SerializedName("name") val name: String? = null,
    @SerializedName("asset_type") val assetType: String? = null,
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("machine_id") val machineId: Int? = null,
    @SerializedName("status") val status: String? = null,
    @SerializedName("category") val category: String? = null,
    @SerializedName("serial_number") val serialNumber: String? = null,
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("model") val model: String? = null,
    @SerializedName("location") val location: String? = null,
    @SerializedName("purchase_date") val purchaseDate: String? = null,
    @SerializedName("purchase_price") val purchasePrice: Double? = null,
    @SerializedName("warranty_expiry") val warrantyExpiry: String? = null,
    @SerializedName("description") val description: String? = null
)
