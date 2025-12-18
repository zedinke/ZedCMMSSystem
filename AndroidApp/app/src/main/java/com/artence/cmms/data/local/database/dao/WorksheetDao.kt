package com.artence.cmms.data.local.database.dao

import androidx.room.*
import com.artence.cmms.data.local.database.entities.WorksheetEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface WorksheetDao {
    @Query("SELECT * FROM worksheets")
    fun getAllWorksheets(): Flow<List<WorksheetEntity>>

    @Query("SELECT * FROM worksheets WHERE id = :id")
    suspend fun getWorksheetById(id: Int): WorksheetEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWorksheet(worksheet: WorksheetEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertWorksheets(worksheets: List<WorksheetEntity>)

    @Update
    suspend fun updateWorksheet(worksheet: WorksheetEntity)

    @Delete
    suspend fun deleteWorksheet(worksheet: WorksheetEntity)

    @Query("DELETE FROM worksheets")
    suspend fun deleteAllWorksheets()
}
