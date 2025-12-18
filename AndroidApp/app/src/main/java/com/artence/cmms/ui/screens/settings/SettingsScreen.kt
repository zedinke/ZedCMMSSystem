package com.artence.cmms.ui.screens.settings

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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    navController: NavController,
    viewModel: SettingsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    var showLogoutDialog by remember { mutableStateOf(false) }
    var showLanguageDialog by remember { mutableStateOf(false) }

    // Show error snackbar
    LaunchedEffect(uiState.error) {
        uiState.error?.let { error ->
            snackbarHostState.showSnackbar(error)
            viewModel.clearError()
        }
    }

    // On logout, navigate to login
    LaunchedEffect(uiState.isLoggedOut) {
        if (uiState.isLoggedOut) {
            navController.navigate("login") {
                popUpTo("dashboard") { inclusive = true }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.settings)) },
                navigationIcon = {
                    IconButton(onClick = { navController.navigateUp() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = stringResource(R.string.cancel))
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Profile Section
            item {
                Text(
                    stringResource(R.string.settings_profile),
                    style = MaterialTheme.typography.titleMedium
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text("${stringResource(R.string.username)}: ${uiState.username ?: stringResource(R.string.not_available)}")
                        Text("${stringResource(R.string.email)}: ${uiState.email ?: stringResource(R.string.not_available)}")
                        Text("${stringResource(R.string.role)}: ${uiState.role ?: stringResource(R.string.not_available)}")

                        Button(
                            onClick = { navController.navigate("profile_edit") },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Icon(Icons.Default.Edit, contentDescription = null)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(stringResource(R.string.settings_edit_profile))
                        }
                    }
                }
            }

            // Preferences Section
            item {
                Text(
                    stringResource(R.string.settings_preferences),
                    style = MaterialTheme.typography.titleMedium
                )
            }

            // Language Setting
            item {
                SettingsRow(
                    title = stringResource(R.string.settings_language),
                    subtitle = when (uiState.language) {
                        "hu" -> stringResource(R.string.settings_language_hungarian)
                        "en" -> stringResource(R.string.settings_language_english)
                        else -> stringResource(R.string.settings_language_system)
                    },
                    icon = Icons.Default.Language,
                    onClick = { showLanguageDialog = true }
                )
            }

            // Theme Setting
            item {
                SettingsRow(
                    title = stringResource(R.string.settings_theme),
                    subtitle = if (uiState.isDarkMode) stringResource(R.string.settings_theme_dark) else stringResource(R.string.settings_theme_light),
                    icon = if (uiState.isDarkMode) Icons.Default.Bedtime else Icons.Default.LightMode,
                    onClick = { viewModel.toggleDarkMode() }
                )
            }

            // Notifications Setting
            item {
                SettingsToggle(
                    title = stringResource(R.string.settings_enable_notifications),
                    isEnabled = uiState.notificationsEnabled,
                    icon = Icons.Default.NotificationsActive,
                    onToggle = { viewModel.setNotifications(it) }
                )
            }

            // Offline Mode Setting
            item {
                SettingsToggle(
                    title = stringResource(R.string.settings_offline_mode),
                    subtitle = stringResource(R.string.settings_offline_mode_subtitle),
                    isEnabled = uiState.offlineMode,
                    icon = Icons.Default.CloudOff,
                    onToggle = { viewModel.setOfflineMode(it) }
                )
            }

            // About Section
            item {
                Text(
                    stringResource(R.string.settings_about),
                    style = MaterialTheme.typography.titleMedium
                )
            }

            item {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text("${stringResource(R.string.settings_app_version)}: 1.0.0")
                        Text("${stringResource(R.string.settings_build)}: ${uiState.buildNumber ?: stringResource(R.string.not_available)}")
                        Text("${stringResource(R.string.settings_database)}: ${stringResource(R.string.settings_database_synced)}")

                        Button(
                            onClick = { /* TODO: Show about dialog */ },
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 8.dp)
                        ) {
                            Text(stringResource(R.string.settings_privacy_policy))
                        }
                    }
                }
            }

            // Danger Zone
            item {
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    stringResource(R.string.settings_danger_zone),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.error
                )
            }

            item {
                Button(
                    onClick = { showLogoutDialog = true },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Icon(Icons.Default.Logout, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(stringResource(R.string.logout))
                }
            }
        }
    }

    // Language Dialog
    if (showLanguageDialog) {
        AlertDialog(
            onDismissRequest = { showLanguageDialog = false },
            title = { Text(stringResource(R.string.settings_select_language)) },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    LanguageOption(
                        label = stringResource(R.string.settings_language_english),
                        code = "en",
                        isSelected = uiState.language == "en",
                        onClick = {
                            viewModel.setLanguage("en")
                            showLanguageDialog = false
                        }
                    )
                    LanguageOption(
                        label = stringResource(R.string.settings_language_hungarian),
                        code = "hu",
                        isSelected = uiState.language == "hu",
                        onClick = {
                            viewModel.setLanguage("hu")
                            showLanguageDialog = false
                        }
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = { showLanguageDialog = false }) {
                    Text(stringResource(R.string.close))
                }
            }
        )
    }

    // Logout Confirmation Dialog
    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = { Text(stringResource(R.string.logout)) },
            text = { Text(stringResource(R.string.settings_logout_confirm)) },
            confirmButton = {
                Button(
                    onClick = {
                        viewModel.logout()
                        showLogoutDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.error
                    )
                ) {
                    Text(stringResource(R.string.logout))
                }
            },
            dismissButton = {
                TextButton(onClick = { showLogoutDialog = false }) {
                    Text(stringResource(R.string.cancel))
                }
            }
        )
    }
}

@Composable
private fun SettingsRow(
    title: String,
    subtitle: String,
    icon: ImageVector,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Column {
                    Text(title, style = MaterialTheme.typography.bodyMedium)
                    Text(
                        subtitle,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            Icon(Icons.Default.ChevronRight, contentDescription = null)
        }
    }
}

@Composable
private fun SettingsToggle(
    title: String,
    subtitle: String = "",
    isEnabled: Boolean,
    icon: ImageVector,
    onToggle: (Boolean) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary
                )
                Column {
                    Text(title, style = MaterialTheme.typography.bodyMedium)
                    if (subtitle.isNotEmpty()) {
                        Text(
                            subtitle,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
            Switch(
                checked = isEnabled,
                onCheckedChange = onToggle
            )
        }
    }
}

@Composable
private fun LanguageOption(
    label: String,
    code: String,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        RadioButton(
            selected = isSelected,
            onClick = onClick
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(label)
    }
}
