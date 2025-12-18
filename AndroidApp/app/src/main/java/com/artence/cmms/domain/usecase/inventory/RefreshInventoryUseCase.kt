package com.artence.cmms.domain.usecase.inventory

import com.artence.cmms.data.repository.InventoryRepository
import javax.inject.Inject

class RefreshInventoryUseCase @Inject constructor(
    private val inventoryRepository: InventoryRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return inventoryRepository.refreshInventory()
    }
}

