package com.artence.cmms.ui.screens.settings

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.local.datastore.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SettingsUiState(
    val username: String? = null,
    val email: String? = null,
    val role: String? = null,
    val language: String = "en",
    val isDarkMode: Boolean = false,
    val notificationsEnabled: Boolean = true,
    val offlineMode: Boolean = true,
    val buildNumber: String = "1.0.0",
    val isLoggedOut: Boolean = false,
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val tokenManager: TokenManager
) : ViewModel() {

    private val _uiState = MutableStateFlow(SettingsUiState())
    val uiState: StateFlow<SettingsUiState> = _uiState.asStateFlow()

    init {
        loadSettings()
    }

    private fun loadSettings() {
        viewModelScope.launch {
            try {
                // Load user info from token manager
                val username = tokenManager.getUsername().toString()
                val email = "user@example.com" // TODO: Get from API
                val role = tokenManager.getRole().toString()

                _uiState.update {
                    it.copy(
                        username = username,
                        email = email,
                        role = role
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(error = "Failed to load settings")
                }
            }
        }
    }

    fun setLanguage(language: String) {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(language = language) }
                // TODO: Save to DataStore and apply locale change
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to change language") }
            }
        }
    }

    fun toggleDarkMode() {
        viewModelScope.launch {
            try {
                val newDarkMode = !_uiState.value.isDarkMode
                _uiState.update { it.copy(isDarkMode = newDarkMode) }
                // TODO: Save to DataStore and apply theme change
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to change theme") }
            }
        }
    }

    fun setNotifications(enabled: Boolean) {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(notificationsEnabled = enabled) }
                // TODO: Save to DataStore and register/unregister for notifications
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to change notification setting") }
            }
        }
    }

    fun setOfflineMode(enabled: Boolean) {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(offlineMode = enabled) }
                // TODO: Save to DataStore and adjust sync behavior
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "Failed to change offline mode") }
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            try {
                _uiState.update { it.copy(isLoading = true) }
                // Clear token and user data
                tokenManager.clearAll()
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        isLoggedOut = true
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "Failed to logout: ${e.message}"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

