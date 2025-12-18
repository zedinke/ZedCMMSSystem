package com.artence.cmms.domain.usecase.machine

import com.artence.cmms.data.repository.MachineRepository
import javax.inject.Inject

class RefreshMachinesUseCase @Inject constructor(
    private val machineRepository: MachineRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return machineRepository.refreshMachines()
    }
}

