package com.artence.cmms.data.remote.dto

import com.google.gson.annotations.SerializedName

data class RoleDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String?
)

data class UserDto(
    @SerializedName("id") val id: Int,
    @SerializedName("username") val username: String,
    @SerializedName("email") val email: String,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String?,
    @SerializedName("must_change_password") val mustChangePassword: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String?,
    @SerializedName("role") val role: RoleDto?
)

data class CreateUserDto(
    @SerializedName("username") val username: String,
    @SerializedName("email") val email: String,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String?,
    @SerializedName("role_id") val roleId: Int
)

data class UpdateUserDto(
    @SerializedName("username") val username: String?,
    @SerializedName("email") val email: String?,
    @SerializedName("full_name") val fullName: String?,
    @SerializedName("phone") val phone: String?,
    @SerializedName("role_id") val roleId: Int?
)

