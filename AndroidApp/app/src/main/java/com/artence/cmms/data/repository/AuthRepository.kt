package com.artence.cmms.data.repository

import com.artence.cmms.data.local.datastore.TokenManager
import com.artence.cmms.data.remote.api.AuthApi
import com.artence.cmms.data.remote.dto.LoginRequest
import com.artence.cmms.util.DiagnosticsUtil
import javax.inject.Inject
import javax.inject.Singleton
import android.util.Log

private const val TAG = "AuthRepository"

@Singleton
class AuthRepository @Inject constructor(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager
) {

    suspend fun login(loginRequest: LoginRequest): Result<Unit> {
        return try {
            Log.d(TAG, "Logging in with username: ${loginRequest.username}")

            // Diagnostika futtatása
            Log.d(TAG, "=== Running diagnostics ===")
            Log.d(TAG, "DNS: ${DiagnosticsUtil.testDnsResolution()}")
            Log.d(TAG, "Server connectivity: ${DiagnosticsUtil.testServerConnectivity()}")
            Log.d(TAG, "Login endpoint: ${DiagnosticsUtil.testLoginEndpoint()}")
            Log.d(TAG, "=== End diagnostics ===")

            val response = authApi.login(loginRequest)
            Log.d(TAG, "Login response status: ${response.code()}, body: ${response.body()}, error: ${response.errorBody()?.string()}")

            if (response.isSuccessful && response.body() != null) {
                val tokenResponse = response.body()!!
                Log.d(TAG, "Login successful, saving token and user info")
                tokenManager.saveToken(tokenResponse.accessToken)
                tokenManager.saveUserInfo(
                    userId = tokenResponse.userId,
                    username = tokenResponse.username,
                    role = tokenResponse.roleName
                )
                Log.d(TAG, "Token and user info saved successfully")
                Result.success(Unit)
            } else {
                val errorMsg = "Login failed: ${response.code()} ${response.message()}"
                Log.e(TAG, errorMsg)
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Exception during login: ${e.message}", e)
            Result.failure(e)
        }
    }

    suspend fun logout() {
        Log.d(TAG, "Logging out")
        tokenManager.clearAll()
    }
}
