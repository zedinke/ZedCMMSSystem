package com.artence.cmms.data.local.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Int,
    val username: String,
    val email: String?,
    val fullName: String?,
    val phone: String?,
    val roleId: Int,
    val isActive: Boolean,
    val languagePreference: String,
    val createdAt: Long,
    val updatedAt: Long?
)
