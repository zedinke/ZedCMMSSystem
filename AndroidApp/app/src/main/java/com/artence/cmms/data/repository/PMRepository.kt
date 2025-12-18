package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.PMTaskDao
import com.artence.cmms.data.remote.api.PMApi
import com.artence.cmms.data.remote.dto.pm.CreatePMTaskDto
import com.artence.cmms.data.remote.dto.pm.ExecutePMTaskDto
import com.artence.cmms.data.remote.dto.pm.UpdatePMTaskDto
import com.artence.cmms.domain.mapper.PMTaskMapper
import com.artence.cmms.domain.model.PMTask
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PMRepository @Inject constructor(
    private val pmApi: PMApi,
    private val pmTaskDao: PMTaskDao
) {

    fun getPMTasks(): Flow<List<PMTask>> {
        return pmTaskDao.getAllPMTasks().map { entities ->
            entities.map { PMTaskMapper.fromEntity(it) }
        }
    }

    fun getPMTasksByStatus(status: String): Flow<List<PMTask>> {
        return pmTaskDao.getPMTasksByStatus(status).map { entities ->
            entities.map { PMTaskMapper.fromEntity(it) }
        }
    }

    fun getPMTasksByMachine(machineId: Int): Flow<List<PMTask>> {
        return pmTaskDao.getPMTasksByMachine(machineId).map { entities ->
            entities.map { PMTaskMapper.fromEntity(it) }
        }
    }

    suspend fun getPMTaskById(id: Int): PMTask? {
        val entity = pmTaskDao.getPMTaskById(id)
        return entity?.let { PMTaskMapper.fromEntity(it) }
    }

    fun getUpcomingPMTasks(limit: Int = 10): Flow<List<PMTask>> {
        return pmTaskDao.getUpcomingPMTasks(limit).map { entities ->
            entities.map { PMTaskMapper.fromEntity(it) }
        }
    }

    fun getOverdueTaskCount(): Flow<Int> {
        return pmTaskDao.getOverdueTaskCount()
    }

    suspend fun refreshPMTasks(): Result<Unit> {
        return try {
            val response = pmApi.getPMTasks()
            if (response.isSuccessful && response.body() != null) {
                val tasks = response.body()!!
                val entities = tasks.map { PMTaskMapper.dtoToEntity(it) }
                pmTaskDao.deleteAllPMTasks()
                pmTaskDao.insertPMTasks(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to fetch PM tasks: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createPMTask(task: CreatePMTaskDto): Result<PMTask> {
        return try {
            val response = pmApi.createPMTask(task)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val entity = PMTaskMapper.dtoToEntity(dto)
                pmTaskDao.insertPMTask(entity)
                Result.success(PMTaskMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to create PM task: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updatePMTask(id: Int, task: UpdatePMTaskDto): Result<PMTask> {
        return try {
            val response = pmApi.updatePMTask(id, task)  // API-ban taskId, de itt id marad
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val entity = PMTaskMapper.dtoToEntity(dto)
                pmTaskDao.updatePMTask(entity)
                Result.success(PMTaskMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to update PM task: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun executePMTask(id: Int, data: ExecutePMTaskDto): Result<PMTask> {
        return try {
            val response = pmApi.executePMTask(id, data)
            if (response.isSuccessful && response.body() != null) {
                val dto = response.body()!!
                val entity = PMTaskMapper.dtoToEntity(dto)
                pmTaskDao.updatePMTask(entity)
                Result.success(PMTaskMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to execute PM task: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deletePMTask(id: Int): Result<Unit> {
        return try {
            val response = pmApi.deletePMTask(id)
            if (response.isSuccessful) {
                val entity = pmTaskDao.getPMTaskById(id)
                entity?.let { pmTaskDao.deletePMTask(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete PM task: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

