package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.MachineDao
import com.artence.cmms.data.remote.api.MachineApi
import com.artence.cmms.data.remote.dto.CreateMachineDto
import com.artence.cmms.data.remote.dto.UpdateMachineDto
import com.artence.cmms.domain.mapper.MachineMapper
import com.artence.cmms.domain.model.Machine
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class MachineRepository @Inject constructor(
    private val machineDao: MachineDao,
    private val machineApi: MachineApi
) {

    fun getMachines(): Flow<List<Machine>> {
        return machineDao.getAllMachines().map { entities ->
            entities.map { MachineMapper.fromEntity(it) }
        }
    }

    suspend fun getMachineById(id: Int): Machine? {
        val entity = machineDao.getMachineById(id)
        return entity?.let { MachineMapper.fromEntity(it) }
    }

    suspend fun refreshMachines(): Result<Unit> {
        return try {
            val response = machineApi.getMachines()
            if (response.isSuccessful && response.body() != null) {
                val listResponse = response.body()!!
                val machines = listResponse.items
                val entities = machines.map { MachineMapper.dtoToEntity(it) }
                machineDao.deleteAllMachines()
                machineDao.insertMachines(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to fetch machines: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createMachine(machine: CreateMachineDto): Result<Machine> {
        return try {
            val response = machineApi.createMachine(machine)
            if (response.isSuccessful && response.body() != null) {
                val machineDto = response.body()!!
                val entity = MachineMapper.dtoToEntity(machineDto)
                machineDao.insertMachine(entity)
                Result.success(MachineMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to create machine: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateMachine(id: Int, machine: UpdateMachineDto): Result<Machine> {
        return try {
            val response = machineApi.updateMachine(id, machine)
            if (response.isSuccessful && response.body() != null) {
                val machineDto = response.body()!!
                val entity = MachineMapper.dtoToEntity(machineDto)
                machineDao.updateMachine(entity)
                Result.success(MachineMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed to update machine: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteMachine(id: Int): Result<Unit> {
        return try {
            val response = machineApi.deleteMachine(id)
            if (response.isSuccessful) {
                val entity = machineDao.getMachineById(id)
                entity?.let { machineDao.deleteMachine(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete machine: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
