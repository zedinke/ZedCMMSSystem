package com.artence.cmms.domain.usecase.worksheet

import com.artence.cmms.data.repository.WorksheetRepository
import javax.inject.Inject

class RefreshWorksheetsUseCase @Inject constructor(
    private val worksheetRepository: WorksheetRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return worksheetRepository.refreshWorksheets()
    }
}

