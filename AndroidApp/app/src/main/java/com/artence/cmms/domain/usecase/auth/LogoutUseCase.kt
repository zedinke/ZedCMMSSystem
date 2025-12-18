package com.artence.cmms.domain.usecase.auth

import com.artence.cmms.data.local.datastore.TokenManager
import com.artence.cmms.data.repository.AuthRepository
import javax.inject.Inject

class LogoutUseCase @Inject constructor(
    private val authRepository: AuthRepository,
    private val tokenManager: TokenManager
) {
    suspend operator fun invoke() {
        authRepository.logout()
        tokenManager.clearAll()
    }
}

