package com.artence.cmms.domain.mapper

import com.artence.cmms.data.local.database.entities.MachineEntity
import com.artence.cmms.data.remote.dto.MachineDto
import com.artence.cmms.domain.model.Machine
import com.artence.cmms.util.toTimestamp

object MachineMapper {

    fun fromEntity(entity: MachineEntity): Machine {
        return Machine(
            id = entity.id,
            productionLineId = entity.productionLineId,
            productionLineName = null, // Not stored in entity
            name = entity.name,
            serialNumber = entity.serialNumber,
            model = entity.model,
            manufacturer = entity.manufacturer,
            status = entity.status,
            assetTag = entity.assetTag,
            description = null,
            installDate = null,
            createdAt = entity.createdAt,
            updatedAt = entity.updatedAt
        )
    }

    fun toEntity(machine: Machine): MachineEntity {
        return MachineEntity(
            id = machine.id,
            productionLineId = machine.productionLineId,
            name = machine.name,
            serialNumber = machine.serialNumber,
            model = machine.model,
            manufacturer = machine.manufacturer,
            status = machine.status,
            assetTag = machine.assetTag,
            createdAt = machine.createdAt,
            updatedAt = machine.updatedAt
        )
    }

    fun fromDto(dto: MachineDto): Machine {
        return Machine(
            id = dto.id,
            productionLineId = dto.productionLineId ?: 0,
            productionLineName = null,
            name = dto.name,
            serialNumber = dto.serialNumber,
            model = dto.model,
            manufacturer = null,
            status = dto.status,
            assetTag = null,
            description = null,
            installDate = null,
            createdAt = dto.createdAt.toTimestamp(),
            updatedAt = dto.updatedAt?.toTimestamp()
        )
    }

    fun dtoToEntity(dto: MachineDto): MachineEntity {
        return MachineEntity(
            id = dto.id,
            productionLineId = dto.productionLineId ?: 0,
            name = dto.name,
            serialNumber = dto.serialNumber,
            model = dto.model,
            manufacturer = null,
            status = dto.status,
            assetTag = null,
            createdAt = dto.createdAt.toTimestamp(),
            updatedAt = dto.updatedAt?.toTimestamp()
        )
    }
}

