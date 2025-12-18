# Android Implementáció - TODO Lista

## 🎯 Prioritás 1: Alapvető Képernyők (MVP)

### ✅ Kész
- [x] Login Screen + ViewModel
- [x] Dashboard Screen + ViewModel
- [x] Assets Screen + ViewModel
- [x] Asset lista megjelenítés
- [x] SwipeRefresh
- [x] Offline cache (Assets)

### 🚧 Worksheets Screen
- [ ] WorksheetApi interface
- [ ] WorksheetDto-k (WorksheetDto, CreateWorksheetDto, UpdateWorksheetDto)
- [ ] WorksheetMapper
- [ ] WorksheetRepository kibővítése (CRUD + cache)
- [ ] Use Cases (GetWorksheetsUseCase, RefreshWorksheetsUseCase, stb.)
- [ ] WorksheetsViewModel
- [ ] WorksheetsScreen (lista nézet)
- [ ] WorksheetDetailScreen
- [ ] Navigation integráció

### 🚧 Machines Screen
- [ ] MachineApi interface
- [ ] MachineDto-k
- [ ] MachineMapper
- [ ] MachineRepository kibővítése
- [ ] Machine Use Cases
- [ ] MachinesViewModel
- [ ] MachinesScreen (lista nézet)
- [ ] MachineDetailScreen
- [ ] Production Line kapcsolat kezelése

### 🚧 Inventory Screen
- [ ] InventoryEntity + InventoryDao létrehozása
- [ ] Database frissítés (migration)
- [ ] InventoryApi interface
- [ ] InventoryDto-k
- [ ] InventoryMapper
- [ ] InventoryRepository
- [ ] Inventory Use Cases
- [ ] InventoryViewModel
- [ ] InventoryScreen
- [ ] Stock transaction kezelés

## 🎯 Prioritás 2: Detail Képernyők & CRUD

### AssetDetailScreen
- [ ] AssetDetailViewModel
- [ ] AssetDetailScreen composable
- [ ] View mode
- [ ] Edit mode
- [ ] Delete confirmation dialog
- [ ] Image display (ha van)
- [ ] CreateAssetUseCase
- [ ] UpdateAssetUseCase
- [ ] DeleteAssetUseCase

### WorksheetDetailScreen
- [ ] WorksheetDetailViewModel
- [ ] WorksheetDetailScreen
- [ ] Status változtatás
- [ ] Assigned user display
- [ ] Machine kapcsolat
- [ ] Comments/Notes
- [ ] Time tracking

### MachineDetailScreen
- [ ] MachineDetailViewModel
- [ ] MachineDetailScreen
- [ ] Maintenance history
- [ ] Linked worksheets
- [ ] QR code display

## 🎯 Prioritás 3: Egyéb Funkcionális Képernyők

### PM (Preventive Maintenance) Screen
- [ ] PMTaskEntity + PMTaskDao
- [ ] PMHistoryEntity + PMHistoryDao
- [ ] PMApi interface
- [ ] PM DTOs és Mappers
- [ ] PMRepository
- [ ] PM Use Cases
- [ ] PMViewModel
- [ ] PMScreen (schedule lista)
- [ ] PM task completion flow

### Reports Screen
- [ ] ReportsViewModel
- [ ] ReportsScreen
- [ ] Report típusok listája
- [ ] Chart library integráció
- [ ] PDF export (később)
- [ ] Filter opciók
- [ ] Date range picker

### Users Screen (Admin)
- [ ] UsersViewModel
- [ ] UsersScreen (csak admin role-nak)
- [ ] User CRUD (ha admin)
- [ ] Role management
- [ ] User detail view

### Settings Screen
- [ ] SettingsViewModel
- [ ] SettingsScreen
- [ ] Profile szerkesztés
- [ ] Nyelv váltás
- [ ] Theme váltás (Dark mode)
- [ ] Notification settings
- [ ] About section
- [ ] Logout

## 🎯 Prioritás 4: Közös UI Komponensek

### Komponensek
- [ ] LoadingIndicator composable
- [ ] EmptyState composable
- [ ] ErrorState composable
- [ ] ConfirmDialog composable
- [ ] FilterDialog composable
- [ ] DatePickerDialog composable
- [ ] ImagePicker composable
- [ ] QRCodeScanner composable
- [ ] BottomSheet komponensek

### Top App Bar
- [ ] CMMSTopAppBar composable
- [ ] Search bar variáns
- [ ] Filter button
- [ ] Overflow menu

## 🎯 Prioritás 5: Backend Integráció

### API Integrációk
- [ ] Összes API interface implementálása
- [ ] UserApi
- [ ] ProductionLineApi
- [ ] PMApi
- [ ] ReportsApi
- [ ] AuthInterceptor token automatikus hozzáadás
- [ ] Token refresh mechanizmus
- [ ] Error response handling

### DTOs
- [ ] UserDto, CreateUserDto, UpdateUserDto
- [ ] MachineDto, CreateMachineDto, UpdateMachineDto
- [ ] Összes többi DTO

### Repository-k
- [ ] UserRepository teljes implementáció
- [ ] MachineRepository teljes implementáció
- [ ] WorksheetRepository teljes implementáció
- [ ] PMRepository
- [ ] ReportsRepository

## 🎯 Prioritás 6: Offline Működés & Szinkronizáció

### Sync
- [ ] SyncWorker létrehozása (WorkManager)
- [ ] Periodic sync setup (15 perc)
- [ ] Manual sync trigger
- [ ] Conflict resolution stratégia
- [ ] Last sync timestamp tárolás
- [ ] Sync status indicator

### Offline Support
- [ ] Network state monitoring
- [ ] Offline mode indicator
- [ ] Pending operations queue
- [ ] Offline creation/update support
- [ ] Sync on network available

## 🎯 Prioritás 7: Advanced Features

### QR/Barcode
- [ ] ML Kit Barcode Scanning library integráció
- [ ] QR Scanner composable
- [ ] Asset QR code generation
- [ ] Machine QR code scanning
- [ ] Barcode to asset linking

### Image Handling
- [ ] Camera capture integration
- [ ] Image picker from gallery
- [ ] Image compression
- [ ] Image upload API
- [ ] Image cache management
- [ ] Image viewer

### Notifications
- [ ] Firebase Cloud Messaging setup
- [ ] Notification handling
- [ ] Notification permissions
- [ ] Push notification display
- [ ] Notification click handling

## 🎯 Prioritás 8: UI/UX Fejlesztések

### Dark Mode
- [ ] Dark color scheme definíció
- [ ] Theme switcher
- [ ] System theme követés
- [ ] Preference tárolás

### Animations
- [ ] Screen transitions
- [ ] Loading animations
- [ ] Success/Error animations
- [ ] Pull-to-refresh animation
- [ ] List item animations

### Accessibility
- [ ] Content descriptions
- [ ] Screen reader support
- [ ] Touch target sizes
- [ ] Color contrast check
- [ ] Font scaling support

## 🎯 Prioritás 9: Testing

### Unit Tests
- [ ] ViewModel tesztek (minden screen)
- [ ] Repository tesztek
- [ ] Use Case tesztek
- [ ] Mapper tesztek
- [ ] Extension funkció tesztek

### Integration Tests
- [ ] API integration tesztek
- [ ] Database operation tesztek
- [ ] Repository integration tesztek

### UI Tests
- [ ] Login flow teszt
- [ ] Navigation flow teszt
- [ ] CRUD operation tesztek
- [ ] Error state tesztek

## 🎯 Prioritás 10: Dokumentáció & Cleanup

### Dokumentáció
- [ ] Kód kommentek
- [ ] KDoc dokumentáció
- [ ] API használati példák
- [ ] Architecture decision records
- [ ] User manual

### Code Cleanup
- [ ] Unused imports cleanup
- [ ] Code formatting (ktlint)
- [ ] Warning-ok javítása
- [ ] TODO kommentek átnézése
- [ ] Performance optimalizálás

### Build & Release
- [ ] ProGuard rules
- [ ] Release build testing
- [ ] APK size optimalizálás
- [ ] Version code & name setup
- [ ] Signing configuration

## 📊 Előrehaladás

- **Kész:** ~60% ✅🎉
- **Folyamatban:** Machines Screen befejezve!
- **Következő:** Inventory Screen vagy Detail Screen-ek
- **Becsült MVP befejezés:** 1 hét

---

**Utolsó frissítés:** 2025-01-14  
**Státusz:** 🚀 Aktív fejlesztés

