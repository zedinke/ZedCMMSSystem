package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.CreateMachineDto
import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.MachineDto
import com.artence.cmms.data.remote.dto.UpdateMachineDto
import retrofit2.Response
import retrofit2.http.*

interface MachineApi {
    @GET("machines")
    suspend fun getMachines(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100,
        @Query("status") status: String? = null
    ): Response<ListResponse<MachineDto>>

    @GET("machines/{id}")
    suspend fun getMachineById(@Path("id") id: Int): Response<MachineDto>

    @POST("machines")
    suspend fun createMachine(@Body machine: CreateMachineDto): Response<MachineDto>

    @PUT("machines/{id}")
    suspend fun updateMachine(
        @Path("id") id: Int,
        @Body machine: UpdateMachineDto
    ): Response<MachineDto>

    @DELETE("machines/{id}")
    suspend fun deleteMachine(@Path("id") id: Int): Response<Unit>
}

