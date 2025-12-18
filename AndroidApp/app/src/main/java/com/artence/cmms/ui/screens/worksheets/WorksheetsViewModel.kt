package com.artence.cmms.ui.screens.worksheets

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.domain.model.Worksheet
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class WorksheetsUiState(
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val worksheets: List<Worksheet> = emptyList(),
    val filterStatus: String? = null,
    val error: String? = null
)

@HiltViewModel
class WorksheetsViewModel @Inject constructor(
    // TODO: Inject repository when available
) : ViewModel() {

    private val _uiState = MutableStateFlow(WorksheetsUiState())
    val uiState: StateFlow<WorksheetsUiState> = _uiState.asStateFlow()

    fun load() {
        _uiState.value = _uiState.value.copy(isLoading = true)
        viewModelScope.launch {
            try {
                // TODO: munkalapok betöltése repository-ból
                _uiState.value = _uiState.value.copy(isLoading = false)
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    fun refreshWorksheets() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true)
            try {
                // TODO: frissítés repository hívással
                delay(300)
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
        // TODO: apply filtering when worksheets are loaded
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
