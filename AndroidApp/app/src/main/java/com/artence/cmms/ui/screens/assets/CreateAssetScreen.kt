package com.artence.cmms.ui.screens.assets

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.artence.cmms.data.remote.dto.CreateAssetDto
import com.artence.cmms.ui.screens.assets.create.CreateAssetViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateAssetScreen(
    navController: NavController,
    viewModel: CreateAssetViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    // Show error snackbar
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(error)
            viewModel.clearError()
        }
    }

    // On success, navigate back
    LaunchedEffect(uiState.isSuccess) {
        if (uiState.isSuccess) {
            snackbarHostState.showSnackbar("Asset created successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Create New Asset") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        CreateAssetForm(
            isLoading = uiState.isLoading,
            onCreateAsset = { name, serialNumber, model, manufacturer ->
                viewModel.createAsset(
                    name = name,
                    serialNumber = serialNumber,
                    model = model,
                    manufacturer = manufacturer,
                    status = "Operational"
                )
            },
            onCancel = { navController.navigateUp() },
            modifier = Modifier.padding(paddingValues)
        )
    }
}

@Composable
private fun CreateAssetForm(
    isLoading: Boolean,
    onCreateAsset: (String, String?, String?, String?) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var name by remember { mutableStateOf("") }
    var serialNumber by remember { mutableStateOf("") }
    var model by remember { mutableStateOf("") }
    var manufacturer by remember { mutableStateOf("") }
    var nameError by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(
                "Asset Details",
                style = MaterialTheme.typography.titleMedium
            )
        }

        item {
            OutlinedTextField(
                value = name,
                onValueChange = {
                    name = it
                    nameError = false
                },
                label = { Text("Asset Name *") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                isError = nameError,
                supportingText = {
                    if (nameError) Text("Name is required", color = MaterialTheme.colorScheme.error)
                }
            )
        }

        item {
            OutlinedTextField(
                value = serialNumber,
                onValueChange = { serialNumber = it },
                label = { Text("Serial Number") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            )
        }

        item {
            OutlinedTextField(
                value = model,
                onValueChange = { model = it },
                label = { Text("Model") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            )
        }

        item {
            OutlinedTextField(
                value = manufacturer,
                onValueChange = { manufacturer = it },
                label = { Text("Manufacturer") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            )
        }

        item {
            Text(
                "Status: Operational (default)",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        item {
            Spacer(modifier = Modifier.height(16.dp))
        }

        item {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = { onCancel() },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading
                ) {
                    Text("Cancel")
                }
                Button(
                    onClick = {
                        if (name.isBlank()) {
                            nameError = true
                        } else {
                            onCreateAsset(
                                name,
                                serialNumber.ifEmpty { null },
                                model.ifEmpty { null },
                                manufacturer.ifEmpty { null }
                            )
                        }
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && name.isNotEmpty()
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("Create Asset")
                    }
                }
            }
        }
    }
}
