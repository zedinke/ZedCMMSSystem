package com.artence.cmms.ui.screens.worksheets

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
import com.artence.cmms.domain.model.Worksheet
import com.artence.cmms.ui.screens.worksheets.detail.WorksheetDetailViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WorksheetDetailScreen(
    worksheetId: Int,
    navController: NavController,
    viewModel: WorksheetDetailViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showDeleteConfirmDialog by remember { mutableStateOf(false) }
    var showStatusChangeDialog by remember { mutableStateOf(false) }
    var isEditMode by remember { mutableStateOf(false) }
    var selectedStatus by remember { mutableStateOf("") }

    val statusOptions = listOf("Pending", "In Progress", "Completed", "Cancelled")

    // Load worksheet on mount
    LaunchedEffect(worksheetId) {
        viewModel.loadWorksheet(worksheetId)
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
            snackbarHostState.showSnackbar("Worksheet deleted successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(uiState.worksheet?.title ?: "Worksheet Details") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    if (!isEditMode) {
                        IconButton(onClick = { showStatusChangeDialog = true }) {
                            Icon(Icons.Default.EditNote, contentDescription = "Change Status")
                        }
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
        } else if (uiState.worksheet != null) {
            if (isEditMode) {
                EditWorksheetForm(
                    worksheet = uiState.worksheet!!,
                    isLoading = uiState.isSaving,
                    onSave = { title, description, priority ->
                        viewModel.updateWorksheet(
                            id = worksheetId,
                            title = title,
                            description = description,
                            priority = priority
                        )
                        isEditMode = false
                    },
                    onCancel = { isEditMode = false },
                    modifier = Modifier.padding(paddingValues)
                )
            } else {
                WorksheetDetailView(
                    worksheet = uiState.worksheet!!,
                    modifier = Modifier.padding(paddingValues)
                )
            }
        }
    }

    // Delete confirmation dialog
    if (showDeleteConfirmDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteConfirmDialog = false },
            title = { Text("Delete Worksheet") },
            text = { Text("Are you sure you want to delete this worksheet? This action cannot be undone.") },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.deleteWorksheet(worksheetId)
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

    // Status change dialog
    if (showStatusChangeDialog) {
        AlertDialog(
            onDismissRequest = { showStatusChangeDialog = false },
            title = { Text("Change Status") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    statusOptions.forEach { status ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            RadioButton(
                                selected = status == uiState.worksheet?.status,
                                onClick = { selectedStatus = status },
                                modifier = Modifier.padding(end = 8.dp)
                            )
                            Text(status)
                        }
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.updateWorksheetStatus(worksheetId, selectedStatus)
                        showStatusChangeDialog = false
                    },
                    enabled = selectedStatus.isNotEmpty()
                ) {
                    Text("Confirm")
                }
            },
            dismissButton = {
                TextButton(onClick = { showStatusChangeDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}

@Composable
private fun WorksheetDetailView(
    worksheet: Worksheet,
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
                    DetailRow("Title", worksheet.title)
                    DetailRow(
                        "Status",
                        worksheet.status,
                        getStatusColor(worksheet.status)
                    )
                    if (worksheet.priority != null) {
                        DetailRow("Priority", worksheet.priority!!)
                    }
                    if (worksheet.description != null && worksheet.description!!.isNotEmpty()) {
                        DetailRow("Description", worksheet.description!!)
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
                        "Assignment",
                        style = MaterialTheme.typography.titleMedium
                    )
                    if (worksheet.machineId != null) {
                        DetailRow("Machine ID", worksheet.machineId.toString())
                    }
                    if (worksheet.assignedToUserId != null) {
                        DetailRow("Assigned User ID", worksheet.assignedToUserId.toString())
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
                        "Timeline",
                        style = MaterialTheme.typography.titleMedium
                    )
                    DetailRow("Created", worksheet.createdAtFormatted)
                    DetailRow("Updated", worksheet.updatedAtFormatted ?: "Never")
                }
            }
        }
    }
}

@Composable
private fun EditWorksheetForm(
    worksheet: Worksheet,
    isLoading: Boolean,
    onSave: (String, String?, String?) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var title by remember { mutableStateOf(worksheet.title) }
    var description by remember { mutableStateOf(worksheet.description ?: "") }
    var priority by remember { mutableStateOf(worksheet.priority ?: "") }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            OutlinedTextField(
                value = title,
                onValueChange = { title = it },
                label = { Text("Title") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            )
        }

        item {
            OutlinedTextField(
                value = description,
                onValueChange = { description = it },
                label = { Text("Description") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                minLines = 3
            )
        }

        item {
            OutlinedTextField(
                value = priority,
                onValueChange = { priority = it },
                label = { Text("Priority") },
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
                        onSave(
                            title,
                            description.ifEmpty { null },
                            priority.ifEmpty { null }
                        )
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && title.isNotEmpty()
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
private fun DetailRow(
    label: String,
    value: String,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Column {
        Text(
            label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            value,
            style = MaterialTheme.typography.bodyMedium,
            color = valueColor
        )
    }
}

private fun getStatusColor(status: String): Color {
    return when (status) {
        "Pending" -> Color(0xFFFFC107) // Amber
        "In Progress" -> Color(0xFF2196F3) // Blue
        "Completed" -> Color(0xFF4CAF50) // Green
        "Cancelled" -> Color(0xFFF44336) // Red
        else -> Color.Gray
    }
}

