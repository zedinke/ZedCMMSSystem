package com.artence.cmms.ui.screens.assets.create

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.CreateAssetDto
import com.artence.cmms.domain.model.Asset
import com.artence.cmms.data.repository.AssetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class CreateAssetUiState(
    val isLoading: Boolean = false,
    val isSuccess: Boolean = false,
    val error: String? = null,
    val asset: Asset? = null
)

@HiltViewModel
class CreateAssetViewModel @Inject constructor(
    private val assetRepository: AssetRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CreateAssetUiState())
    val uiState: StateFlow<CreateAssetUiState> = _uiState.asStateFlow()

    fun createAsset(
        name: String,
        serialNumber: String?,
        model: String?,
        manufacturer: String?,
        status: String,
        category: String? = null,
        assetTag: String? = null,
        location: String? = null,
        purchaseDate: String? = null,
        purchasePrice: Double? = null,
        warrantyExpiry: String? = null,
        description: String? = null
    ) {
        if (name.isBlank()) {
            _uiState.update { it.copy(error = "Asset name is required") }
            return
        }

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val dto = CreateAssetDto(
                    name = name,
                    category = category,
                    assetTag = assetTag,
                    serialNumber = serialNumber,
                    manufacturer = manufacturer,
                    model = model,
                    location = location,
                    status = status,
                    purchaseDate = purchaseDate,
                    purchasePrice = purchasePrice,
                    warrantyExpiry = warrantyExpiry,
                    description = description
                )
                val result = assetRepository.createAsset(dto)
                result.onSuccess { asset ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            isSuccess = true,
                            asset = asset
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            error = e.message ?: "Failed to create asset"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to create asset"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
