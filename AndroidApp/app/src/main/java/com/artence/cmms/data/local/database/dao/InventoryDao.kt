package com.artence.cmms.data.local.database.dao

import androidx.room.*
import com.artence.cmms.data.local.database.entities.InventoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface InventoryDao {
    @Query("SELECT * FROM inventory")
    fun getAllInventory(): Flow<List<InventoryEntity>>

    @Query("SELECT * FROM inventory WHERE id = :id")
    suspend fun getInventoryById(id: Int): InventoryEntity?

    @Query("SELECT * FROM inventory WHERE assetId = :assetId")
    fun getInventoryByAssetId(assetId: Int): Flow<InventoryEntity?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertInventory(inventory: InventoryEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertInventoryList(inventoryList: List<InventoryEntity>)

    @Update
    suspend fun updateInventory(inventory: InventoryEntity)

    @Delete
    suspend fun deleteInventory(inventory: InventoryEntity)

    @Query("DELETE FROM inventory")
    suspend fun deleteAllInventory()
}

