package com.artence.cmms.domain.model

data class User(
    val id: Int,
    val username: String,
    val email: String?,
    val fullName: String?,
    val phone: String?,
    val roleId: Int,
    val roleName: String?,
    val isActive: Boolean,
    val languagePreference: String,
    val createdAt: Long,
    val updatedAt: Long?
)

