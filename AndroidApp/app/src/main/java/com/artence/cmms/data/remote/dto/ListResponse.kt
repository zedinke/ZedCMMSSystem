package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

/**
 * Generic list response wrapper for paginated API responses
 */
data class ListResponse<T>(
    @SerializedName("total") val total: Int,
    @SerializedName("items") val items: List<T>
)

