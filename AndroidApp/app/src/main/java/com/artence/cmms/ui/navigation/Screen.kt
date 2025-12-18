package com.artence.cmms.ui.navigation

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Dashboard : Screen("dashboard")

    object Assets : Screen("assets")
    object AssetDetail : Screen("asset/{assetId}") {
        fun createRoute(assetId: Int) = "asset/$assetId"
    }
    object CreateAsset : Screen("create_asset")

    object Worksheets : Screen("worksheets")
    object WorksheetDetail : Screen("worksheet/{worksheetId}") {
        fun createRoute(worksheetId: Int) = "worksheet/$worksheetId"
    }
    object CreateWorksheet : Screen("create_worksheet")

    object Machines : Screen("machines")
    object MachineDetail : Screen("machine/{machineId}") {
        fun createRoute(machineId: Int) = "machine/$machineId"
    }

    object Inventory : Screen("inventory")
    object InventoryDetail : Screen("inventory/{inventoryId}") {
        fun createRoute(inventoryId: Int) = "inventory/$inventoryId"
    }
    object CreateInventory : Screen("create_inventory")

    object Settings : Screen("settings")

    object PM : Screen("pm")
    object Reports : Screen("reports")
    object Users : Screen("users")
}



