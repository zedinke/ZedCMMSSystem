package com.artence.cmms.data.local.database.dao;

import android.database.Cursor;
import android.os.CancellationSignal;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.room.CoroutinesRoom;
import androidx.room.EntityDeletionOrUpdateAdapter;
import androidx.room.EntityInsertionAdapter;
import androidx.room.RoomDatabase;
import androidx.room.RoomSQLiteQuery;
import androidx.room.SharedSQLiteStatement;
import androidx.room.util.CursorUtil;
import androidx.room.util.DBUtil;
import androidx.sqlite.db.SupportSQLiteStatement;
import com.artence.cmms.data.local.database.entities.InventoryEntity;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Integer;
import java.lang.Object;
import java.lang.Override;
import java.lang.String;
import java.lang.SuppressWarnings;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Callable;
import javax.annotation.processing.Generated;
import kotlin.Unit;
import kotlin.coroutines.Continuation;
import kotlinx.coroutines.flow.Flow;

@Generated("androidx.room.RoomProcessor")
@SuppressWarnings({"unchecked", "deprecation"})
public final class InventoryDao_Impl implements InventoryDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<InventoryEntity> __insertionAdapterOfInventoryEntity;

  private final EntityDeletionOrUpdateAdapter<InventoryEntity> __deletionAdapterOfInventoryEntity;

  private final EntityDeletionOrUpdateAdapter<InventoryEntity> __updateAdapterOfInventoryEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllInventory;

  public InventoryDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfInventoryEntity = new EntityInsertionAdapter<InventoryEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `inventory` (`id`,`partId`,`assetId`,`quantity`,`minQuantity`,`maxQuantity`,`location`,`lastUpdated`,`createdAt`) VALUES (?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final InventoryEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getPartId() == null) {
          statement.bindNull(2);
        } else {
          statement.bindLong(2, entity.getPartId());
        }
        if (entity.getAssetId() == null) {
          statement.bindNull(3);
        } else {
          statement.bindLong(3, entity.getAssetId());
        }
        statement.bindLong(4, entity.getQuantity());
        statement.bindLong(5, entity.getMinQuantity());
        statement.bindLong(6, entity.getMaxQuantity());
        if (entity.getLocation() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getLocation());
        }
        statement.bindLong(8, entity.getLastUpdated());
        statement.bindLong(9, entity.getCreatedAt());
      }
    };
    this.__deletionAdapterOfInventoryEntity = new EntityDeletionOrUpdateAdapter<InventoryEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `inventory` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final InventoryEntity entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfInventoryEntity = new EntityDeletionOrUpdateAdapter<InventoryEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `inventory` SET `id` = ?,`partId` = ?,`assetId` = ?,`quantity` = ?,`minQuantity` = ?,`maxQuantity` = ?,`location` = ?,`lastUpdated` = ?,`createdAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final InventoryEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getPartId() == null) {
          statement.bindNull(2);
        } else {
          statement.bindLong(2, entity.getPartId());
        }
        if (entity.getAssetId() == null) {
          statement.bindNull(3);
        } else {
          statement.bindLong(3, entity.getAssetId());
        }
        statement.bindLong(4, entity.getQuantity());
        statement.bindLong(5, entity.getMinQuantity());
        statement.bindLong(6, entity.getMaxQuantity());
        if (entity.getLocation() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getLocation());
        }
        statement.bindLong(8, entity.getLastUpdated());
        statement.bindLong(9, entity.getCreatedAt());
        statement.bindLong(10, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAllInventory = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM inventory";
        return _query;
      }
    };
  }

  @Override
  public Object insertInventory(final InventoryEntity inventory,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfInventoryEntity.insert(inventory);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertInventoryList(final List<InventoryEntity> inventoryList,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfInventoryEntity.insert(inventoryList);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteInventory(final InventoryEntity inventory,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfInventoryEntity.handle(inventory);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateInventory(final InventoryEntity inventory,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfInventoryEntity.handle(inventory);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllInventory(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllInventory.acquire();
        try {
          __db.beginTransaction();
          try {
            _stmt.executeUpdateDelete();
            __db.setTransactionSuccessful();
            return Unit.INSTANCE;
          } finally {
            __db.endTransaction();
          }
        } finally {
          __preparedStmtOfDeleteAllInventory.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<InventoryEntity>> getAllInventory() {
    final String _sql = "SELECT * FROM inventory";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"inventory"}, new Callable<List<InventoryEntity>>() {
      @Override
      @NonNull
      public List<InventoryEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPartId = CursorUtil.getColumnIndexOrThrow(_cursor, "partId");
          final int _cursorIndexOfAssetId = CursorUtil.getColumnIndexOrThrow(_cursor, "assetId");
          final int _cursorIndexOfQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "quantity");
          final int _cursorIndexOfMinQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "minQuantity");
          final int _cursorIndexOfMaxQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "maxQuantity");
          final int _cursorIndexOfLocation = CursorUtil.getColumnIndexOrThrow(_cursor, "location");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final List<InventoryEntity> _result = new ArrayList<InventoryEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final InventoryEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final Integer _tmpPartId;
            if (_cursor.isNull(_cursorIndexOfPartId)) {
              _tmpPartId = null;
            } else {
              _tmpPartId = _cursor.getInt(_cursorIndexOfPartId);
            }
            final Integer _tmpAssetId;
            if (_cursor.isNull(_cursorIndexOfAssetId)) {
              _tmpAssetId = null;
            } else {
              _tmpAssetId = _cursor.getInt(_cursorIndexOfAssetId);
            }
            final int _tmpQuantity;
            _tmpQuantity = _cursor.getInt(_cursorIndexOfQuantity);
            final int _tmpMinQuantity;
            _tmpMinQuantity = _cursor.getInt(_cursorIndexOfMinQuantity);
            final int _tmpMaxQuantity;
            _tmpMaxQuantity = _cursor.getInt(_cursorIndexOfMaxQuantity);
            final String _tmpLocation;
            if (_cursor.isNull(_cursorIndexOfLocation)) {
              _tmpLocation = null;
            } else {
              _tmpLocation = _cursor.getString(_cursorIndexOfLocation);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            _item = new InventoryEntity(_tmpId,_tmpPartId,_tmpAssetId,_tmpQuantity,_tmpMinQuantity,_tmpMaxQuantity,_tmpLocation,_tmpLastUpdated,_tmpCreatedAt);
            _result.add(_item);
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @Override
  public Object getInventoryById(final int id,
      final Continuation<? super InventoryEntity> $completion) {
    final String _sql = "SELECT * FROM inventory WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, id);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<InventoryEntity>() {
      @Override
      @Nullable
      public InventoryEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPartId = CursorUtil.getColumnIndexOrThrow(_cursor, "partId");
          final int _cursorIndexOfAssetId = CursorUtil.getColumnIndexOrThrow(_cursor, "assetId");
          final int _cursorIndexOfQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "quantity");
          final int _cursorIndexOfMinQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "minQuantity");
          final int _cursorIndexOfMaxQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "maxQuantity");
          final int _cursorIndexOfLocation = CursorUtil.getColumnIndexOrThrow(_cursor, "location");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final InventoryEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final Integer _tmpPartId;
            if (_cursor.isNull(_cursorIndexOfPartId)) {
              _tmpPartId = null;
            } else {
              _tmpPartId = _cursor.getInt(_cursorIndexOfPartId);
            }
            final Integer _tmpAssetId;
            if (_cursor.isNull(_cursorIndexOfAssetId)) {
              _tmpAssetId = null;
            } else {
              _tmpAssetId = _cursor.getInt(_cursorIndexOfAssetId);
            }
            final int _tmpQuantity;
            _tmpQuantity = _cursor.getInt(_cursorIndexOfQuantity);
            final int _tmpMinQuantity;
            _tmpMinQuantity = _cursor.getInt(_cursorIndexOfMinQuantity);
            final int _tmpMaxQuantity;
            _tmpMaxQuantity = _cursor.getInt(_cursorIndexOfMaxQuantity);
            final String _tmpLocation;
            if (_cursor.isNull(_cursorIndexOfLocation)) {
              _tmpLocation = null;
            } else {
              _tmpLocation = _cursor.getString(_cursorIndexOfLocation);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            _result = new InventoryEntity(_tmpId,_tmpPartId,_tmpAssetId,_tmpQuantity,_tmpMinQuantity,_tmpMaxQuantity,_tmpLocation,_tmpLastUpdated,_tmpCreatedAt);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
          _statement.release();
        }
      }
    }, $completion);
  }

  @Override
  public Flow<InventoryEntity> getInventoryByAssetId(final int assetId) {
    final String _sql = "SELECT * FROM inventory WHERE assetId = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, assetId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"inventory"}, new Callable<InventoryEntity>() {
      @Override
      @Nullable
      public InventoryEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfPartId = CursorUtil.getColumnIndexOrThrow(_cursor, "partId");
          final int _cursorIndexOfAssetId = CursorUtil.getColumnIndexOrThrow(_cursor, "assetId");
          final int _cursorIndexOfQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "quantity");
          final int _cursorIndexOfMinQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "minQuantity");
          final int _cursorIndexOfMaxQuantity = CursorUtil.getColumnIndexOrThrow(_cursor, "maxQuantity");
          final int _cursorIndexOfLocation = CursorUtil.getColumnIndexOrThrow(_cursor, "location");
          final int _cursorIndexOfLastUpdated = CursorUtil.getColumnIndexOrThrow(_cursor, "lastUpdated");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final InventoryEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final Integer _tmpPartId;
            if (_cursor.isNull(_cursorIndexOfPartId)) {
              _tmpPartId = null;
            } else {
              _tmpPartId = _cursor.getInt(_cursorIndexOfPartId);
            }
            final Integer _tmpAssetId;
            if (_cursor.isNull(_cursorIndexOfAssetId)) {
              _tmpAssetId = null;
            } else {
              _tmpAssetId = _cursor.getInt(_cursorIndexOfAssetId);
            }
            final int _tmpQuantity;
            _tmpQuantity = _cursor.getInt(_cursorIndexOfQuantity);
            final int _tmpMinQuantity;
            _tmpMinQuantity = _cursor.getInt(_cursorIndexOfMinQuantity);
            final int _tmpMaxQuantity;
            _tmpMaxQuantity = _cursor.getInt(_cursorIndexOfMaxQuantity);
            final String _tmpLocation;
            if (_cursor.isNull(_cursorIndexOfLocation)) {
              _tmpLocation = null;
            } else {
              _tmpLocation = _cursor.getString(_cursorIndexOfLocation);
            }
            final long _tmpLastUpdated;
            _tmpLastUpdated = _cursor.getLong(_cursorIndexOfLastUpdated);
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            _result = new InventoryEntity(_tmpId,_tmpPartId,_tmpAssetId,_tmpQuantity,_tmpMinQuantity,_tmpMaxQuantity,_tmpLocation,_tmpLastUpdated,_tmpCreatedAt);
          } else {
            _result = null;
          }
          return _result;
        } finally {
          _cursor.close();
        }
      }

      @Override
      protected void finalize() {
        _statement.release();
      }
    });
  }

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
