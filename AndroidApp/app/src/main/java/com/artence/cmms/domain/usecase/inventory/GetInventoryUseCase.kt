package com.artence.cmms.domain.usecase.inventory

import com.artence.cmms.data.repository.InventoryRepository
import com.artence.cmms.domain.model.Inventory
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetInventoryUseCase @Inject constructor(
    private val inventoryRepository: InventoryRepository
) {
    operator fun invoke(): Flow<List<Inventory>> {
        return inventoryRepository.getInventory()
    }
}

