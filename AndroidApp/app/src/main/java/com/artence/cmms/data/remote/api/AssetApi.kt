package com.artence.cmms.data.remote.api

import com.artence.cmms.data.remote.dto.AssetDto
import com.artence.cmms.data.remote.dto.CreateAssetDto
import com.artence.cmms.data.remote.dto.ListResponse
import com.artence.cmms.data.remote.dto.UpdateAssetDto
import retrofit2.Response
import retrofit2.http.*

/**
 * AssetApi - Backend támogatás hozzáadva
 * 
 * A szerveren most már van /api/assets router (szinkronizálva a lokális verzióval).
 */
interface AssetApi {
    // NOTE: Ezek a végpontok NEM működnek, mert nincs /api/v1/assets a szerveren
    @GET("assets")
    suspend fun getAssets(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100,
        @Query("status") status: String? = null
    ): Response<ListResponse<AssetDto>>

    @GET("assets/{id}")
    suspend fun getAssetById(@Path("id") id: Int): Response<AssetDto>

    @POST("assets")
    suspend fun createAsset(@Body asset: CreateAssetDto): Response<AssetDto>

    @PUT("assets/{id}")
    suspend fun updateAsset(
        @Path("id") id: Int,
        @Body asset: UpdateAssetDto
    ): Response<AssetDto>

    @DELETE("assets/{id}")
    suspend fun deleteAsset(@Path("id") id: Int): Response<Unit>
}

