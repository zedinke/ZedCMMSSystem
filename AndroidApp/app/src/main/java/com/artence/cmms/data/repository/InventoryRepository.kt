package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.InventoryDao
import com.artence.cmms.data.remote.api.InventoryApi
import com.artence.cmms.data.remote.dto.CreateInventoryDto
import com.artence.cmms.data.remote.dto.UpdateInventoryDto
import com.artence.cmms.domain.mapper.InventoryMapper
import com.artence.cmms.domain.model.Inventory
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class InventoryRepository @Inject constructor(
    private val inventoryDao: InventoryDao,
    private val inventoryApi: InventoryApi
) {

    fun getInventory(): Flow<List<Inventory>> {
        return inventoryDao.getAllInventory().map { entities ->
            entities.map { InventoryMapper.fromEntity(it) }
        }
    }

    suspend fun getInventoryById(id: Int): Inventory? {
        val entity = inventoryDao.getInventoryById(id)
        return entity?.let { InventoryMapper.fromEntity(it) }
    }

    fun getInventoryByAssetId(assetId: Int): Flow<Inventory?> {
        return inventoryDao.getInventoryByAssetId(assetId).map { entity ->
            entity?.let { InventoryMapper.fromEntity(it) }
        }
    }

    suspend fun refreshInventory(): Result<Unit> {
        return try {
            val response = inventoryApi.getInventory()
            if (response.isSuccessful && response.body() != null) {
                val listResponse = response.body()!!
                val inventory = listResponse.items
                val entities = inventory.map { InventoryMapper.dtoToEntity(it) }
                inventoryDao.deleteAllInventory()
                inventoryDao.insertInventoryList(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to fetch inventory: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createInventory(inventory: CreateInventoryDto): Result<Inventory> {
        return try {
            val response = inventoryApi.createInventory(inventory)
            if (response.isSuccessful && response.body() != null) {
                val inventoryDto = response.body()!!
                val entity = InventoryMapper.dtoToEntity(inventoryDto)
                inventoryDao.insertInventory(entity)
                Result.success(InventoryMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to create inventory: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateInventory(id: Int, inventory: UpdateInventoryDto): Result<Inventory> {
        return try {
            val response = inventoryApi.updateInventory(id, inventory)
            if (response.isSuccessful && response.body() != null) {
                val inventoryDto = response.body()!!
                val entity = InventoryMapper.dtoToEntity(inventoryDto)
                inventoryDao.updateInventory(entity)
                Result.success(InventoryMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to update inventory: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteInventory(id: Int): Result<Unit> {
        return try {
            val response = inventoryApi.deleteInventory(id)
            if (response.isSuccessful) {
                val entity = inventoryDao.getInventoryById(id)
                entity?.let { inventoryDao.deleteInventory(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete inventory: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

