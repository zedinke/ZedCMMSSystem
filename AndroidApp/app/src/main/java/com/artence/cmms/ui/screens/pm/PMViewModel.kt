package com.artence.cmms.ui.screens.pm

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.repository.PMRepository
import com.artence.cmms.domain.model.PMTask
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PMUiState(
    val pmTasks: List<PMTask> = emptyList(),
    val filteredTasks: List<PMTask> = emptyList(),
    val overdueCount: Int = 0,
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val filterStatus: String? = null, // Scheduled, Overdue, In Progress, Completed
    val error: String? = null
)

@HiltViewModel
class PMViewModel @Inject constructor(
    private val pmRepository: PMRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(PMUiState())
    val uiState: StateFlow<PMUiState> = _uiState.asStateFlow()

    init {
        loadPMTasks()
        loadOverdueCount()
    }

    private fun loadPMTasks() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                pmRepository.getPMTasks().collectLatest { tasks ->
                    val filtered = if (_uiState.value.filterStatus != null) {
                        tasks.filter { it.status == _uiState.value.filterStatus }
                    } else {
                        tasks
                    }
                    _uiState.update {
                        it.copy(
                            pmTasks = tasks,
                            filteredTasks = filtered,
                            isLoading = false
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load PM tasks"
                    )
                }
            }
        }
    }

    private fun loadOverdueCount() {
        viewModelScope.launch {
            pmRepository.getOverdueTaskCount().collectLatest { count ->
                _uiState.update { it.copy(overdueCount = count) }
            }
        }
    }

    fun refreshPMTasks() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            try {
                pmRepository.refreshPMTasks().onSuccess {
                    _uiState.update { it.copy(isRefreshing = false) }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isRefreshing = false,
                            error = e.message ?: "Failed to refresh PM tasks"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isRefreshing = false,
                        error = e.message ?: "Failed to refresh PM tasks"
                    )
                }
            }
        }
    }

    fun setStatusFilter(status: String?) {
        val filtered = if (status != null) {
            _uiState.value.pmTasks.filter { it.status == status }
        } else {
            _uiState.value.pmTasks
        }
        _uiState.update {
            it.copy(
                filterStatus = status,
                filteredTasks = filtered
            )
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

