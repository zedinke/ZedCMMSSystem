package com.artence.cmms.ui.screens.inventory.create

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.CreateInventoryDto
import com.artence.cmms.domain.model.Inventory
import com.artence.cmms.data.repository.InventoryRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CreateInventoryUiState(
    val isLoading: Boolean = false,
    val isSuccess: Boolean = false,
    val error: String? = null,
    val inventory: Inventory? = null
)

@HiltViewModel
class CreateInventoryViewModel @Inject constructor(
    private val inventoryRepository: InventoryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateInventoryUiState())
    val uiState: StateFlow<CreateInventoryUiState> = _uiState.asStateFlow()

    fun createInventory(
        name: String,
        quantity: Int,
        minQuantity: Int,
        maxQuantity: Int,
        location: String?,
        assetId: Int? = null,
        partId: Int? = null
    ) {
        if (name.isBlank()) {
            _uiState.update { it.copy(error = "Name is required") }
            return
        }
        if (quantity < 0 || minQuantity < 0 || maxQuantity < 0) {
            _uiState.update { it.copy(error = "Quantities cannot be negative") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val dto = CreateInventoryDto(
                    name = name,
                    assetId = assetId,
                    partId = partId,
                    quantity = quantity,
                    minQuantity = minQuantity,
                    maxQuantity = maxQuantity,
                    location = location
                )
                val result = inventoryRepository.createInventory(dto)
                result.onSuccess { inventory ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isSuccess = true,
                            inventory = inventory
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = e.message ?: "Failed to create inventory"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to create inventory"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
