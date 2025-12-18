package com.artence.cmms.domain.usecase.worksheet

import com.artence.cmms.data.repository.WorksheetRepository
import com.artence.cmms.domain.model.Worksheet
import javax.inject.Inject

class GetWorksheetByIdUseCase @Inject constructor(
    private val worksheetRepository: WorksheetRepository
) {
    suspend operator fun invoke(id: Int): Worksheet? {
        return worksheetRepository.getWorksheetById(id)
    }
}

