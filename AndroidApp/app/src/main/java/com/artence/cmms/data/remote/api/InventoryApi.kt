package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.CreateInventoryDto
import com.artence.cmms.data.remote.dto.InventoryDto
import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.UpdateInventoryDto
import retrofit2.Response
import retrofit2.http.*

interface InventoryApi {
    // Note: Backend uses /api/inventory endpoint
    @GET("inventory")
    suspend fun getInventory(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100
    ): Response<ListResponse<InventoryDto>>

    @GET("inventory/{id}")
    suspend fun getInventoryById(@Path("id") id: Int): Response<InventoryDto>

    @POST("inventory")
    suspend fun createInventory(@Body inventory: CreateInventoryDto): Response<InventoryDto>

    @PUT("inventory/{id}")
    suspend fun updateInventory(
        @Path("id") id: Int,
        @Body inventory: UpdateInventoryDto
    ): Response<InventoryDto>

    @DELETE("inventory/{id}")
    suspend fun deleteInventory(@Path("id") id: Int): Response<Unit>
}

