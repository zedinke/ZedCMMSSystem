package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.AssetDao
import com.artence.cmms.data.remote.api.AssetApi
import com.artence.cmms.data.remote.dto.CreateAssetDto
import com.artence.cmms.data.remote.dto.UpdateAssetDto
import com.artence.cmms.domain.mapper.toDomain
import com.artence.cmms.domain.mapper.toEntity
import com.artence.cmms.domain.model.Asset
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AssetRepository @Inject constructor(
    private val assetApi: AssetApi,
    private val assetDao: AssetDao
) {

    fun getAssets(): Flow<List<Asset>> {
        return assetDao.getAllAssets().map { entities ->
            entities.map { it.toDomain() }
        }
    }

    suspend fun getAssetById(id: Int): Asset? {
        val entity = assetDao.getAssetById(id)
        return entity?.toDomain()
    }

    suspend fun refreshAssets(): Result<Unit> {
        return try {
            val response = assetApi.getAssets()
            if (response.isSuccessful && response.body() != null) {
                val listResponse = response.body()!!
                val assets = listResponse.items
                val entities = assets.map { it.toDomain().toEntity() }
                assetDao.deleteAllAssets()
                assetDao.insertAssets(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to fetch assets: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createAsset(asset: CreateAssetDto): Result<Asset> {
        return try {
            val response = assetApi.createAsset(asset)
            if (response.isSuccessful && response.body() != null) {
                val assetDto = response.body()!!
                val entity = assetDto.toDomain().toEntity()
                assetDao.insertAsset(entity)
                Result.success(entity.toDomain())
            } else {
                Result.failure(Exception("Failed to create asset: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateAsset(id: Int, asset: UpdateAssetDto): Result<Asset> {
        return try {
            val response = assetApi.updateAsset(id, asset)
            if (response.isSuccessful && response.body() != null) {
                val assetDto = response.body()!!
                val entity = assetDto.toDomain().toEntity()
                assetDao.updateAsset(entity)
                Result.success(entity.toDomain())
            } else {
                Result.failure(Exception("Failed to update asset: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteAsset(id: Int): Result<Unit> {
        return try {
            val response = assetApi.deleteAsset(id)
            if (response.isSuccessful) {
                val entity = assetDao.getAssetById(id)
                entity?.let { assetDao.deleteAsset(it) }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete asset: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
