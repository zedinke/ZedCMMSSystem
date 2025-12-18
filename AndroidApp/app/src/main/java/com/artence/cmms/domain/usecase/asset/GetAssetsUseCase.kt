package com.artence.cmms.domain.usecase.asset

import com.artence.cmms.data.repository.AssetRepository
import com.artence.cmms.domain.model.Asset
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetAssetsUseCase @Inject constructor(
    private val assetRepository: AssetRepository
) {
    operator fun invoke(): Flow<List<Asset>> {
        return assetRepository.getAssets()
    }
}

