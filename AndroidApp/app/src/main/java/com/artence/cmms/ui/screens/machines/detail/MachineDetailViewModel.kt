package com.artence.cmms.ui.screens.machines.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.UpdateMachineDto
import com.artence.cmms.domain.model.Machine
import com.artence.cmms.data.repository.MachineRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class MachineDetailUiState(
    val machine: Machine? = null,
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val isDeleted: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class MachineDetailViewModel @Inject constructor(
    private val machineRepository: MachineRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(MachineDetailUiState())
    val uiState: StateFlow<MachineDetailUiState> = _uiState.asStateFlow()

    fun loadMachine(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val machine = machineRepository.getMachineById(id)
                _uiState.update {
                    it.copy(
                        machine = machine,
                        isLoading = false,
                        error = if (machine == null) "Machine not found" else null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load machine"
                    )
                }
            }
        }
    }

    fun updateMachine(
        id: Int,
        name: String,
        serialNumber: String?,
        model: String?,
        manufacturer: String?,
        status: String
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val dto = UpdateMachineDto(
                    productionLineId = null,
                    name = name,
                    serialNumber = serialNumber,
                    model = model,
                    manufacturer = manufacturer,
                    status = status,
                    assetTag = null,
                    description = null,
                    installDate = null
                )
                val result = machineRepository.updateMachine(id, dto)
                result.onSuccess { machine ->
                    _uiState.update {
                        it.copy(
                            machine = machine,
                            isSaving = false
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to update machine"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to update machine"
                    )
                }
            }
        }
    }

    fun deleteMachine(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val result = machineRepository.deleteMachine(id)
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
                            error = e.message ?: "Failed to delete machine"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to delete machine"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
