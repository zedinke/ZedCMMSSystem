package com.artence.cmms.ui.screens.machines

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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.artence.cmms.R
import com.artence.cmms.domain.model.Machine
import com.artence.cmms.ui.screens.machines.detail.MachineDetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MachineDetailScreen(
    machineId: Int,
    navController: NavController,
    viewModel: MachineDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showDeleteConfirmDialog by remember { mutableStateOf(false) }
    var isEditMode by remember { mutableStateOf(false) }

    // Load machine on mount
    LaunchedEffect(machineId) {
        viewModel.loadMachine(machineId)
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
            snackbarHostState.showSnackbar("Machine deleted successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(uiState.machine?.name ?: "Machine Details") },
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
        } else if (uiState.machine != null) {
            if (isEditMode) {
                EditMachineForm(
                    machine = uiState.machine!!,
                    isLoading = uiState.isSaving,
                    onSave = { name, serialNumber, model, manufacturer, status ->
                        viewModel.updateMachine(
                            id = machineId,
                            name = name,
                            serialNumber = serialNumber,
                            model = model,
                            manufacturer = manufacturer,
                            status = status
                        )
                        isEditMode = false
                    },
                    onCancel = { isEditMode = false },
                    modifier = Modifier.padding(paddingValues)
                )
            } else {
                MachineDetailView(
                    machine = uiState.machine!!,
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }
    }

    // Delete confirmation dialog
    if (showDeleteConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteConfirmDialog = false },
            title = { Text("Delete Machine") },
            text = { Text("Are you sure you want to delete this machine? This action cannot be undone.") },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.deleteMachine(machineId)
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
private fun MachineDetailView(
    machine: Machine,
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
                    // Header with name and status
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            "Machine Info",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.weight(1f)
                        )
                        Surface(
                            shape = MaterialTheme.shapes.small,
                            color = machine.status.getMachineStatusColor().copy(alpha = 0.2f)
                        ) {
                            Text(
                                text = machine.status,
                                style = MaterialTheme.typography.labelSmall,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                color = machine.status.getMachineStatusColor()
                            )
                        }
                    }

                    DetailRow("Name", machine.name)
                    DetailRow("Serial Number", machine.serialNumber ?: "N/A")
                    DetailRow("Model", machine.model ?: "N/A")
                    DetailRow("Manufacturer", machine.manufacturer ?: "N/A")
                    DetailRow("Asset Tag", machine.assetTag ?: "N/A")
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
                        "Production Line",
                        style = MaterialTheme.typography.titleMedium
                    )
                    DetailRow("ID", machine.productionLineId.toString())
                    DetailRow("Name", machine.productionLineName ?: "N/A")
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
                    if (machine.installDateFormatted != null) {
                        DetailRow("Install Date", machine.installDateFormatted!!)
                    }
                    DetailRow("Created", machine.createdAtFormatted)
                    DetailRow("Updated", machine.updatedAtFormatted ?: "Never")
                }
            }
        }

        if (!machine.description.isNullOrEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            "Description",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            machine.description,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun EditMachineForm(
    machine: Machine,
    isLoading: Boolean,
    onSave: (String, String?, String?, String?, String) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var name by remember { mutableStateOf(machine.name) }
    var serialNumber by remember { mutableStateOf(machine.serialNumber ?: "") }
    var model by remember { mutableStateOf(machine.model ?: "") }
    var manufacturer by remember { mutableStateOf(machine.manufacturer ?: "") }
    var status by remember { mutableStateOf(machine.status) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            OutlinedTextField(
                value = name,
                onValueChange = { name = it },
                label = { Text("Name") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
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
            OutlinedTextField(
                value = status,
                onValueChange = { status = it },
                label = { Text("Status") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                readOnly = true
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
                        onSave(
                            name,
                            serialNumber.ifEmpty { null },
                            model.ifEmpty { null },
                            manufacturer.ifEmpty { null },
                            status
                        )
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && name.isNotEmpty()
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

private fun String.getMachineStatusColor(): Color {
    return when (this) {
        "Operational" -> Color(0xFF4CAF50) // Green
        "Maintenance" -> Color(0xFFFFC107) // Amber
        "Breakdown" -> Color(0xFFF44336) // Red
        "Offline" -> Color(0xFF9E9E9E) // Gray
        else -> Color.Gray
    }
}

