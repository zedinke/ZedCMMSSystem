# Android Fejlesztői Gyorsreferencia

## 🚀 Gyakori Parancsok

### Build
```bash
# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Clean build
./gradlew clean build
```

### Testing
```bash
# Unit tests
./gradlew test

# Connected tests
./gradlew connectedAndroidTest
```

## 📁 Fájl Struktúra Sablon

### Új Screen Hozzáadása

1. **Screen definíció** (`ui/navigation/Screen.kt`):
```kotlin
object MyScreen : Screen("my_screen")
```

2. **ViewModel** (`ui/screens/myscreen/MyScreenViewModel.kt`):
```kotlin
@HiltViewModel
class MyScreenViewModel @Inject constructor(
    private val myUseCase: MyUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow(MyUiState())
    val uiState: StateFlow<MyUiState> = _uiState.asStateFlow()
}
```

3. **Screen Composable** (`ui/screens/myscreen/MyScreen.kt`):
```kotlin
@Composable
fun MyScreen(
    navController: NavController,
    viewModel: MyScreenViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    // UI implementation
}
```

4. **NavGraph hozzáadás** (`ui/navigation/NavGraph.kt`):
```kotlin
composable(Screen.MyScreen.route) {
    MyScreen(navController = navController)
}
```

## 🔧 Repository Pattern

### Repository Template
```kotlin
@Singleton
class MyRepository @Inject constructor(
    private val myApi: MyApi,
    private val myDao: MyDao
) {
    // Get from local cache (Flow for reactive updates)
    fun getItems(): Flow<List<MyModel>> {
        return myDao.getAllItems().map { entities ->
            entities.map { MyMapper.fromEntity(it) }
        }
    }
    
    // Refresh from API
    suspend fun refreshItems(): Result<Unit> {
        return try {
            val response = myApi.getItems()
            if (response.isSuccessful && response.body() != null) {
                val items = response.body()!!
                val entities = items.map { MyMapper.dtoToEntity(it) }
                myDao.deleteAllItems()
                myDao.insertItems(entities)
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Create
    suspend fun createItem(dto: CreateItemDto): Result<MyModel> {
        return try {
            val response = myApi.createItem(dto)
            if (response.isSuccessful && response.body() != null) {
                val itemDto = response.body()!!
                val entity = MyMapper.dtoToEntity(itemDto)
                myDao.insertItem(entity)
                Result.success(MyMapper.fromEntity(entity))
            } else {
                Result.failure(Exception("Failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

## 🎨 UI State Pattern

```kotlin
data class MyUiState(
    val items: List<MyModel> = emptyList(),
    val isLoading: Boolean = false,
    val isRefreshing: Boolean = false,
    val error: String? = null,
    val selectedItem: MyModel? = null
)
```

## 🔄 API + DTO Pattern

### API Interface
```kotlin
interface MyApi {
    @GET("items")
    suspend fun getItems(): Response<List<MyDto>>
    
    @GET("items/{id}")
    suspend fun getItem(@Path("id") id: Int): Response<MyDto>
    
    @POST("items")
    suspend fun createItem(@Body item: CreateItemDto): Response<MyDto>
    
    @PUT("items/{id}")
    suspend fun updateItem(
        @Path("id") id: Int,
        @Body item: UpdateItemDto
    ): Response<MyDto>
    
    @DELETE("items/{id}")
    suspend fun deleteItem(@Path("id") id: Int): Response<Unit>
}
```

### DTO
```kotlin
data class MyDto(
    @SerializedName("id") val id: Int,
    @SerializedName("name") val name: String,
    @SerializedName("created_at") val createdAt: String
)

data class CreateItemDto(
    @SerializedName("name") val name: String
)

data class UpdateItemDto(
    @SerializedName("name") val name: String?
)
```

## 💾 Room Database Pattern

### Entity
```kotlin
@Entity(tableName = "items")
data class ItemEntity(
    @PrimaryKey val id: Int,
    val name: String,
    val createdAt: Long
)
```

### DAO
```kotlin
@Dao
interface ItemDao {
    @Query("SELECT * FROM items")
    fun getAllItems(): Flow<List<ItemEntity>>
    
    @Query("SELECT * FROM items WHERE id = :id")
    suspend fun getItemById(id: Int): ItemEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItem(item: ItemEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItems(items: List<ItemEntity>)
    
    @Update
    suspend fun updateItem(item: ItemEntity)
    
    @Delete
    suspend fun deleteItem(item: ItemEntity)
    
    @Query("DELETE FROM items")
    suspend fun deleteAllItems()
}
```

## 🗺️ Mapper Pattern

```kotlin
object MyMapper {
    // Entity -> Domain Model
    fun fromEntity(entity: ItemEntity): Item {
        return Item(
            id = entity.id,
            name = entity.name,
            createdAt = entity.createdAt
        )
    }
    
    // Domain Model -> Entity
    fun toEntity(item: Item): ItemEntity {
        return ItemEntity(
            id = item.id,
            name = item.name,
            createdAt = item.createdAt
        )
    }
    
    // DTO -> Domain Model
    fun fromDto(dto: ItemDto): Item {
        return Item(
            id = dto.id,
            name = dto.name,
            createdAt = dto.createdAt.toTimestamp()
        )
    }
    
    // DTO -> Entity (for cache)
    fun dtoToEntity(dto: ItemDto): ItemEntity {
        return ItemEntity(
            id = dto.id,
            name = dto.name,
            createdAt = dto.createdAt.toTimestamp()
        )
    }
}
```

## 📦 Use Case Pattern

```kotlin
class GetItemsUseCase @Inject constructor(
    private val repository: ItemRepository
) {
    operator fun invoke(): Flow<List<Item>> {
        return repository.getItems()
    }
}

class RefreshItemsUseCase @Inject constructor(
    private val repository: ItemRepository
) {
    suspend operator fun invoke(): Result<Unit> {
        return repository.refreshItems()
    }
}

class CreateItemUseCase @Inject constructor(
    private val repository: ItemRepository
) {
    suspend operator fun invoke(dto: CreateItemDto): Result<Item> {
        return repository.createItem(dto)
    }
}
```

## 🎯 Hilt DI Pattern

### AppModule hozzáadások
```kotlin
// API Provider
@Provides
@Singleton
fun provideMyApi(retrofit: Retrofit): MyApi {
    return retrofit.create(MyApi::class.java)
}

// DAO Provider
@Provides
@Singleton
fun provideMyDao(database: CMMSDatabase): MyDao {
    return database.myDao()
}

// Repository Provider
@Provides
@Singleton
fun provideMyRepository(
    myApi: MyApi,
    myDao: MyDao
): MyRepository {
    return MyRepository(myApi, myDao)
}
```

## 🎨 Compose UI Patterns

### Lista Screen Template
```kotlin
@Composable
fun ItemsListScreen(
    navController: NavController,
    viewModel: ItemsViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Items") },
                navigationIcon = { /* Back button */ },
                actions = { /* Refresh, Search */ }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* Navigate to create */ }) {
                Icon(Icons.Default.Add, "Add")
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(uiState.items) { item ->
                ItemCard(
                    item = item,
                    onClick = { /* Navigate to detail */ }
                )
            }
        }
    }
}
```

### Card Template
```kotlin
@Composable
fun ItemCard(
    item: Item,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = item.name,
                style = MaterialTheme.typography.titleMedium
            )
            Text(
                text = item.createdAt.toDateString(),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

## 🔍 Debugging Tips

### Logolás
```kotlin
// Timber használata
Timber.d("Debug message: $value")
Timber.e(exception, "Error occurred")
```

### Network Inspector
- Chucker automatikusan működik debug buildben
- Notification-ből nyitható meg
- Összes API hívás látható

### Database Inspector
- Android Studio -> View -> Tool Windows -> App Inspection
- Database Inspector tab
- Live adatok megtekintése

## 📱 Teszt Eszközök

### Emulator localhost
```kotlin
const val BASE_URL = "http://10.0.2.2:8000/api/"  // Emulator
```

### Fizikai eszköz
```kotlin
const val BASE_URL = "http://YOUR_IP:8000/api/"   // Fizikai eszköz
```

## ⚡ Gyakori Hibák & Megoldások

### Hilt injection error
- Ellenőrizd, hogy minden dependency provider definiálva van
- `@HiltAndroidApp` az Application osztályon
- `@AndroidEntryPoint` az Activity/Fragment-en
- `@HiltViewModel` a ViewModel-en

### Room migration error
- Növeld a version számot
- Adj hozzá Migration-t vagy használj `fallbackToDestructiveMigration()`

### Compose recomposition
- Használj `remember` változókhoz
- `LaunchedEffect` side effectekhez
- `derivedStateOf` számított értékekhez

---

**Utolsó frissítés:** 2025-01-14

