package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Reports summary response DTO
 */
data class ReportsSummaryDto(
    @SerializedName("machines_total") val machinesTotal: Int,
    @SerializedName("worksheets_open") val worksheetsOpen: Int,
    @SerializedName("inventory_low_stock") val inventoryLowStock: Int,
    @SerializedName("pm_due_this_week") val pmDueThisWeek: Int
)

