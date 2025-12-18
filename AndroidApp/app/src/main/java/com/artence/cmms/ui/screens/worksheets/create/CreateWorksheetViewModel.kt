package com.artence.cmms.ui.screens.worksheets.create

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.CreateWorksheetDto
import com.artence.cmms.domain.model.Worksheet
import com.artence.cmms.data.repository.WorksheetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CreateWorksheetUiState(
    val isLoading: Boolean = false,
    val isSuccess: Boolean = false,
    val error: String? = null,
    val worksheet: Worksheet? = null
)

@HiltViewModel
class CreateWorksheetViewModel @Inject constructor(
    private val worksheetRepository: WorksheetRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateWorksheetUiState())
    val uiState: StateFlow<CreateWorksheetUiState> = _uiState.asStateFlow()

    fun createWorksheet(
        title: String,
        description: String?,
        priority: String?,
        status: String
    ) {
        if (title.isBlank()) {
            _uiState.update { it.copy(error = "Worksheet title is required") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val generatedNumber = "WS-${System.currentTimeMillis()}"
                val dto = CreateWorksheetDto(
                    worksheetNumber = generatedNumber,
                    title = title,
                    description = description,
                    type = "General",
                    priority = priority ?: "Low",
                    status = status,
                    assignedToUserId = null
                )
                val result = worksheetRepository.createWorksheet(dto)
                result.onSuccess { worksheet ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isSuccess = true,
                            worksheet = worksheet
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = e.message ?: "Failed to create worksheet"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to create worksheet"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
