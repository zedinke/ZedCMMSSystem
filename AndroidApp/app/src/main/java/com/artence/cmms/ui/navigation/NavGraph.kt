package com.artence.cmms.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.artence.cmms.data.local.datastore.TokenManager
import com.artence.cmms.ui.screens.assets.AssetDetailScreen
import com.artence.cmms.ui.screens.assets.AssetsScreen
import com.artence.cmms.ui.screens.assets.CreateAssetScreen
import com.artence.cmms.ui.screens.dashboard.DashboardScreen
import com.artence.cmms.ui.screens.inventory.CreateInventoryScreen
import com.artence.cmms.ui.screens.inventory.InventoryDetailScreen
import com.artence.cmms.ui.screens.inventory.InventoryScreen
import com.artence.cmms.ui.screens.login.LoginScreen
import com.artence.cmms.ui.screens.machines.MachineDetailScreen
import com.artence.cmms.ui.screens.machines.MachinesScreen
import com.artence.cmms.ui.screens.pm.PMScreen
import com.artence.cmms.ui.screens.reports.ReportsScreen
import com.artence.cmms.ui.screens.settings.SettingsScreen
import com.artence.cmms.ui.screens.users.UsersScreen
import com.artence.cmms.ui.screens.worksheets.CreateWorksheetScreen
import com.artence.cmms.ui.screens.worksheets.WorksheetDetailScreen
import com.artence.cmms.ui.screens.worksheets.WorksheetsScreen
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking

@Composable
fun NavGraph(
    navController: NavHostController,
    tokenManager: TokenManager
) {
    // Check if user is logged in
    val token = runBlocking { tokenManager.getToken().first() }
    val startDestination = if (token.isNullOrEmpty()) {
        Screen.Login.route
    } else {
        Screen.Dashboard.route
    }

    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Dashboard.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.Dashboard.route) {
            DashboardScreen(
                navController = navController
            )
        }

        composable(Screen.Assets.route) {
            AssetsScreen(
                navController = navController
            )
        }

        composable(Screen.AssetDetail.route) { backStackEntry ->
            val assetId = backStackEntry.arguments?.getString("assetId")?.toIntOrNull() ?: return@composable
            AssetDetailScreen(
                assetId = assetId,
                navController = navController
            )
        }

        composable(Screen.CreateAsset.route) {
            CreateAssetScreen(
                navController = navController
            )
        }

        composable(Screen.Worksheets.route) {
            WorksheetsScreen(
                navController = navController
            )
        }

        composable(Screen.WorksheetDetail.route) { backStackEntry ->
            val worksheetId = backStackEntry.arguments?.getString("worksheetId")?.toIntOrNull() ?: return@composable
            WorksheetDetailScreen(
                worksheetId = worksheetId,
                navController = navController
            )
        }

        composable(Screen.CreateWorksheet.route) {
            CreateWorksheetScreen(
                navController = navController
            )
        }

        composable(Screen.Machines.route) {
            MachinesScreen(
                navController = navController
            )
        }

        composable(Screen.MachineDetail.route) { backStackEntry ->
            val machineId = backStackEntry.arguments?.getString("machineId")?.toIntOrNull() ?: return@composable
            MachineDetailScreen(
                machineId = machineId,
                navController = navController
            )
        }

        composable(Screen.Inventory.route) {
            InventoryScreen(
                navController = navController
            )
        }

        composable(Screen.InventoryDetail.route) { backStackEntry ->
            val inventoryId = backStackEntry.arguments?.getString("inventoryId")?.toIntOrNull() ?: return@composable
            InventoryDetailScreen(
                inventoryId = inventoryId,
                navController = navController
            )
        }

        composable(Screen.CreateInventory.route) {
            CreateInventoryScreen(
                navController = navController
            )
        }

        composable(Screen.Settings.route) {
            SettingsScreen(
                navController = navController
            )
        }

        composable(Screen.PM.route) {
            PMScreen(
                navController = navController
            )
        }

        composable(Screen.Reports.route) {
            ReportsScreen(
                navController = navController
            )
        }

        composable(Screen.Users.route) {
            UsersScreen(
                navController = navController
            )
        }

        // Add other screens here
    }
}

