package com.artence.cmms.domain.usecase.machine

import com.artence.cmms.data.repository.MachineRepository
import com.artence.cmms.domain.model.Machine
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetMachinesUseCase @Inject constructor(
    private val machineRepository: MachineRepository
) {
    operator fun invoke(): Flow<List<Machine>> {
        return machineRepository.getMachines()
    }
}

