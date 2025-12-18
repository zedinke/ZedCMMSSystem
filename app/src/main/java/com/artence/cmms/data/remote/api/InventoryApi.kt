package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.inventory.InventoryDto
import com.artence.cmms.data.remote.dto.inventory.CreateInventoryDto
import com.artence.cmms.data.remote.dto.inventory.UpdateInventoryDto
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path

interface InventoryApi {
    @GET("inventory")
    suspend fun getAllInventory(): List<InventoryDto>

    @GET("inventory/{id}")
    suspend fun getInventoryById(@Path("id") id: String): InventoryDto

    @POST("inventory")
    suspend fun createInventory(@Body inventory: CreateInventoryDto): InventoryDto

    @PUT("inventory/{id}")
    suspend fun updateInventory(
        @Path("id") id: String,
        @Body inventory: UpdateInventoryDto
    ): InventoryDto

    @DELETE("inventory/{id}")
    suspend fun deleteInventory(@Path("id") id: String)
}

