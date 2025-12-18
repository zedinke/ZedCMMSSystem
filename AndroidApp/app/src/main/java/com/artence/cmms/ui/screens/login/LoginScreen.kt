package com.artence.cmms.ui.screens.login

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.artence.cmms.util.DiagnosticsUtil

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    viewModel: LoginViewModel = hiltViewModel(),
    onLoginSuccess: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var showDiagnosticsDialog by remember { mutableStateOf(false) }
    var diagnosticsResult by remember { mutableStateOf("") }
    var diagnosticsLoading by remember { mutableStateOf(false) }

    // Navigate on success
    LaunchedEffect(uiState.isSuccess) {
        if (uiState.isSuccess) {
            onLoginSuccess()
        }
    }

    // Show error snackbar
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(error)
            viewModel.clearError()
        }
    }

    if (showDiagnosticsDialog) {
        DiagnosticsDialog(
            result = diagnosticsResult,
            isLoading = diagnosticsLoading,
            onDismiss = { showDiagnosticsDialog = false }
        )
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // Logo or App name
            Text(
                text = "CMMS",
                style = MaterialTheme.typography.displayLarge,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(48.dp))

            // Username field
            OutlinedTextField(
                value = username,
                onValueChange = { username = it },
                label = { Text("Username") },
                leadingIcon = {
                    Icon(Icons.Default.Person, contentDescription = "Username")
                },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                enabled = !uiState.isLoading
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Password field
            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("Password") },
                leadingIcon = {
                    Icon(Icons.Default.Lock, contentDescription = "Password")
                },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                enabled = !uiState.isLoading
            )

            Spacer(modifier = Modifier.height(32.dp))

            // Login button
            Button(
                onClick = {
                    if (username.isNotBlank() && password.isNotBlank()) {
                        viewModel.login(username, password)
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isLoading && username.isNotBlank() && password.isNotBlank()
            ) {
                if (uiState.isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Login")
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Test Server button
            OutlinedButton(
                onClick = {
                    showDiagnosticsDialog = true
                    diagnosticsLoading = true
                    diagnosticsResult = "Running diagnostics..."
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isLoading && !diagnosticsLoading
            ) {
                Text("Test Server")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Version info
            Text(
                text = "Version 1.0.0",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun DiagnosticsDialog(
    result: String,
    isLoading: Boolean,
    onDismiss: () -> Unit
) {
    var diagnosticsText by remember { mutableStateOf(result) }

    LaunchedEffect(isLoading) {
        if (isLoading && result.contains("Running")) {
            val results = buildString {
                appendLine("=== SERVER DIAGNOSTICS ===")
                appendLine()
                appendLine("DNS Resolution:")
                try {
                    appendLine(DiagnosticsUtil.testDnsResolution())
                } catch (e: Exception) {
                    appendLine("Error: ${e.message}")
                }
                appendLine()
                appendLine("Server Connectivity:")
                try {
                    appendLine(DiagnosticsUtil.testServerConnectivity())
                } catch (e: Exception) {
                    appendLine("Error: ${e.message}")
                }
                appendLine()
                appendLine("Login Endpoint:")
                try {
                    appendLine(DiagnosticsUtil.testLoginEndpoint())
                } catch (e: Exception) {
                    appendLine("Error: ${e.message}")
                }
            }
            diagnosticsText = results
        }
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Server Diagnostics") },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .verticalScroll(rememberScrollState())
            ) {
                if (isLoading && result.contains("Running")) {
                    CircularProgressIndicator()
                } else {
                    Text(diagnosticsText, style = MaterialTheme.typography.bodySmall)
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Close")
            }
        }
    )
}


