# ANDROID CMMS - ARCHITECTURE DOCUMENTATION

**Version:** 1.0  
**Architecture Pattern:** MVVM + Clean Architecture  
**Last Updated:** 2025-01-14

---

## 🏗️ OVERALL ARCHITECTURE

```
┌──────────────────────────────────────────────────────┐
│          PRESENTATION LAYER (UI)                     │
├──────────────────────────────────────────────────────┤
│  Jetpack Compose Screens                             │
│  ├─ LoginScreen                                      │
│  ├─ DashboardScreen                                  │
│  ├─ AssetScreen + AssetDetailScreen                  │
│  ├─ WorksheetScreen + WorksheetDetailScreen          │
│  ├─ MachineScreen + MachineDetailScreen              │
│  ├─ InventoryScreen + InventoryDetailScreen          │
│  ├─ PMScreen                                         │
│  ├─ ReportsScreen                                    │
│  ├─ SettingsScreen                                   │
│  └─ UsersScreen                                      │
└──────────────────┬──────────────────────────────────┘
                   │ observes
                   ↓
┌──────────────────────────────────────────────────────┐
│     APPLICATION LAYER (ViewModels)                   │
├──────────────────────────────────────────────────────┤
│  ViewModel (StateFlow-based State Management)        │
│  ├─ LoginViewModel                                   │
│  ├─ DashboardViewModel                               │
│  ├─ AssetViewModel + AssetDetailViewModel            │
│  ├─ WorksheetViewModel + WorksheetDetailViewModel    │
│  ├─ MachineViewModel + MachineDetailViewModel        │
│  ├─ InventoryViewModel + InventoryDetailViewModel    │
│  ├─ PMViewModel                                      │
│  ├─ ReportsViewModel                                 │
│  └─ SettingsViewModel                                │
│                                                      │
│  Responsibilities:                                   │
│  ✓ UI State Management                               │
│  ✓ Business Logic Orchestration                      │
│  ✓ Event Handling                                    │
│  ✓ Data Transformation                               │
└──────────────────┬──────────────────────────────────┘
                   │ uses
                   ↓
┌──────────────────────────────────────────────────────┐
│        DOMAIN LAYER (Business Logic)                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  REPOSITORIES (CRUD Operations)                      │
│  ├─ AssetRepository                                  │
│  ├─ WorksheetRepository                              │
│  ├─ MachineRepository                                │
│  ├─ InventoryRepository                              │
│  ├─ PMRepository                                     │
│  ├─ AuthRepository                                   │
│  └─ UserRepository                                   │
│                                                      │
│  MODELS (Domain Entities)                            │
│  ├─ Asset                                            │
│  ├─ Worksheet                                        │
│  ├─ Machine                                          │
│  ├─ Inventory                                        │
│  ├─ PMTask                                           │
│  └─ User                                             │
│                                                      │
│  MAPPERS (Data Transformation)                       │
│  ├─ AssetMapper (Entity ↔ DTO ↔ Domain)             │
│  ├─ WorksheetMapper                                  │
│  ├─ MachineMapper                                    │
│  ├─ InventoryMapper                                  │
│  └─ PMTaskMapper                                     │
│                                                      │
│  Responsibilities:                                   │
│  ✓ Business Logic                                    │
│  ✓ CRUD Operations                                   │
│  ✓ Data Transformation                               │
│  ✓ Offline-First Strategy                            │
└──────────────────┬──────────────────────────────────┘
                   │ orchestrates
                   ↓
┌──────────────────────────────────────────────────────┐
│           DATA LAYER (I/O)                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  REMOTE DATA SOURCE (API)                            │
│  ├─ AuthApi (Retrofit)                               │
│  ├─ AssetApi                                         │
│  ├─ WorksheetApi                                     │
│  ├─ MachineApi                                       │
│  ├─ InventoryApi                                     │
│  └─ PMApi                                            │
│                                                      │
│  LOCAL DATA SOURCE (Room Database)                   │
│  ├─ CMMSDatabase                                     │
│  ├─ AssetDao ↔ AssetEntity                          │
│  ├─ WorksheetDao ↔ WorksheetEntity                  │
│  ├─ MachineDao ↔ MachineEntity                      │
│  ├─ InventoryDao ↔ InventoryEntity                  │
│  ├─ PMTaskDao ↔ PMTaskEntity                        │
│  └─ UserDao ↔ UserEntity                            │
│                                                      │
│  PREFERENCES (DataStore)                             │
│  └─ TokenManager (Encrypted Preferences)             │
│                                                      │
│  Responsibilities:                                   │
│  ✓ Remote API Communication                          │
│  ✓ Local Database Operations                         │
│  ✓ Data Caching & Offline Support                    │
│  ✓ Preference Storage (Token, Settings)              │
└──────────────────────────────────────────────────────┘
```

---

## 📊 DATA FLOW DIAGRAM

### User Login Flow

```
┌─────────────┐
│ LoginScreen │
└──────┬──────┘
       │ User enters email/password
       ↓
┌──────────────────────┐
│ LoginViewModel       │
│ login(email, pass)   │
└──────┬───────────────┘
       │ calls
       ↓
┌──────────────────────┐
│ AuthRepository       │
│ login()              │
└──────┬───────────────┘
       │ calls API
       ↓
┌──────────────────────┐
│ AuthApi              │
│ POST /auth/login     │
└──────┬───────────────┘
       │ returns JWT token
       ↓
┌──────────────────────┐
│ TokenManager         │
│ Save Token           │
└──────┬───────────────┘
       │ Update UI State
       ↓
┌──────────────────────┐
│ DashboardScreen      │
│ Navigated           │
└──────────────────────┘
```

### Asset CRUD Flow

```
┌─────────────────────┐
│ AssetsScreen        │
│ List Assets         │
└──────┬──────────────┘
       │ observes
       ↓
┌─────────────────────────┐
│ AssetViewModel          │
│ uiState: StateFlow      │
└──────┬──────────────────┘
       │ calls
       ↓
┌──────────────────────────┐
│ AssetRepository          │
│ getAssets(): Flow        │
└──────┬───────────────────┘
       │ priority: Local DB first
       ↓
       ├─ Local: AssetDao (Room)
       │  └─ Returns from cache immediately
       │
       └─ Remote: AssetApi (Retrofit)
          └─ GET /assets
          └─ Returns fresh data
          └─ Updates Room DB

┌─────────────────────┐
│ AssetsScreen        │
│ Displays List       │
│ + SwipeRefresh      │
└─────────────────────┘
```

---

## 🔄 STATE MANAGEMENT

### ViewModel + StateFlow Pattern

```kotlin
// ViewModel example
@HiltViewModel
class AssetViewModel @Inject constructor(
    private val repository: AssetRepository
) : ViewModel() {
    
    // UI State (immutable, reactive)
    private val _uiState = MutableStateFlow(AssetUiState())
    val uiState: StateFlow<AssetUiState> = _uiState.asStateFlow()
    
    // Events from UI
    fun loadAssets() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                repository.getAssets().collectLatest { assets ->
                    _uiState.update { 
                        it.copy(
                            assets = assets,
                            isLoading = false
                        )
                    }
                }
            } catch (e: Exception) {
                _uiState.update { 
                    it.copy(
                        error = e.message,
                        isLoading = false
                    )
                }
            }
        }
    }
}

// Screen observes state
@Composable
fun AssetScreen(viewModel: AssetViewModel) {
    val uiState by viewModel.uiState.collectAsState()
    
    // Recomposes whenever uiState changes
    LazyColumn {
        items(uiState.assets) { asset ->
            AssetCard(asset)
        }
    }
}
```

---

## 🔐 OFFLINE-FIRST ARCHITECTURE

```
┌─────────────────┐
│ Network State?  │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
 ONLINE    OFFLINE
    │         │
    │         └─→ Load from Room DB
    │             (Immediate response)
    │
    └─→ Try API Call
        ├─ Success
        │  └─→ Update Room DB
        │      └─→ Return to UI
        │
        └─ Failure
           └─→ Fallback to Room DB
               (Cache)
```

### Offline-First Benefits
- ✅ Instant data loading
- ✅ Works without internet
- ✅ Reduced API calls
- ✅ Better performance
- ✅ Improved UX

---

## 🔌 DEPENDENCY INJECTION (Hilt)

```
AppModule (Singleton)
├─ OkHttpClient (with Cache)
├─ Retrofit (REST Client)
├─ CMMSDatabase (Room DB)
├─ APIs
│  ├─ AuthApi
│  ├─ AssetApi
│  ├─ WorksheetApi
│  ├─ MachineApi
│  ├─ InventoryApi
│  └─ PMApi
├─ DAOs
│  ├─ AssetDao
│  ├─ WorksheetDao
│  ├─ MachineDao
│  ├─ InventoryDao
│  ├─ PMTaskDao
│  └─ UserDao
├─ Repositories
│  ├─ AssetRepository
│  ├─ WorksheetRepository
│  ├─ MachineRepository
│  ├─ InventoryRepository
│  ├─ PMRepository
│  └─ AuthRepository
├─ TokenManager
└─ Application Context

@HiltViewModel
Each ViewModel auto-injects dependencies
```

---

## 🗄️ DATABASE SCHEMA

```sql
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT,
    serialNumber TEXT,
    model TEXT,
    manufacturer TEXT,
    location TEXT,
    category TEXT,
    assetTag TEXT,
    purchaseDate LONG,
    purchasePrice REAL,
    warrantyExpiry LONG,
    description TEXT,
    createdAt LONG,
    updatedAt LONG
);

CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_name ON assets(name);
CREATE INDEX idx_assets_assetTag ON assets(assetTag);

-- Similar for other entities (worksheets, machines, inventory, pm_tasks)
```

---

## 🔄 LIFECYCLE & MEMORY MANAGEMENT

```
App Start
├─ Application created
├─ Hilt DI initialized
├─ Database opened (Room)
├─ Preferences loaded (DataStore)
└─ Ready for UI

ViewModel Lifecycle
├─ Created when Screen composed
├─ Data flows collected
├─ State updated
└─ Destroyed when Screen removed

Memory Management
├─ LeakCanary monitors (debug)
├─ Coroutines properly scoped
├─ Flows properly collected
└─ Resources cleaned up
```

---

## 🎯 KEY ARCHITECTURAL PRINCIPLES

### 1. Single Responsibility
Each class has ONE reason to change.

### 2. Dependency Inversion
High-level modules don't depend on low-level modules.
Both depend on abstractions (interfaces/repositories).

### 3. Offline-First
Local data is always priority, API is secondary.

### 4. Reactive Programming
Everything is Flow-based for real-time updates.

### 5. Testability
All layers are independently testable through DI.

---

## 📈 PERFORMANCE OPTIMIZATIONS

- ✅ Room Database indexing (fast queries)
- ✅ OkHttp caching (reduce API calls)
- ✅ Lazy loading (Jetpack Compose)
- ✅ Flow-based state (efficient recomposition)
- ✅ Coroutine scoping (memory safe)
- ✅ LeakCanary monitoring (memory leaks)

---

## 🔄 SEQUENCE DIAGRAM - Asset Creation

```
User          UI           ViewModel     Repository    API       Database
 │             │              │            │           │           │
 │──Create───→ │              │            │           │           │
 │             │──loadForm──→ │            │           │           │
 │             │←─setState───│            │           │           │
 │─Fills Form→ │              │            │           │           │
 │─Clicks Save→│              │            │           │           │
 │             │─validateForm→ │            │           │           │
 │             │←─valid───────│            │           │           │
 │             │─createAsset→ │            │           │           │
 │             │              │─create()─→ │           │           │
 │             │              │            │─POST API→ │           │
 │             │              │            │←─response│           │
 │             │              │            │─save()──→ │───INSERT→ │
 │             │              │            │←─saved───│←─success─ │
 │             │←─onSuccess──│←─result────│           │           │
 │←─Redirect──│              │            │           │           │
 │             │              │            │           │           │
```

---

**Architecture Version:** 1.0  
**Last Updated:** 2025-01-14  
**Status:** Production Ready ✅

