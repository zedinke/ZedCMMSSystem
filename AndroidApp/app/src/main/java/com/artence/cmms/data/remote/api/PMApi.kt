package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.pm.CreatePMTaskDto
import com.artence.cmms.data.remote.dto.pm.ExecutePMTaskDto
import com.artence.cmms.data.remote.dto.pm.PMTaskDto
import com.artence.cmms.data.remote.dto.pm.UpdatePMTaskDto
import retrofit2.Response
import retrofit2.http.*

interface PMApi {
    // Note: Backend uses /api/v1/pm prefix (router prefix is /api/v1/pm, app.py adds /api)
    // So the full path is /api/api/v1/pm/tasks, but the actual endpoint should be /api/v1/pm/tasks
    // Since BASE_URL already includes /api/, we use v1/pm here
    @GET("v1/pm/tasks")
    suspend fun getPMTasks(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100
    ): Response<List<PMTaskDto>>

    @GET("v1/pm/tasks/{id}")
    suspend fun getPMTaskById(@Path("id") id: Int): Response<PMTaskDto>

    @GET("v1/pm/tasks/machine/{machineId}")
    suspend fun getPMTasksByMachine(@Path("machineId") machineId: Int): Response<List<PMTaskDto>>

    @GET("v1/pm/tasks/upcoming")
    suspend fun getUpcomingPMTasks(@Query("limit") limit: Int = 10): Response<List<PMTaskDto>>

    @POST("v1/pm/tasks")
    suspend fun createPMTask(@Body task: CreatePMTaskDto): Response<PMTaskDto>

    @PUT("v1/pm/tasks/{id}")
    suspend fun updatePMTask(
        @Path("id") id: Int,
        @Body task: UpdatePMTaskDto
    ): Response<PMTaskDto>

    @POST("v1/pm/tasks/{id}/execute")
    suspend fun executePMTask(
        @Path("id") id: Int,
        @Body data: ExecutePMTaskDto
    ): Response<PMTaskDto>

    @DELETE("v1/pm/tasks/{id}")
    suspend fun deletePMTask(@Path("id") id: Int): Response<Unit>
}

