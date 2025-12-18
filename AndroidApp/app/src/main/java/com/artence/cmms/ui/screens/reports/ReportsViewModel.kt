package com.artence.cmms.ui.screens.reports

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.repository.ReportsRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ReportsUiState(
    val machinesTotal: Int = 0,
    val worksheetsOpen: Int = 0,
    val inventoryLowStock: Int = 0,
    val pmDueThisWeek: Int = 0,
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class ReportsViewModel @Inject constructor(
    private val reportsRepository: ReportsRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ReportsUiState())
    val uiState: StateFlow<ReportsUiState> = _uiState.asStateFlow()

    init {
        loadReportData()
    }

    private fun loadReportData() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val result = reportsRepository.getReportsSummary()
                result.fold(
                    onSuccess = { summary ->
                        _uiState.update {
                            it.copy(
                                machinesTotal = summary.machinesTotal,
                                worksheetsOpen = summary.worksheetsOpen,
                                inventoryLowStock = summary.inventoryLowStock,
                                pmDueThisWeek = summary.pmDueThisWeek,
                                isLoading = false
                            )
                        }
                    },
                    onFailure = { error ->
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                error = error.message ?: "Failed to load reports"
                            )
                        }
                    }
                )
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load reports"
                    )
                }
            }
        }
    }

    fun refreshReports() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            try {
                val result = reportsRepository.getReportsSummary()
                result.fold(
                    onSuccess = { summary ->
                        _uiState.update {
                            it.copy(
                                machinesTotal = summary.machinesTotal,
                                worksheetsOpen = summary.worksheetsOpen,
                                inventoryLowStock = summary.inventoryLowStock,
                                pmDueThisWeek = summary.pmDueThisWeek,
                                isRefreshing = false
                            )
                        }
                    },
                    onFailure = { error ->
                        _uiState.update {
                            it.copy(
                                isRefreshing = false,
                                error = error.message ?: "Failed to refresh reports"
                            )
                        }
                    }
                )
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isRefreshing = false,
                        error = e.message ?: "Failed to refresh reports"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

