package com.artence.cmms.ui.screens.reports

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.artence.cmms.R
import com.google.accompanist.swiperefresh.SwipeRefresh
import com.google.accompanist.swiperefresh.rememberSwipeRefreshState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReportsScreen(
    navController: NavController,
    viewModel: ReportsViewModel = hiltViewModel()
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

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.reports)) },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = stringResource(R.string.cancel))
                    }
                },
                actions = {
                    IconButton(onClick = { viewModel.refreshReports() }) {
                        Icon(Icons.Default.Refresh, contentDescription = stringResource(R.string.refresh))
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        SwipeRefresh(
            state = rememberSwipeRefreshState(uiState.isRefreshing),
            onRefresh = { viewModel.refreshReports() },
            modifier = Modifier.padding(paddingValues)
        ) {
            if (uiState.isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    // Summary Section
                    item {
                        Text(
                            stringResource(R.string.reports_summary),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }

                    item {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(120.dp),
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            StatCard(
                                title = stringResource(R.string.reports_machines_total),
                                value = uiState.machinesTotal.toString(),
                                icon = Icons.Default.Build,
                                modifier = Modifier.weight(1f)
                            )
                            StatCard(
                                title = stringResource(R.string.reports_worksheets_open),
                                value = uiState.worksheetsOpen.toString(),
                                icon = Icons.Default.Assignment,
                                modifier = Modifier.weight(1f)
                            )
                            StatCard(
                                title = stringResource(R.string.reports_pm_due_this_week),
                                value = uiState.pmDueThisWeek.toString(),
                                icon = Icons.Default.Schedule,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }

                    item {
                        StatCard(
                            title = stringResource(R.string.reports_inventory_low_stock),
                            value = uiState.inventoryLowStock.toString(),
                            icon = Icons.Default.Warning,
                            modifier = Modifier.fillMaxWidth()
                        )
                    }

                    // Maintenance Section
                    item {
                        Text(
                            stringResource(R.string.reports_maintenance),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_maintenance_history),
                            subtitle = stringResource(R.string.reports_maintenance_history_subtitle),
                            icon = Icons.Default.History,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_pm_schedule),
                            subtitle = stringResource(R.string.reports_pm_schedule_subtitle),
                            icon = Icons.Default.Schedule,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_maintenance_costs),
                            subtitle = stringResource(R.string.reports_maintenance_costs_subtitle),
                            icon = Icons.Default.AttachMoney,
                            onClick = { /* TODO */ }
                        )
                    }

                    // Inventory Section
                    item {
                        Text(
                            stringResource(R.string.inventory),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_stock_levels),
                            subtitle = stringResource(R.string.reports_stock_levels_subtitle),
                            icon = Icons.Default.Inventory,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_low_stock_items),
                            subtitle = stringResource(R.string.reports_low_stock_items_subtitle),
                            icon = Icons.Default.Warning,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_stock_movements),
                            subtitle = stringResource(R.string.reports_stock_movements_subtitle),
                            icon = Icons.Default.SwapHoriz,
                            onClick = { /* TODO */ }
                        )
                    }

                    // Performance Section
                    item {
                        Text(
                            stringResource(R.string.reports_performance),
                            style = MaterialTheme.typography.titleMedium
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_machine_performance),
                            subtitle = stringResource(R.string.reports_machine_performance_subtitle),
                            icon = Icons.Default.BarChart,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        ReportCard(
                            title = stringResource(R.string.reports_technician_performance),
                            subtitle = stringResource(R.string.reports_technician_performance_subtitle),
                            icon = Icons.Default.Person,
                            onClick = { /* TODO */ }
                        )
                    }

                    item {
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }
            }
        }
    }
}

@Composable
private fun StatCard(
    title: String,
    value: String,
    icon: ImageVector,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.1f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(24.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                value,
                style = MaterialTheme.typography.headlineSmall,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                title,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

@Composable
private fun ReportCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                modifier = Modifier.size(32.dp),
                tint = MaterialTheme.colorScheme.primary
            )
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    title,
                    style = MaterialTheme.typography.bodyMedium
                )
                Text(
                    subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
