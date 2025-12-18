package com.artence.cmms.data.repository

import com.artence.cmms.data.local.dao.InventoryDao
import com.artence.cmms.data.remote.api.InventoryApi
import com.artence.cmms.data.remote.dto.inventory.CreateInventoryDto
import com.artence.cmms.data.remote.dto.inventory.UpdateInventoryDto
import com.artence.cmms.domain.mapper.InventoryMapper
import com.artence.cmms.domain.model.Inventory
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class InventoryRepository @Inject constructor(
    private val inventoryDao: InventoryDao,
    private val inventoryApi: InventoryApi
) {
    fun getAllInventory(): Flow<List<Inventory>> =
        inventoryDao.getAllInventory().map { entities ->
            entities.map { InventoryMapper.entityToDomain(it) }
        }

    fun getInventoryByStatus(status: String): Flow<List<Inventory>> =
        inventoryDao.getInventoryByStatus(status).map { entities ->
            entities.map { InventoryMapper.entityToDomain(it) }
        }

    fun getLowStockItems(): Flow<List<Inventory>> =
        inventoryDao.getLowStockItems().map { entities ->
            entities.map { InventoryMapper.entityToDomain(it) }
        }

    suspend fun getInventoryById(id: String): Inventory? {
        val entity = inventoryDao.getInventoryById(id)
        return entity?.let { InventoryMapper.entityToDomain(it) }
    }

    suspend fun refreshInventory() {
        try {
            val inventories = inventoryApi.getAllInventory()
            val entities = inventories.map { InventoryMapper.dtoToEntity(it) }
            inventoryDao.insertAllInventory(entities)
        } catch (e: Exception) {
            throw e
        }
    }

    suspend fun createInventory(inventory: CreateInventoryDto): Inventory {
        val dto = inventoryApi.createInventory(inventory)
        val entity = InventoryMapper.dtoToEntity(dto)
        inventoryDao.insertInventory(entity)
        return InventoryMapper.dtoToDomain(dto)
    }

    suspend fun updateInventory(id: String, inventory: UpdateInventoryDto): Inventory {
        val dto = inventoryApi.updateInventory(id, inventory)
        val entity = InventoryMapper.dtoToEntity(dto)
        inventoryDao.updateInventory(entity)
        return InventoryMapper.dtoToDomain(dto)
    }

    suspend fun deleteInventory(id: String) {
        inventoryApi.deleteInventory(id)
        inventoryDao.softDeleteInventory(id)
    }
}

