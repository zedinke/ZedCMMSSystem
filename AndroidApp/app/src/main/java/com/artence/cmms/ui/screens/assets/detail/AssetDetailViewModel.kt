package com.artence.cmms.ui.screens.assets.detail

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.data.remote.dto.UpdateAssetDto
import com.artence.cmms.domain.model.Asset
import com.artence.cmms.data.repository.AssetRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AssetDetailUiState(
    val asset: Asset? = null,
    val isLoading: Boolean = false,
    val isSaving: Boolean = false,
    val isDeleted: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class AssetDetailViewModel @Inject constructor(
    private val assetRepository: AssetRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AssetDetailUiState())
    val uiState: StateFlow<AssetDetailUiState> = _uiState.asStateFlow()

    fun loadAsset(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val asset = assetRepository.getAssetById(id)
                _uiState.update {
                    it.copy(
                        asset = asset,
                        isLoading = false,
                        error = if (asset == null) "Asset not found" else null
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = e.message ?: "Failed to load asset"
                    )
                }
            }
        }
    }

    fun updateAsset(
        id: Int,
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
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val dto = UpdateAssetDto(
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
                val result = assetRepository.updateAsset(id, dto)
                result.onSuccess { asset ->
                    _uiState.update {
                        it.copy(
                            asset = asset,
                            isSaving = false
                        )
                    }
                }.onFailure { e ->
                    _uiState.update {
                        it.copy(
                            isSaving = false,
                            error = e.message ?: "Failed to update asset"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to update asset"
                    )
                }
            }
        }
    }

    fun deleteAsset(id: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }
            try {
                val result = assetRepository.deleteAsset(id)
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
                            error = e.message ?: "Failed to delete asset"
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSaving = false,
                        error = e.message ?: "Failed to delete asset"
                    )
                }
            }
        }
    }

    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}
