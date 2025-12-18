package com.artence.cmms.ui.screens.inventory

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.domain.model.Inventory
import com.artence.cmms.domain.usecase.inventory.GetInventoryUseCase
import com.artence.cmms.domain.usecase.inventory.RefreshInventoryUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class InventoryUiState(
    val inventory: List<Inventory> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null,
    val filterStatus: String? = null // "all", "low", "high", "out"
)

@HiltViewModel
class InventoryViewModel @Inject constructor(
    private val getInventoryUseCase: GetInventoryUseCase,
    private val refreshInventoryUseCase: RefreshInventoryUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(InventoryUiState())
    val uiState: StateFlow<InventoryUiState> = _uiState.asStateFlow()

    init {
        loadInventory()
        refreshInventory()
    }

    private fun loadInventory() {
        viewModelScope.launch {
            getInventoryUseCase().collect { inventory ->
                _uiState.value = _uiState.value.copy(
                    inventory = filterInventory(inventory),
                    isLoading = false
                )
            }
        }
    }

    fun refreshInventory() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isRefreshing = true)

            val result = refreshInventoryUseCase()

            result.fold(
                onSuccess = {
                    _uiState.value = _uiState.value.copy(
                        isRefreshing = false,
                        error = null
                    )
                },
                onFailure = { error ->
                    _uiState.value = _uiState.value.copy(
                        isRefreshing = false,
                        error = error.message ?: "Failed to refresh inventory"
                    )
                }
            )
        }
    }

    fun setStatusFilter(status: String?) {
        _uiState.value = _uiState.value.copy(filterStatus = status)
        viewModelScope.launch {
            getInventoryUseCase().collect { inventory ->
                _uiState.value = _uiState.value.copy(
                    inventory = filterInventory(inventory)
                )
            }
        }
    }

    private fun filterInventory(inventory: List<Inventory>): List<Inventory> {
        val status = _uiState.value.filterStatus
        return when (status) {
            "low" -> inventory.filter { it.isLow() }
            "high" -> inventory.filter { it.isHigh() }
            "out" -> inventory.filter { it.quantity == 0 }
            else -> inventory
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}

