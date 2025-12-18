package com.artence.cmms.ui.screens.worksheets

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
import com.artence.cmms.ui.screens.worksheets.create.CreateWorksheetViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CreateWorksheetScreen(
    navController: NavController,
    viewModel: CreateWorksheetViewModel = hiltViewModel()
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
            snackbarHostState.showSnackbar("Worksheet created successfully")
            navController.navigateUp()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Create New Worksheet") },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        CreateWorksheetForm(
            isLoading = uiState.isLoading,
            onCreateWorksheet = { title, description, priority ->
                viewModel.createWorksheet(
                    title = title,
                    description = description,
                    priority = priority,
                    status = "Pending"
                )
            },
            onCancel = { navController.navigateUp() },
            modifier = Modifier.padding(paddingValues)
        )
    }
}

@Composable
private fun CreateWorksheetForm(
    isLoading: Boolean,
    onCreateWorksheet: (String, String?, String?) -> Unit,
    onCancel: () -> Unit,
    modifier: Modifier = Modifier
) {
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var priority by remember { mutableStateOf("") }
    var titleError by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text(
                "Worksheet Details",
                style = MaterialTheme.typography.titleMedium
            )
        }

        item {
            OutlinedTextField(
                value = title,
                onValueChange = {
                    title = it
                    titleError = false
                },
                label = { Text("Title *") },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading,
                isError = titleError,
                supportingText = {
                    if (titleError) Text("Title is required", color = MaterialTheme.colorScheme.error)
                }
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
                enabled = !isLoading,
                supportingText = { Text("e.g. Low, Medium, High") }
            )
        }

        item {
            Text(
                "Status: Pending (default)",
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
                        if (title.isBlank()) {
                            titleError = true
                        } else {
                            onCreateWorksheet(
                                title,
                                description.ifEmpty { null },
                                priority.ifEmpty { null }
                            )
                        }
                    },
                    modifier = Modifier.weight(1f),
                    enabled = !isLoading && title.isNotEmpty()
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colorScheme.onPrimary
                        )
                    } else {
                        Text("Create Worksheet")
                    }
                }
            }
        }
    }
}

