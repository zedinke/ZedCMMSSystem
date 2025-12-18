package com.artence.cmms.ui.screens.inventory.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.UpdateInventoryDto
import com.artence.cmms.domain.model.Inventory
import com.artence.cmms.data.repository.InventoryRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class InventoryDetailUiState(
    val inventory: Inventory? = null,
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val isDeleted: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class InventoryDetailViewModel @Inject constructor(
    private val inventoryRepository: InventoryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(InventoryDetailUiState())
    val uiState: StateFlow<InventoryDetailUiState> = _uiState.asStateFlow()

    fun loadInventory(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val inventory = inventoryRepository.getInventoryById(id)
                _uiState.update {
                    it.copy(
                        inventory = inventory,
                        isLoading = false,
                        error = if (inventory == null) "Inventory item not found" else null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load inventory"
                    )
                }
            }
        }
    }

    fun updateInventory(
        id: Int,
        quantity: Int,
        minQuantity: Int,
        maxQuantity: Int,
        location: String?
    ) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val dto = UpdateInventoryDto(
                    quantity = quantity,
                    minQuantity = minQuantity,
                    maxQuantity = maxQuantity,
                    location = location
                )
                val result = inventoryRepository.updateInventory(id, dto)
                result.onSuccess { inventory ->
                    _uiState.update {
                        it.copy(
                            inventory = inventory,
                            isSaving = false
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to update inventory"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to update inventory"
                    )
                }
            }
        }
    }

    fun deleteInventory(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val result = inventoryRepository.deleteInventory(id)
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
                            error = e.message ?: "Failed to delete inventory"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to delete inventory"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
