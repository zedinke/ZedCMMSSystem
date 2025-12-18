package com.artence.cmms.domain.usecase.inventory

import com.artence.cmms.data.repository.InventoryRepository
import com.artence.cmms.domain.model.Inventory
import javax.inject.Inject

class GetInventoryByIdUseCase @Inject constructor(
    private val inventoryRepository: InventoryRepository
) {
    suspend operator fun invoke(id: Int): Inventory? {
        return inventoryRepository.getInventoryById(id)
    }
}

