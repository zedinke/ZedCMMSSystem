package com.artence.cmms.data.repository

import com.artence.cmms.data.local.database.dao.UserDao
import com.artence.cmms.data.remote.api.UserApi
import com.artence.cmms.data.remote.dto.CreateUserDto
import com.artence.cmms.data.remote.dto.UpdateUserDto
import com.artence.cmms.data.remote.dto.UserDto
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class UserRepository @Inject constructor(
    private val userDao: UserDao,
    private val userApi: UserApi
) {
    suspend fun getUsers(
        skip: Int = 0,
        limit: Int = 100,
        roleName: String? = null,
        status: String? = null
    ): Result<Pair<Int, List<UserDto>>> {
        return try {
            val response = userApi.getUsers(skip, limit, roleName, status)
            if (response.isSuccessful && response.body() != null) {
                val listResponse = response.body()!!
                Result.success(Pair(listResponse.total, listResponse.items))
            } else {
                Result.failure(Exception("Failed to fetch users: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getUserById(id: Int): Result<UserDto> {
        return try {
            val response = userApi.getUserById(id)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to fetch user: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun createUser(user: CreateUserDto): Result<UserDto> {
        return try {
            val response = userApi.createUser(user)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to create user: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateUser(id: Int, user: UpdateUserDto): Result<UserDto> {
        return try {
            val response = userApi.updateUser(id, user)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to update user: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteUser(id: Int): Result<Unit> {
        return try {
            val response = userApi.deleteUser(id)
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to delete user: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun resetPassword(id: Int): Result<UserDto> {
        return try {
            val response = userApi.resetPassword(id)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Failed to reset password: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
