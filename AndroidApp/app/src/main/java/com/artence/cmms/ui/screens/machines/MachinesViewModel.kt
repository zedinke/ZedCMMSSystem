package com.artence.cmms.ui.screens.machines

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.domain.model.Machine
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class MachinesUiState(
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val machines: List<Machine> = emptyList(),
    val filterStatus: String? = null,
    val error: String? = null
)

@HiltViewModel
class MachinesViewModel @Inject constructor(
    // TODO: Inject repository when available
) : ViewModel() {

    private val _uiState = MutableStateFlow(MachinesUiState())
    val uiState: StateFlow<MachinesUiState> = _uiState.asStateFlow()

    fun load() {
        _uiState.value = _uiState.value.copy(isLoading = true)
        viewModelScope.launch {
            try {
                // TODO: gépek betöltése a repository-ból
                // Temporarily keep empty list
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun refreshMachines() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true)
            try {
                // TODO: frissítés repository hívással
                delay(300) // simulate short refresh
                _uiState.value = _uiState.value.copy(isRefreshing = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isRefreshing = false,
                    error = e.message
                )
            }
        }
    }

    fun setStatusFilter(status: String?) {
        _uiState.value = _uiState.value.copy(filterStatus = status)
        // Optionally filter machines list based on status when repository implemented
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
