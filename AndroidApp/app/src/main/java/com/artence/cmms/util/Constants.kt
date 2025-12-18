package com.artence.cmms.util

object Constants {
    // PRODUCTION: Élő backend szerver és MySQL adatbázis
    const val BASE_URL = "http://116.203.226.140:8000/api/"
    const val TIMEOUT_SECONDS = 30L

    // Room
    const val DATABASE_NAME = "cmms_db"

    // DataStore
    const val PREFERENCES_NAME = "cmms_prefs"
    const val KEY_ACCESS_TOKEN = "access_token"
    const val KEY_USER_ID = "user_id"
    const val KEY_USERNAME = "username"
    const val KEY_ROLE = "role"
    const val KEY_LANGUAGE = "language"

    // Languages
    const val LANGUAGE_EN = "en"
    const val LANGUAGE_HU = "hu"

    // Machine statuses
    const val MACHINE_STATUS_OPERATIONAL = "OPERATIONAL"
    const val MACHINE_STATUS_MAINTENANCE = "MAINTENANCE"
    const val MACHINE_STATUS_BREAKDOWN = "BREAKDOWN"
    const val MACHINE_STATUS_OFFLINE = "OFFLINE"

    // Worksheet statuses
    const val WORKSHEET_STATUS_PENDING = "PENDING"
    const val WORKSHEET_STATUS_IN_PROGRESS = "IN_PROGRESS"
    const val WORKSHEET_STATUS_COMPLETED = "COMPLETED"
    const val WORKSHEET_STATUS_CANCELLED = "CANCELLED"

    // Priorities
    const val PRIORITY_LOW = "LOW"
    const val PRIORITY_MEDIUM = "MEDIUM"
    const val PRIORITY_HIGH = "HIGH"
    const val PRIORITY_URGENT = "URGENT"
}

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}
