package com.artence.cmms.ui.screens.inventory

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.artence.cmms.ui.screens.inventory.create.CreateInventoryViewModel
import androidx.compose.foundation.text.KeyboardOptions

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateInventoryScreen(
    navController: NavController,
    viewModel: CreateInventoryViewModel = hiltViewModel()
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
            snackbarHostState.showSnackbar("Inventory item created successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Create New Inventory Item") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        CreateInventoryForm(
            isLoading = uiState.isLoading,
            onCreateInventory = { name, quantity, minQuantity, maxQuantity, location ->
                viewModel.createInventory(
                    name = name,
                    quantity = quantity,
                    minQuantity = minQuantity,
                    maxQuantity = maxQuantity,
                    location = location
                )
            },
            onCancel = { navController.navigateUp() },
            modifier = Modifier.padding(paddingValues)
        )
    }
}

@Composable
private fun CreateInventoryForm(
    isLoading: Boolean,
    onCreateInventory: (String, Int, Int, Int, String?) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var name by remember { mutableStateOf("") }
    var quantity by remember { mutableStateOf("") }
    var minQuantity by remember { mutableStateOf("") }
    var maxQuantity by remember { mutableStateOf("") }
    var location by remember { mutableStateOf("") }
    var nameError by remember { mutableStateOf(false) }
    var quantityError by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(
                "Stock Information",
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
                label = { Text("Name *") },
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
                value = quantity,
                onValueChange = {
                    quantity = it
                    quantityError = false
                },
                label = { Text("Current Quantity *") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                isError = quantityError,
                supportingText = {
                    if (quantityError) Text("Quantity is required", color = MaterialTheme.colorScheme.error)
                }
            )
        }

        item {
            OutlinedTextField(
                value = minQuantity,
                onValueChange = { minQuantity = it },
                label = { Text("Minimum Quantity *") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }

        item {
            OutlinedTextField(
                value = maxQuantity,
                onValueChange = { maxQuantity = it },
                label = { Text("Maximum Quantity *") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }

        item {
            OutlinedTextField(
                value = location,
                onValueChange = { location = it },
                label = { Text("Location") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
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
                        }
                        if (quantity.isBlank() || minQuantity.isBlank() || maxQuantity.isBlank()) {
                            quantityError = true
                        }
                        if (!nameError && !quantityError) {
                            try {
                                onCreateInventory(
                                    name,
                                    quantity.toInt(),
                                    minQuantity.toInt(),
                                    maxQuantity.toInt(),
                                    location.ifEmpty { null }
                                )
                            } catch (e: Exception) {
                                // Handle number format exception
                            }
                        }
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && name.isNotBlank() && quantity.isNotEmpty() && minQuantity.isNotEmpty() && maxQuantity.isNotEmpty()
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("Create Inventory")
                    }
                }
            }
        }
    }
}
