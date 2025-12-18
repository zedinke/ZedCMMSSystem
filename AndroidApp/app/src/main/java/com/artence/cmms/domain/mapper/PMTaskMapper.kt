package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.database.entities.PMTaskEntity
import com.artence.cmms.data.remote.dto.pm.PMTaskDto
import com.artence.cmms.domain.model.PMTask

object PMTaskMapper {
    fun fromEntity(entity: PMTaskEntity): PMTask {
        return PMTask(
            id = entity.id,
            machineId = entity.machineId,
            machineName = entity.machineName,
            taskName = entity.taskName,
            description = entity.description,
            frequency = entity.frequency,
            lastExecuted = entity.lastExecuted,
            nextScheduled = entity.nextScheduled,
            status = entity.status,
            assignedToUserId = entity.assignedToUserId,
            assignedToUsername = entity.assignedToUsername,
            priority = entity.priority,
            estimatedDuration = entity.estimatedDuration,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt
        )
    }

    fun toEntity(domain: PMTask): PMTaskEntity {
        return PMTaskEntity(
            id = domain.id,
            machineId = domain.machineId,
            machineName = domain.machineName,
            taskName = domain.taskName,
            description = domain.description,
            frequency = domain.frequency,
            lastExecuted = domain.lastExecuted,
            nextScheduled = domain.nextScheduled,
            status = domain.status,
            assignedToUserId = domain.assignedToUserId,
            assignedToUsername = domain.assignedToUsername,
            priority = domain.priority,
            estimatedDuration = domain.estimatedDuration,
            createdAt = domain.createdAt,
            updatedAt = domain.updatedAt
        )
    }

    fun dtoToEntity(dto: PMTaskDto): PMTaskEntity {
        return PMTaskEntity(
            id = dto.id,
            machineId = dto.machineId,
            machineName = dto.machineName,
            taskName = dto.taskName,
            description = dto.description,
            frequency = dto.frequency,
            lastExecuted = dto.lastExecuted,
            nextScheduled = dto.nextScheduled,
            status = dto.status,
            assignedToUserId = dto.assignedToUserId,
            assignedToUsername = dto.assignedToUsername,
            priority = dto.priority,
            estimatedDuration = dto.estimatedDuration,
            createdAt = dto.createdAt,
            updatedAt = dto.updatedAt
        )
    }

    fun fromDto(dto: PMTaskDto): PMTask {
        return fromEntity(dtoToEntity(dto))
    }
}

