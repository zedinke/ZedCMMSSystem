package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.CreateWorksheetDto
import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.UpdateWorksheetDto
import com.artence.cmms.data.remote.dto.WorksheetDto
import retrofit2.Response
import retrofit2.http.*

interface WorksheetApi {
    @GET("worksheets")
    suspend fun getWorksheets(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100,
        @Query("status") status: String? = null,
        @Query("machine_id") machineId: Int? = null
    ): Response<ListResponse<WorksheetDto>>

    @GET("worksheets/{id}")
    suspend fun getWorksheetById(@Path("id") id: Int): Response<WorksheetDto>

    @POST("worksheets")
    suspend fun createWorksheet(@Body worksheet: CreateWorksheetDto): Response<WorksheetDto>

    @PUT("worksheets/{id}")
    suspend fun updateWorksheet(
        @Path("id") id: Int,
        @Body worksheet: UpdateWorksheetDto
    ): Response<WorksheetDto>

    @DELETE("worksheets/{id}")
    suspend fun deleteWorksheet(@Path("id") id: Int): Response<Unit>
}

