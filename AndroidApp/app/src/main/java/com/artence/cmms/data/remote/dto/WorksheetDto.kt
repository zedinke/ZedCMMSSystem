package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

data class WorksheetDto(
    @SerializedName("id") val id: Int,
    @SerializedName("machine_id") val machineId: Int,
    @SerializedName("maintenance_type") val maintenanceType: String,
    @SerializedName("description") val description: String?,
    @SerializedName("assigned_to_user_id") val assignedToUserId: Int?,
    @SerializedName("status") val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String?,
    @SerializedName("completed_at") val completedAt: String?,
    @SerializedName("worksheet_number") val worksheetNumber: String? = null,
    @SerializedName("title") val title: String? = null,
    @SerializedName("type") val type: String? = null,
    @SerializedName("priority") val priority: String? = null,
    @SerializedName("scheduled_start_date") val scheduledStartDate: String? = null,
    @SerializedName("scheduled_end_date") val scheduledEndDate: String? = null,
    @SerializedName("actual_start_date") val actualStartDate: String? = null,
    @SerializedName("actual_end_date") val actualEndDate: String? = null,
    @SerializedName("completion_notes") val completionNotes: String? = null,
    @SerializedName("parts_used") val partsUsed: List<Map<String, Any>>? = null
)

data class CreateWorksheetDto(
    @SerializedName("machine_id") val machineId: Int? = null,
    @SerializedName("maintenance_type") val maintenanceType: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("assigned_to_user_id") val assignedToUserId: Int? = null,
    @SerializedName("status") val status: String? = "pending",
    @SerializedName("worksheet_number") val worksheetNumber: String? = null,
    @SerializedName("title") val title: String? = null,
    @SerializedName("type") val type: String? = null,
    @SerializedName("priority") val priority: String? = null
)

data class UpdateWorksheetDto(
    @SerializedName("description") val description: String? = null,
    @SerializedName("assigned_to_user_id") val assignedToUserId: Int? = null,
    @SerializedName("status") val status: String? = null,
    @SerializedName("worksheet_number") val worksheetNumber: String? = null,
    @SerializedName("title") val title: String? = null,
    @SerializedName("type") val type: String? = null,
    @SerializedName("priority") val priority: String? = null,
    @SerializedName("scheduled_start_date") val scheduledStartDate: String? = null,
    @SerializedName("scheduled_end_date") val scheduledEndDate: String? = null,
    @SerializedName("actual_start_date") val actualStartDate: String? = null,
    @SerializedName("actual_end_date") val actualEndDate: String? = null,
    @SerializedName("completion_notes") val completionNotes: String? = null,
    @SerializedName("parts_used") val partsUsed: List<Map<String, Any>>? = null
)

