package com.artence.cmms.domain.usecase.machine

import com.artence.cmms.data.repository.MachineRepository
import com.artence.cmms.domain.model.Machine
import javax.inject.Inject

class GetMachineByIdUseCase @Inject constructor(
    private val machineRepository: MachineRepository
) {
    suspend operator fun invoke(id: Int): Machine? {
        return machineRepository.getMachineById(id)
    }
}

