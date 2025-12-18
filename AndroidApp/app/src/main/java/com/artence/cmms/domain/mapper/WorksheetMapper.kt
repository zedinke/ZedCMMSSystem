package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.database.entities.WorksheetEntity
import com.artence.cmms.data.remote.dto.WorksheetDto
import com.artence.cmms.domain.model.Worksheet
import com.artence.cmms.util.toTimestamp

object WorksheetMapper {

    fun fromEntity(entity: WorksheetEntity): Worksheet {
        return Worksheet(
            id = entity.id,
            machineId = entity.machineId,
            machineName = null,
            assignedToUserId = entity.assignedToUserId,
            assignedToUsername = null,
            title = entity.title,
            description = entity.description,
            status = entity.status,
            priority = entity.priority,
            workType = null,
            estimatedTime = null,
            actualTime = null,
            notes = null,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt,
            completedAt = null
        )
    }

    fun toEntity(worksheet: Worksheet): WorksheetEntity {
        return WorksheetEntity(
            id = worksheet.id,
            machineId = worksheet.machineId,
            assignedToUserId = worksheet.assignedToUserId,
            title = worksheet.title,
            description = worksheet.description,
            status = worksheet.status,
            priority = worksheet.priority,
            createdAt = worksheet.createdAt,
            updatedAt = worksheet.updatedAt
        )
    }

    fun fromDto(dto: WorksheetDto): Worksheet {
        return Worksheet(
            id = dto.id,
            machineId = dto.machineId,
            machineName = null,
            assignedToUserId = dto.assignedToUserId,
            assignedToUsername = null,
            title = dto.maintenanceType,
            description = dto.description,
            status = dto.status,
            priority = null,
            workType = dto.maintenanceType,
            estimatedTime = null,
            actualTime = null,
            notes = null,
            createdAt = dto.createdAt.toTimestamp(),
            updatedAt = dto.updatedAt?.toTimestamp(),
            completedAt = dto.completedAt?.toTimestamp()
        )
    }

    fun dtoToEntity(dto: WorksheetDto): WorksheetEntity {
        return WorksheetEntity(
            id = dto.id,
            machineId = dto.machineId,
            assignedToUserId = dto.assignedToUserId,
            title = dto.maintenanceType,
            description = dto.description,
            status = dto.status,
            priority = null,
            createdAt = dto.createdAt.toTimestamp(),
            updatedAt = dto.updatedAt?.toTimestamp()
        )
    }
}
