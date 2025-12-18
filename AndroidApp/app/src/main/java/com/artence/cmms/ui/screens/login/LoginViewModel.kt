package com.artence.cmms.ui.screens.login

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.domain.usecase.auth.LoginUseCase
import com.artence.cmms.util.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject
import android.util.Log

private const val TAG = "LoginViewModel"

data class LoginUiState(
    val isLoading: Boolean = false,
    val error: String? = null,
    val isSuccess: Boolean = false
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val loginUseCase: LoginUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun login(username: String, password: String) {
        Log.d(TAG, "login() called with username=$username")
        _uiState.value = _uiState.value.copy(isLoading = true, error = null)
        viewModelScope.launch {
            try {
                Log.d(TAG, "Executing loginUseCase...")
                when (val result = loginUseCase(username, password)) {
                    is Result.Success -> {
                        Log.d(TAG, "Login successful")
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            isSuccess = true,
                            error = null
                        )
                    }
                    is Result.Error -> {
                        Log.e(TAG, "Login error: ${result.message}")
                        _uiState.value = _uiState.value.copy(
                            isLoading = false,
                            isSuccess = false,
                            error = result.message
                        )
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Unexpected exception in login: ${e.message}", e)
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    isSuccess = false,
                    error = "Unexpected error: ${e.message}"
                )
            }
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
