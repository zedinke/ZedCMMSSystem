package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.ReportsSummaryDto
import retrofit2.Response
import retrofit2.http.GET

interface ReportsApi {
    @GET("reports/summary")
    suspend fun getReportsSummary(): Response<ReportsSummaryDto>
}

