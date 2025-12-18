package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.CreateUserDto
import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.UpdateUserDto
import com.artence.cmms.data.remote.dto.UserDto
import retrofit2.Response
import retrofit2.http.*

interface UserApi {
    @GET("users")
    suspend fun getUsers(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100,
        @Query("role_name") roleName: String? = null,
        @Query("status") status: String? = null
    ): Response<ListResponse<UserDto>>

    @GET("users/{id}")
    suspend fun getUserById(@Path("id") id: Int): Response<UserDto>

    @POST("users")
    suspend fun createUser(@Body user: CreateUserDto): Response<UserDto>

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") id: Int,
        @Body user: UpdateUserDto
    ): Response<UserDto>

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: Int): Response<Unit>

    @POST("users/{id}/reset-password")
    suspend fun resetPassword(@Path("id") id: Int): Response<UserDto>
}

