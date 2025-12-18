package com.artence.cmms.data.repository

import com.artence.cmms.data.remote.api.ReportsApi
import com.artence.cmms.data.remote.dto.ReportsSummaryDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ReportsRepository @Inject constructor(
    private val reportsApi: ReportsApi
) {
    suspend fun getReportsSummary(): Result<ReportsSummaryDto> {
        return try {
            val response = reportsApi.getReportsSummary()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch reports summary: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

