package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.LoginRequest
import com.artence.cmms.data.remote.dto.TokenResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {
    @POST("v1/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>
}
