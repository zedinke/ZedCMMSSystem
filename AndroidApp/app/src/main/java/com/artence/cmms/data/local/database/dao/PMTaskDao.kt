package com.artence.cmms.data.local.database.dao

import androidx.room.*
import com.artence.cmms.data.local.database.entities.PMTaskEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface PMTaskDao {
    @Query("SELECT * FROM pm_tasks ORDER BY nextScheduled ASC")
    fun getAllPMTasks(): Flow<List<PMTaskEntity>>

    @Query("SELECT * FROM pm_tasks WHERE status = :status ORDER BY nextScheduled ASC")
    fun getPMTasksByStatus(status: String): Flow<List<PMTaskEntity>>

    @Query("SELECT * FROM pm_tasks WHERE machineId = :machineId ORDER BY nextScheduled ASC")
    fun getPMTasksByMachine(machineId: Int): Flow<List<PMTaskEntity>>

    @Query("SELECT * FROM pm_tasks WHERE id = :id")
    suspend fun getPMTaskById(id: Int): PMTaskEntity?

    @Query("SELECT * FROM pm_tasks WHERE status IN ('Overdue', 'Scheduled') ORDER BY nextScheduled ASC LIMIT :limit")
    fun getUpcomingPMTasks(limit: Int = 10): Flow<List<PMTaskEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPMTask(task: PMTaskEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPMTasks(tasks: List<PMTaskEntity>)

    @Update
    suspend fun updatePMTask(task: PMTaskEntity)

    @Delete
    suspend fun deletePMTask(task: PMTaskEntity)

    @Query("DELETE FROM pm_tasks")
    suspend fun deleteAllPMTasks()

    @Query("SELECT COUNT(*) FROM pm_tasks WHERE status = 'Overdue'")
    fun getOverdueTaskCount(): Flow<Int>
}

