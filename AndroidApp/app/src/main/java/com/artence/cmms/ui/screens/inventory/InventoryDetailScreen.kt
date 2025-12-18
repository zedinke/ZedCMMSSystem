package com.artence.cmms.ui.screens.inventory

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.artence.cmms.domain.model.Inventory
import com.artence.cmms.ui.screens.inventory.detail.InventoryDetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InventoryDetailScreen(
    inventoryId: Int,
    navController: NavController,
    viewModel: InventoryDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showDeleteConfirmDialog by remember { mutableStateOf(false) }
    var isEditMode by remember { mutableStateOf(false) }

    // Load inventory on mount
    LaunchedEffect(inventoryId) {
        viewModel.loadInventory(inventoryId)
    }

    // Show error snackbar
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(error)
            viewModel.clearError()
        }
    }

    // Show success message
    LaunchedEffect(uiState.isDeleted) {
        if (uiState.isDeleted) {
            snackbarHostState.showSnackbar("Inventory item deleted successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(uiState.inventory?.partName ?: "Inventory Details") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (!isEditMode) {
                        IconButton(onClick = { isEditMode = true }) {
                            Icon(Icons.Default.Edit, contentDescription = "Edit")
                        }
                        IconButton(onClick = { showDeleteConfirmDialog = true }) {
                            Icon(Icons.Default.Delete, contentDescription = "Delete")
                        }
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        if (uiState.isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (uiState.inventory != null) {
            if (isEditMode) {
                EditInventoryForm(
                    inventory = uiState.inventory!!,
                    isLoading = uiState.isSaving,
                    onSave = { quantity, minQuantity, maxQuantity, location ->
                        viewModel.updateInventory(
                            id = inventoryId,
                            quantity = quantity,
                            minQuantity = minQuantity,
                            maxQuantity = maxQuantity,
                            location = location
                        )
                        isEditMode = false
                    },
                    onCancel = { isEditMode = false },
                    modifier = Modifier.padding(paddingValues)
                )
            } else {
                InventoryDetailView(
                    inventory = uiState.inventory!!,
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }
    }

    // Delete confirmation dialog
    if (showDeleteConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteConfirmDialog = false },
            title = { Text("Delete Inventory Item") },
            text = { Text("Are you sure you want to delete this inventory item? This action cannot be undone.") },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.deleteInventory(inventoryId)
                        showDeleteConfirmDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text("Delete")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteConfirmDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun InventoryDetailView(
    inventory: Inventory,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Header with status badge
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            inventory.partName ?: "N/A",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.weight(1f)
                        )
                        Surface(
                            shape = MaterialTheme.shapes.small,
                            color = inventory.getStatus().getInventoryStatusColor().copy(alpha = 0.2f)
                        ) {
                            Text(
                                text = inventory.getStatus(),
                                style = MaterialTheme.typography.labelSmall,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                color = inventory.getStatus().getInventoryStatusColor()
                            )
                        }
                    }

                    DetailRow("Location", inventory.location ?: "N/A")
                    if (inventory.assetName != null) {
                        DetailRow("Asset", inventory.assetName!!)
                    }
                }
            }
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Stock Information",
                        style = MaterialTheme.typography.titleMedium
                    )

                    // Stock progress bar
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("Current Stock", style = MaterialTheme.typography.bodySmall)
                            Text(
                                "${inventory.quantity} units",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.primary
                            )
                        }

                        val progressValue = run {
                            val maxRange = inventory.maxQuantity.coerceAtLeast(1)
                            (inventory.quantity.toFloat() / maxRange).coerceIn(0f, 1f)
                        }
                        LinearProgressIndicator(
                            progress = progressValue,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    DetailRow("Min Quantity", inventory.minQuantity.toString())
                    DetailRow("Max Quantity", inventory.maxQuantity.toString())
                }
            }
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "Timeline",
                        style = MaterialTheme.typography.titleMedium
                    )
                    DetailRow("Created", inventory.createdAtFormatted)
                    DetailRow("Last Updated", inventory.lastUpdatedFormatted)
                }
            }
        }
    }
}

@Composable
private fun EditInventoryForm(
    inventory: Inventory,
    isLoading: Boolean,
    onSave: (Int, Int, Int, String?) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var quantity by remember { mutableStateOf(inventory.quantity.toString()) }
    var minQuantity by remember { mutableStateOf(inventory.minQuantity.toString()) }
    var maxQuantity by remember { mutableStateOf(inventory.maxQuantity.toString()) }
    var location by remember { mutableStateOf(inventory.location ?: "") }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            OutlinedTextField(
                value = quantity,
                onValueChange = { quantity = it },
                label = { Text("Current Quantity") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }

        item {
            OutlinedTextField(
                value = minQuantity,
                onValueChange = { minQuantity = it },
                label = { Text("Minimum Quantity") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }

        item {
            OutlinedTextField(
                value = maxQuantity,
                onValueChange = { maxQuantity = it },
                label = { Text("Maximum Quantity") },
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
                        try {
                            onSave(
                                quantity.toInt(),
                                minQuantity.toInt(),
                                maxQuantity.toInt(),
                                location.ifEmpty { null }
                            )
                        } catch (e: Exception) {
                            // Handle invalid input
                        }
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading &&
                            quantity.isNotEmpty() &&
                            minQuantity.isNotEmpty() &&
                            maxQuantity.isNotEmpty()
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp))
                    } else {
                        Text("Save")
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Column {
        Text(
            label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

private fun String.getInventoryStatusColor(): Color {
    return when (this) {
        "Out of Stock" -> Color(0xFFF44336) // Red
        "Low Stock" -> Color(0xFFFFC107) // Amber
        "Overstocked" -> Color(0xFF2196F3) // Blue
        "Normal" -> Color(0xFF4CAF50) // Green
        else -> Color.Gray
    }
}
