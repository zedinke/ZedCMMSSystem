package com.artence.cmms.data.local.database;

import androidx.annotation.NonNull;
import androidx.room.DatabaseConfiguration;
import androidx.room.InvalidationTracker;
import androidx.room.RoomDatabase;
import androidx.room.RoomOpenHelper;
import androidx.room.migration.AutoMigrationSpec;
import androidx.room.migration.Migration;
import androidx.room.util.DBUtil;
import androidx.room.util.TableInfo;
import androidx.sqlite.db.SupportSQLiteDatabase;
import androidx.sqlite.db.SupportSQLiteOpenHelper;
import com.artence.cmms.data.local.database.dao.AssetDao;
import com.artence.cmms.data.local.database.dao.AssetDao_Impl;
import com.artence.cmms.data.local.database.dao.InventoryDao;
import com.artence.cmms.data.local.database.dao.InventoryDao_Impl;
import com.artence.cmms.data.local.database.dao.MachineDao;
import com.artence.cmms.data.local.database.dao.MachineDao_Impl;
import com.artence.cmms.data.local.database.dao.PMTaskDao;
import com.artence.cmms.data.local.database.dao.PMTaskDao_Impl;
import com.artence.cmms.data.local.database.dao.UserDao;
import com.artence.cmms.data.local.database.dao.UserDao_Impl;
import com.artence.cmms.data.local.database.dao.WorksheetDao;
import com.artence.cmms.data.local.database.dao.WorksheetDao_Impl;
import java.lang.Class;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.processing.Generated;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class CMMSDatabase_Impl extends CMMSDatabase {
  private volatile UserDao _userDao;

  private volatile MachineDao _machineDao;

  private volatile WorksheetDao _worksheetDao;

  private volatile AssetDao _assetDao;

  private volatile InventoryDao _inventoryDao;

  private volatile PMTaskDao _pMTaskDao;

  @Override
  @NonNull
  protected SupportSQLiteOpenHelper createOpenHelper(@NonNull final DatabaseConfiguration config) {
    final SupportSQLiteOpenHelper.Callback _openCallback = new RoomOpenHelper(config, new RoomOpenHelper.Delegate(1) {
      @Override
      public void createAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER NOT NULL, `username` TEXT NOT NULL, `email` TEXT, `fullName` TEXT, `phone` TEXT, `roleId` INTEGER NOT NULL, `isActive` INTEGER NOT NULL, `languagePreference` TEXT NOT NULL, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER, PRIMARY KEY(`id`))");
        db.execSQL("CREATE TABLE IF NOT EXISTS `machines` (`id` INTEGER NOT NULL, `productionLineId` INTEGER NOT NULL, `name` TEXT NOT NULL, `serialNumber` TEXT, `model` TEXT, `manufacturer` TEXT, `status` TEXT NOT NULL, `assetTag` TEXT, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER, PRIMARY KEY(`id`))");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_machines_status` ON `machines` (`status`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_machines_productionLineId` ON `machines` (`productionLineId`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `worksheets` (`id` INTEGER NOT NULL, `machineId` INTEGER, `assignedToUserId` INTEGER, `title` TEXT NOT NULL, `description` TEXT, `status` TEXT NOT NULL, `priority` TEXT, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER, PRIMARY KEY(`id`))");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_worksheets_status` ON `worksheets` (`status`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_worksheets_priority` ON `worksheets` (`priority`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_worksheets_machineId` ON `worksheets` (`machineId`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `assets` (`id` INTEGER NOT NULL, `name` TEXT NOT NULL, `category` TEXT, `assetTag` TEXT, `serialNumber` TEXT, `manufacturer` TEXT, `model` TEXT, `location` TEXT, `status` TEXT NOT NULL, `purchaseDate` INTEGER, `purchasePrice` REAL, `warrantyExpiry` INTEGER, `description` TEXT, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER, PRIMARY KEY(`id`))");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_assets_status` ON `assets` (`status`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_assets_name` ON `assets` (`name`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_assets_assetTag` ON `assets` (`assetTag`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `inventory` (`id` INTEGER NOT NULL, `partId` INTEGER, `assetId` INTEGER, `quantity` INTEGER NOT NULL, `minQuantity` INTEGER NOT NULL, `maxQuantity` INTEGER NOT NULL, `location` TEXT, `lastUpdated` INTEGER NOT NULL, `createdAt` INTEGER NOT NULL, PRIMARY KEY(`id`))");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_inventory_location` ON `inventory` (`location`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS `pm_tasks` (`id` INTEGER NOT NULL, `machineId` INTEGER NOT NULL, `machineName` TEXT, `taskName` TEXT NOT NULL, `description` TEXT, `frequency` TEXT NOT NULL, `lastExecuted` INTEGER, `nextScheduled` INTEGER NOT NULL, `status` TEXT NOT NULL, `assignedToUserId` INTEGER, `assignedToUsername` TEXT, `priority` TEXT, `estimatedDuration` INTEGER, `createdAt` INTEGER NOT NULL, `updatedAt` INTEGER, PRIMARY KEY(`id`))");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_pm_tasks_status` ON `pm_tasks` (`status`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_pm_tasks_machineId` ON `pm_tasks` (`machineId`)");
        db.execSQL("CREATE INDEX IF NOT EXISTS `index_pm_tasks_nextScheduled` ON `pm_tasks` (`nextScheduled`)");
        db.execSQL("CREATE TABLE IF NOT EXISTS room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)");
        db.execSQL("INSERT OR REPLACE INTO room_master_table (id,identity_hash) VALUES(42, 'b44136155c7efbab874dd2700b7fd617')");
      }

      @Override
      public void dropAllTables(@NonNull final SupportSQLiteDatabase db) {
        db.execSQL("DROP TABLE IF EXISTS `users`");
        db.execSQL("DROP TABLE IF EXISTS `machines`");
        db.execSQL("DROP TABLE IF EXISTS `worksheets`");
        db.execSQL("DROP TABLE IF EXISTS `assets`");
        db.execSQL("DROP TABLE IF EXISTS `inventory`");
        db.execSQL("DROP TABLE IF EXISTS `pm_tasks`");
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onDestructiveMigration(db);
          }
        }
      }

      @Override
      public void onCreate(@NonNull final SupportSQLiteDatabase db) {
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onCreate(db);
          }
        }
      }

      @Override
      public void onOpen(@NonNull final SupportSQLiteDatabase db) {
        mDatabase = db;
        internalInitInvalidationTracker(db);
        final List<? extends RoomDatabase.Callback> _callbacks = mCallbacks;
        if (_callbacks != null) {
          for (RoomDatabase.Callback _callback : _callbacks) {
            _callback.onOpen(db);
          }
        }
      }

      @Override
      public void onPreMigrate(@NonNull final SupportSQLiteDatabase db) {
        DBUtil.dropFtsSyncTriggers(db);
      }

      @Override
      public void onPostMigrate(@NonNull final SupportSQLiteDatabase db) {
      }

      @Override
      @NonNull
      public RoomOpenHelper.ValidationResult onValidateSchema(
          @NonNull final SupportSQLiteDatabase db) {
        final HashMap<String, TableInfo.Column> _columnsUsers = new HashMap<String, TableInfo.Column>(10);
        _columnsUsers.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("username", new TableInfo.Column("username", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("email", new TableInfo.Column("email", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("fullName", new TableInfo.Column("fullName", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("phone", new TableInfo.Column("phone", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("roleId", new TableInfo.Column("roleId", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("isActive", new TableInfo.Column("isActive", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("languagePreference", new TableInfo.Column("languagePreference", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsUsers.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysUsers = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesUsers = new HashSet<TableInfo.Index>(0);
        final TableInfo _infoUsers = new TableInfo("users", _columnsUsers, _foreignKeysUsers, _indicesUsers);
        final TableInfo _existingUsers = TableInfo.read(db, "users");
        if (!_infoUsers.equals(_existingUsers)) {
          return new RoomOpenHelper.ValidationResult(false, "users(com.artence.cmms.data.local.database.entities.UserEntity).\n"
                  + " Expected:\n" + _infoUsers + "\n"
                  + " Found:\n" + _existingUsers);
        }
        final HashMap<String, TableInfo.Column> _columnsMachines = new HashMap<String, TableInfo.Column>(10);
        _columnsMachines.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("productionLineId", new TableInfo.Column("productionLineId", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("serialNumber", new TableInfo.Column("serialNumber", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("model", new TableInfo.Column("model", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("manufacturer", new TableInfo.Column("manufacturer", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("status", new TableInfo.Column("status", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("assetTag", new TableInfo.Column("assetTag", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsMachines.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysMachines = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesMachines = new HashSet<TableInfo.Index>(2);
        _indicesMachines.add(new TableInfo.Index("index_machines_status", false, Arrays.asList("status"), Arrays.asList("ASC")));
        _indicesMachines.add(new TableInfo.Index("index_machines_productionLineId", false, Arrays.asList("productionLineId"), Arrays.asList("ASC")));
        final TableInfo _infoMachines = new TableInfo("machines", _columnsMachines, _foreignKeysMachines, _indicesMachines);
        final TableInfo _existingMachines = TableInfo.read(db, "machines");
        if (!_infoMachines.equals(_existingMachines)) {
          return new RoomOpenHelper.ValidationResult(false, "machines(com.artence.cmms.data.local.database.entities.MachineEntity).\n"
                  + " Expected:\n" + _infoMachines + "\n"
                  + " Found:\n" + _existingMachines);
        }
        final HashMap<String, TableInfo.Column> _columnsWorksheets = new HashMap<String, TableInfo.Column>(9);
        _columnsWorksheets.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("machineId", new TableInfo.Column("machineId", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("assignedToUserId", new TableInfo.Column("assignedToUserId", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("title", new TableInfo.Column("title", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("description", new TableInfo.Column("description", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("status", new TableInfo.Column("status", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("priority", new TableInfo.Column("priority", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsWorksheets.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysWorksheets = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesWorksheets = new HashSet<TableInfo.Index>(3);
        _indicesWorksheets.add(new TableInfo.Index("index_worksheets_status", false, Arrays.asList("status"), Arrays.asList("ASC")));
        _indicesWorksheets.add(new TableInfo.Index("index_worksheets_priority", false, Arrays.asList("priority"), Arrays.asList("ASC")));
        _indicesWorksheets.add(new TableInfo.Index("index_worksheets_machineId", false, Arrays.asList("machineId"), Arrays.asList("ASC")));
        final TableInfo _infoWorksheets = new TableInfo("worksheets", _columnsWorksheets, _foreignKeysWorksheets, _indicesWorksheets);
        final TableInfo _existingWorksheets = TableInfo.read(db, "worksheets");
        if (!_infoWorksheets.equals(_existingWorksheets)) {
          return new RoomOpenHelper.ValidationResult(false, "worksheets(com.artence.cmms.data.local.database.entities.WorksheetEntity).\n"
                  + " Expected:\n" + _infoWorksheets + "\n"
                  + " Found:\n" + _existingWorksheets);
        }
        final HashMap<String, TableInfo.Column> _columnsAssets = new HashMap<String, TableInfo.Column>(15);
        _columnsAssets.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("name", new TableInfo.Column("name", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("category", new TableInfo.Column("category", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("assetTag", new TableInfo.Column("assetTag", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("serialNumber", new TableInfo.Column("serialNumber", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("manufacturer", new TableInfo.Column("manufacturer", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("model", new TableInfo.Column("model", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("location", new TableInfo.Column("location", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("status", new TableInfo.Column("status", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("purchaseDate", new TableInfo.Column("purchaseDate", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("purchasePrice", new TableInfo.Column("purchasePrice", "REAL", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("warrantyExpiry", new TableInfo.Column("warrantyExpiry", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("description", new TableInfo.Column("description", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsAssets.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysAssets = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesAssets = new HashSet<TableInfo.Index>(3);
        _indicesAssets.add(new TableInfo.Index("index_assets_status", false, Arrays.asList("status"), Arrays.asList("ASC")));
        _indicesAssets.add(new TableInfo.Index("index_assets_name", false, Arrays.asList("name"), Arrays.asList("ASC")));
        _indicesAssets.add(new TableInfo.Index("index_assets_assetTag", false, Arrays.asList("assetTag"), Arrays.asList("ASC")));
        final TableInfo _infoAssets = new TableInfo("assets", _columnsAssets, _foreignKeysAssets, _indicesAssets);
        final TableInfo _existingAssets = TableInfo.read(db, "assets");
        if (!_infoAssets.equals(_existingAssets)) {
          return new RoomOpenHelper.ValidationResult(false, "assets(com.artence.cmms.data.local.database.entities.AssetEntity).\n"
                  + " Expected:\n" + _infoAssets + "\n"
                  + " Found:\n" + _existingAssets);
        }
        final HashMap<String, TableInfo.Column> _columnsInventory = new HashMap<String, TableInfo.Column>(9);
        _columnsInventory.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("partId", new TableInfo.Column("partId", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("assetId", new TableInfo.Column("assetId", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("quantity", new TableInfo.Column("quantity", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("minQuantity", new TableInfo.Column("minQuantity", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("maxQuantity", new TableInfo.Column("maxQuantity", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("location", new TableInfo.Column("location", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("lastUpdated", new TableInfo.Column("lastUpdated", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsInventory.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysInventory = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesInventory = new HashSet<TableInfo.Index>(1);
        _indicesInventory.add(new TableInfo.Index("index_inventory_location", false, Arrays.asList("location"), Arrays.asList("ASC")));
        final TableInfo _infoInventory = new TableInfo("inventory", _columnsInventory, _foreignKeysInventory, _indicesInventory);
        final TableInfo _existingInventory = TableInfo.read(db, "inventory");
        if (!_infoInventory.equals(_existingInventory)) {
          return new RoomOpenHelper.ValidationResult(false, "inventory(com.artence.cmms.data.local.database.entities.InventoryEntity).\n"
                  + " Expected:\n" + _infoInventory + "\n"
                  + " Found:\n" + _existingInventory);
        }
        final HashMap<String, TableInfo.Column> _columnsPmTasks = new HashMap<String, TableInfo.Column>(15);
        _columnsPmTasks.put("id", new TableInfo.Column("id", "INTEGER", true, 1, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("machineId", new TableInfo.Column("machineId", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("machineName", new TableInfo.Column("machineName", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("taskName", new TableInfo.Column("taskName", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("description", new TableInfo.Column("description", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("frequency", new TableInfo.Column("frequency", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("lastExecuted", new TableInfo.Column("lastExecuted", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("nextScheduled", new TableInfo.Column("nextScheduled", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("status", new TableInfo.Column("status", "TEXT", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("assignedToUserId", new TableInfo.Column("assignedToUserId", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("assignedToUsername", new TableInfo.Column("assignedToUsername", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("priority", new TableInfo.Column("priority", "TEXT", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("estimatedDuration", new TableInfo.Column("estimatedDuration", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("createdAt", new TableInfo.Column("createdAt", "INTEGER", true, 0, null, TableInfo.CREATED_FROM_ENTITY));
        _columnsPmTasks.put("updatedAt", new TableInfo.Column("updatedAt", "INTEGER", false, 0, null, TableInfo.CREATED_FROM_ENTITY));
        final HashSet<TableInfo.ForeignKey> _foreignKeysPmTasks = new HashSet<TableInfo.ForeignKey>(0);
        final HashSet<TableInfo.Index> _indicesPmTasks = new HashSet<TableInfo.Index>(3);
        _indicesPmTasks.add(new TableInfo.Index("index_pm_tasks_status", false, Arrays.asList("status"), Arrays.asList("ASC")));
        _indicesPmTasks.add(new TableInfo.Index("index_pm_tasks_machineId", false, Arrays.asList("machineId"), Arrays.asList("ASC")));
        _indicesPmTasks.add(new TableInfo.Index("index_pm_tasks_nextScheduled", false, Arrays.asList("nextScheduled"), Arrays.asList("ASC")));
        final TableInfo _infoPmTasks = new TableInfo("pm_tasks", _columnsPmTasks, _foreignKeysPmTasks, _indicesPmTasks);
        final TableInfo _existingPmTasks = TableInfo.read(db, "pm_tasks");
        if (!_infoPmTasks.equals(_existingPmTasks)) {
          return new RoomOpenHelper.ValidationResult(false, "pm_tasks(com.artence.cmms.data.local.database.entities.PMTaskEntity).\n"
                  + " Expected:\n" + _infoPmTasks + "\n"
                  + " Found:\n" + _existingPmTasks);
        }
        return new RoomOpenHelper.ValidationResult(true, null);
      }
    }, "b44136155c7efbab874dd2700b7fd617", "33e1238724652532936af98af5440e28");
    final SupportSQLiteOpenHelper.Configuration _sqliteConfig = SupportSQLiteOpenHelper.Configuration.builder(config.context).name(config.name).callback(_openCallback).build();
    final SupportSQLiteOpenHelper _helper = config.sqliteOpenHelperFactory.create(_sqliteConfig);
    return _helper;
  }

  @Override
  @NonNull
  protected InvalidationTracker createInvalidationTracker() {
    final HashMap<String, String> _shadowTablesMap = new HashMap<String, String>(0);
    final HashMap<String, Set<String>> _viewTables = new HashMap<String, Set<String>>(0);
    return new InvalidationTracker(this, _shadowTablesMap, _viewTables, "users","machines","worksheets","assets","inventory","pm_tasks");
  }

  @Override
  public void clearAllTables() {
    super.assertNotMainThread();
    final SupportSQLiteDatabase _db = super.getOpenHelper().getWritableDatabase();
    try {
      super.beginTransaction();
      _db.execSQL("DELETE FROM `users`");
      _db.execSQL("DELETE FROM `machines`");
      _db.execSQL("DELETE FROM `worksheets`");
      _db.execSQL("DELETE FROM `assets`");
      _db.execSQL("DELETE FROM `inventory`");
      _db.execSQL("DELETE FROM `pm_tasks`");
      super.setTransactionSuccessful();
    } finally {
      super.endTransaction();
      _db.query("PRAGMA wal_checkpoint(FULL)").close();
      if (!_db.inTransaction()) {
        _db.execSQL("VACUUM");
      }
    }
  }

  @Override
  @NonNull
  protected Map<Class<?>, List<Class<?>>> getRequiredTypeConverters() {
    final HashMap<Class<?>, List<Class<?>>> _typeConvertersMap = new HashMap<Class<?>, List<Class<?>>>();
    _typeConvertersMap.put(UserDao.class, UserDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(MachineDao.class, MachineDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(WorksheetDao.class, WorksheetDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(AssetDao.class, AssetDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(InventoryDao.class, InventoryDao_Impl.getRequiredConverters());
    _typeConvertersMap.put(PMTaskDao.class, PMTaskDao_Impl.getRequiredConverters());
    return _typeConvertersMap;
  }

  @Override
  @NonNull
  public Set<Class<? extends AutoMigrationSpec>> getRequiredAutoMigrationSpecs() {
    final HashSet<Class<? extends AutoMigrationSpec>> _autoMigrationSpecsSet = new HashSet<Class<? extends AutoMigrationSpec>>();
    return _autoMigrationSpecsSet;
  }

  @Override
  @NonNull
  public List<Migration> getAutoMigrations(
      @NonNull final Map<Class<? extends AutoMigrationSpec>, AutoMigrationSpec> autoMigrationSpecs) {
    final List<Migration> _autoMigrations = new ArrayList<Migration>();
    return _autoMigrations;
  }

  @Override
  public UserDao userDao() {
    if (_userDao != null) {
      return _userDao;
    } else {
      synchronized(this) {
        if(_userDao == null) {
          _userDao = new UserDao_Impl(this);
        }
        return _userDao;
      }
    }
  }

  @Override
  public MachineDao machineDao() {
    if (_machineDao != null) {
      return _machineDao;
    } else {
      synchronized(this) {
        if(_machineDao == null) {
          _machineDao = new MachineDao_Impl(this);
        }
        return _machineDao;
      }
    }
  }

  @Override
  public WorksheetDao worksheetDao() {
    if (_worksheetDao != null) {
      return _worksheetDao;
    } else {
      synchronized(this) {
        if(_worksheetDao == null) {
          _worksheetDao = new WorksheetDao_Impl(this);
        }
        return _worksheetDao;
      }
    }
  }

  @Override
  public AssetDao assetDao() {
    if (_assetDao != null) {
      return _assetDao;
    } else {
      synchronized(this) {
        if(_assetDao == null) {
          _assetDao = new AssetDao_Impl(this);
        }
        return _assetDao;
      }
    }
  }

  @Override
  public InventoryDao inventoryDao() {
    if (_inventoryDao != null) {
      return _inventoryDao;
    } else {
      synchronized(this) {
        if(_inventoryDao == null) {
          _inventoryDao = new InventoryDao_Impl(this);
        }
        return _inventoryDao;
      }
    }
  }

  @Override
  public PMTaskDao pmTaskDao() {
    if (_pMTaskDao != null) {
      return _pMTaskDao;
    } else {
      synchronized(this) {
        if(_pMTaskDao == null) {
          _pMTaskDao = new PMTaskDao_Impl(this);
        }
        return _pMTaskDao;
      }
    }
  }
}
