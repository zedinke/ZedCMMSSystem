package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

data class MachineDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("model") val model: String?,
    @SerializedName("serial_number") val serialNumber: String?,
    @SerializedName("production_line_id") val productionLineId: Int?,
    @SerializedName("status") val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String?,
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("install_date") val installDate: String? = null
)

data class CreateMachineDto(
    @SerializedName("name") val name: String,
    @SerializedName("model") val model: String? = null,
    @SerializedName("serial_number") val serialNumber: String? = null,
    @SerializedName("production_line_id") val productionLineId: Int? = null,
    @SerializedName("status") val status: String? = "operational",
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("install_date") val installDate: String? = null
)

data class UpdateMachineDto(
    @SerializedName("name") val name: String? = null,
    @SerializedName("model") val model: String? = null,
    @SerializedName("serial_number") val serialNumber: String? = null,
    @SerializedName("production_line_id") val productionLineId: Int? = null,
    @SerializedName("status") val status: String? = null,
    @SerializedName("manufacturer") val manufacturer: String? = null,
    @SerializedName("asset_tag") val assetTag: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("install_date") val installDate: String? = null
)

