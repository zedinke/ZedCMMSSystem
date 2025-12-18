package com.artence.cmms.util

import android.util.Log
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

object DiagnosticsUtil {
    private const val TAG = "DiagnosticsUtil"

    /**
     * Tesztel a szerver elérhetőségét egy egyszerű HTTP GET hívással
     */
    suspend fun testServerConnectivity(baseUrl: String = "http://116.203.226.140:8000"): String {
        return try {
            Log.d(TAG, "Testing connectivity to $baseUrl")
            val url = URL("$baseUrl/api/health/")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.connect()
            
            val responseCode = connection.responseCode
            val responseMessage = connection.responseMessage
            Log.d(TAG, "Health check response: $responseCode $responseMessage")
            
            if (responseCode == 200) {
                val input = BufferedReader(InputStreamReader(connection.inputStream))
                val response = input.readText()
                input.close()
                "Server OK: $response"
            } else {
                "Server responded with: $responseCode $responseMessage"
            }
        } catch (e: Exception) {
            val errorMsg = "Connectivity test failed: ${e.javaClass.simpleName}: ${e.message}"
            Log.e(TAG, errorMsg, e)
            errorMsg
        }
    }

    /**
     * Ellenőrzi az Internet kapcsolatot (DNS resolving)
     */
    suspend fun testDnsResolution(): String {
        return try {
            Log.d(TAG, "Testing DNS resolution for 116.203.226.140")
            val inetAddress = java.net.InetAddress.getByName("116.203.226.140")
            val result = "DNS OK: ${inetAddress.hostAddress}"
            Log.d(TAG, result)
            result
        } catch (e: Exception) {
            val errorMsg = "DNS resolution failed: ${e.message}"
            Log.e(TAG, errorMsg, e)
            errorMsg
        }
    }

    /**
     * Tesztel a login végpontot mock adatokkal
     */
    suspend fun testLoginEndpoint(baseUrl: String = "http://116.203.226.140:8000"): String {
        return try {
            Log.d(TAG, "Testing login endpoint")
            val url = URL("$baseUrl/api/v1/auth/login")
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.doOutput = true
            
            // Mock login request
            val mockRequest = """{"username":"test","password":"test"}"""
            connection.outputStream.write(mockRequest.toByteArray())
            
            val responseCode = connection.responseCode
            Log.d(TAG, "Login endpoint responded with: $responseCode")
            
            when (responseCode) {
                401 -> "Endpoint exists but credentials invalid (401) - this is expected for test credentials"
                422 -> "Endpoint exists but request format invalid (422)"
                200 -> "Login successful (200)"
                404 -> "Endpoint not found (404) - check the URL!"
                else -> "Endpoint responded: $responseCode"
            }
        } catch (e: Exception) {
            val errorMsg = "Login endpoint test failed: ${e.javaClass.simpleName}: ${e.message}"
            Log.e(TAG, errorMsg, e)
            errorMsg
        }
    }
}

