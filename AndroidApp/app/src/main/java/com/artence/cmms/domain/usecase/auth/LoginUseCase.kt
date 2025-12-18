package com.artence.cmms.domain.usecase.auth

import com.artence.cmms.data.repository.AuthRepository
import com.artence.cmms.data.remote.dto.LoginRequest
import com.artence.cmms.util.Result
import javax.inject.Inject

class LoginUseCase @Inject constructor(
    private val authRepository: AuthRepository
) {
    suspend operator fun invoke(username: String, password: String): Result<Unit> {
        // ===== PRODUCTION MODE (ÉLIVE BACKEND SZERVER) =====
        // Csatlakozik a valódi backend API szerverhez: http://116.203.226.140:8000/
        val req = LoginRequest(username = username, password = password)
        val kotlinResult = authRepository.login(req)
        return if (kotlinResult.isSuccess) {
            Result.Success(Unit)
        } else {
            Result.Error(kotlinResult.exceptionOrNull()?.message ?: "Sikertelen bejelentkezés")
        }
    }
}
