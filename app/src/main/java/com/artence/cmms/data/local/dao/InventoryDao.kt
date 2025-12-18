package com.artence.cmms.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.artence.cmms.data.local.entity.InventoryEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface InventoryDao {
    @Query("SELECT * FROM inventory WHERE isDeleted = 0 ORDER BY name ASC")
    fun getAllInventory(): Flow<List<InventoryEntity>>

    @Query("SELECT * FROM inventory WHERE id = :id AND isDeleted = 0")
    suspend fun getInventoryById(id: String): InventoryEntity?

    @Query("SELECT * FROM inventory WHERE status = :status AND isDeleted = 0")
    fun getInventoryByStatus(status: String): Flow<List<InventoryEntity>>

    @Query("SELECT * FROM inventory WHERE quantity <= minQuantity AND isDeleted = 0")
    fun getLowStockItems(): Flow<List<InventoryEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertInventory(inventory: InventoryEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAllInventory(inventories: List<InventoryEntity>)

    @Update
    suspend fun updateInventory(inventory: InventoryEntity)

    @Delete
    suspend fun deleteInventory(inventory: InventoryEntity)

    @Query("UPDATE inventory SET isDeleted = 1 WHERE id = :id")
    suspend fun softDeleteInventory(id: String)

    @Query("DELETE FROM inventory")
    suspend fun clearAllInventory()
}

