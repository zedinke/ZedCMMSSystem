package com.artence.cmms.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.artence.cmms.data.local.database.dao.AssetDao
import com.artence.cmms.data.local.database.dao.InventoryDao
import com.artence.cmms.data.local.database.dao.MachineDao
import com.artence.cmms.data.local.database.dao.PMTaskDao
import com.artence.cmms.data.local.database.dao.UserDao
import com.artence.cmms.data.local.database.dao.WorksheetDao
import com.artence.cmms.data.local.database.entities.AssetEntity
import com.artence.cmms.data.local.database.entities.InventoryEntity
import com.artence.cmms.data.local.database.entities.MachineEntity
import com.artence.cmms.data.local.database.entities.PMTaskEntity
import com.artence.cmms.data.local.database.entities.UserEntity
import com.artence.cmms.data.local.database.entities.WorksheetEntity

@Database(
    entities = [
        UserEntity::class,
        MachineEntity::class,
        WorksheetEntity::class,
        AssetEntity::class,
        InventoryEntity::class,
        PMTaskEntity::class,
    ],
    version = 1,
    exportSchema = false
)
abstract class CMMSDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun machineDao(): MachineDao
    abstract fun worksheetDao(): WorksheetDao
    abstract fun assetDao(): AssetDao
    abstract fun inventoryDao(): InventoryDao
    abstract fun pmTaskDao(): PMTaskDao
}
