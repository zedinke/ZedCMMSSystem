package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.WorksheetDao
import com.artence.cmms.data.remote.api.WorksheetApi
import com.artence.cmms.data.remote.dto.CreateWorksheetDto
import com.artence.cmms.data.remote.dto.UpdateWorksheetDto
import com.artence.cmms.domain.mapper.WorksheetMapper
import com.artence.cmms.domain.model.Worksheet
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WorksheetRepository @Inject constructor(
    private val worksheetApi: WorksheetApi,
    private val worksheetDao: WorksheetDao
) {

    fun getWorksheets(): Flow<List<Worksheet>> {
        return worksheetDao.getAllWorksheets().map { entities ->
            entities.map { WorksheetMapper.fromEntity(it) }
        }
    }

    suspend fun getWorksheetById(id: Int): Worksheet? {
        val entity = worksheetDao.getWorksheetById(id)
        return entity?.let { WorksheetMapper.fromEntity(it) }
    }

    suspend fun refreshWorksheets(): Result<Unit> {
        return try {
            val response = worksheetApi.getWorksheets()
            if (response.isSuccessful && response.body() != null) {
                val listResponse = response.body()!!
                val worksheets = listResponse.items
                val entities = worksheets.map { WorksheetMapper.dtoToEntity(it) }
                worksheetDao.deleteAllWorksheets()
                worksheetDao.insertWorksheets(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to fetch worksheets: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createWorksheet(worksheet: CreateWorksheetDto): Result<Worksheet> {
        return try {
            val response = worksheetApi.createWorksheet(worksheet)
            if (response.isSuccessful && response.body() != null) {
                val worksheetDto = response.body()!!
                val entity = WorksheetMapper.dtoToEntity(worksheetDto)
                worksheetDao.insertWorksheet(entity)
                Result.success(WorksheetMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to create worksheet: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateWorksheet(id: Int, worksheet: UpdateWorksheetDto): Result<Worksheet> {
        return try {
            val response = worksheetApi.updateWorksheet(id, worksheet)
            if (response.isSuccessful && response.body() != null) {
                val worksheetDto = response.body()!!
                val entity = WorksheetMapper.dtoToEntity(worksheetDto)
                worksheetDao.updateWorksheet(entity)
                Result.success(WorksheetMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to update worksheet: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteWorksheet(id: Int): Result<Unit> {
        return try {
            val response = worksheetApi.deleteWorksheet(id)
            if (response.isSuccessful) {
                val entity = worksheetDao.getWorksheetById(id)
                entity?.let { worksheetDao.deleteWorksheet(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete worksheet: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

