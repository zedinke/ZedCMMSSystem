package com.artence.cmms.ui.screens.worksheets.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.UpdateWorksheetDto
import com.artence.cmms.domain.model.Worksheet
import com.artence.cmms.data.repository.WorksheetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class WorksheetDetailUiState(
    val worksheet: Worksheet? = null,
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val isDeleted: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class WorksheetDetailViewModel @Inject constructor(
    private val worksheetRepository: WorksheetRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(WorksheetDetailUiState())
    val uiState: StateFlow<WorksheetDetailUiState> = _uiState.asStateFlow()

    fun loadWorksheet(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val worksheet = worksheetRepository.getWorksheetById(id)
                _uiState.update {
                    it.copy(
                        worksheet = worksheet,
                        isLoading = false,
                        error = if (worksheet == null) "Worksheet not found" else null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load worksheet"
                    )
                }
            }
        }
    }

    fun updateWorksheet(
        id: Int,
        title: String,
        description: String?,
        priority: String?
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val dto = UpdateWorksheetDto(
                    title = title,
                    worksheetNumber = null,
                    description = description,
                    type = null,
                    priority = priority,
                    status = null,
                    assignedToUserId = null,
                    scheduledStartDate = null,
                    scheduledEndDate = null,
                    actualStartDate = null,
                    actualEndDate = null,
                    completionNotes = null,
                    partsUsed = null
                )
                val result = worksheetRepository.updateWorksheet(id, dto)
                result.onSuccess { worksheet ->
                    _uiState.update {
                        it.copy(
                            worksheet = worksheet,
                            isSaving = false
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to update worksheet"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to update worksheet"
                    )
                }
            }
        }
    }

    fun updateWorksheetStatus(id: Int, status: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val dto = UpdateWorksheetDto(
                    title = null,
                    worksheetNumber = null,
                    description = null,
                    type = null,
                    priority = null,
                    status = status,
                    assignedToUserId = null,
                    scheduledStartDate = null,
                    scheduledEndDate = null,
                    actualStartDate = null,
                    actualEndDate = null,
                    completionNotes = null,
                    partsUsed = null
                )
                val result = worksheetRepository.updateWorksheet(id, dto)
                result.onSuccess { worksheet ->
                    _uiState.update {
                        it.copy(
                            worksheet = worksheet,
                            isSaving = false
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to update worksheet status"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to update worksheet status"
                    )
                }
            }
        }
    }

    fun deleteWorksheet(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val result = worksheetRepository.deleteWorksheet(id)
                result.onSuccess {
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            isDeleted = true
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to delete worksheet"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to delete worksheet"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

