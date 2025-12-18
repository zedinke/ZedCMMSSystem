package com.artence.cmms.ui.screens.assets

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.artence.cmms.domain.model.Asset
import com.artence.cmms.domain.usecase.asset.GetAssetsUseCase
import com.artence.cmms.domain.usecase.asset.RefreshAssetsUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

// UI állapot a képernyőhöz
data class AssetsUiState(
    val assets: List<Asset> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class AssetsViewModel @Inject constructor(
    private val getAssetsUseCase: GetAssetsUseCase,
    private val refreshAssetsUseCase: RefreshAssetsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(AssetsUiState())
    val uiState: StateFlow<AssetsUiState> = _uiState.asStateFlow()

    init {
        loadAssets()
        refreshAssets()
    }

    private fun loadAssets() {
        _uiState.value = _uiState.value.copy(isLoading = true)
        viewModelScope.launch {
            try {
                getAssetsUseCase().collect { assets ->
                    _uiState.value = _uiState.value.copy(
                        assets = assets,
                        isLoading = false,
                        error = null
                    )
                }
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message ?: "Nem sikerült betölteni az eszközöket"
                )
            }
        }
    }

    fun refreshAssets() {
        _uiState.value = _uiState.value.copy(isRefreshing = true)
        viewModelScope.launch {
            val result = refreshAssetsUseCase()
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
                        error = error.message ?: "Nem sikerült frissíteni az eszközöket"
                    )
                }
            )
        }
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(error = null)
    }
}
