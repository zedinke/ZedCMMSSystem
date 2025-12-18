package com.artence.cmms.domain.usecase.asset

import com.artence.cmms.data.repository.AssetRepository
import com.artence.cmms.domain.model.Asset
import javax.inject.Inject

class GetAssetByIdUseCase @Inject constructor(
    private val assetRepository: AssetRepository
) {
    suspend operator fun invoke(id: Int): Asset? {
        return assetRepository.getAssetById(id)
    }
}

