package com.artence.cmms.domain.usecase.asset

import com.artence.cmms.data.repository.AssetRepository
import javax.inject.Inject

class RefreshAssetsUseCase @Inject constructor(
    private val assetRepository: AssetRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return assetRepository.refreshAssets()
    }
}

