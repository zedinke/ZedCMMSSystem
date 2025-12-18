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
import com.artence.cmms.data.local.database.entities.AssetEntity;
import java.lang.Class;
import java.lang.Double;
import java.lang.Exception;
import java.lang.Long;
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
public final class AssetDao_Impl implements AssetDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<AssetEntity> __insertionAdapterOfAssetEntity;

  private final EntityDeletionOrUpdateAdapter<AssetEntity> __deletionAdapterOfAssetEntity;

  private final EntityDeletionOrUpdateAdapter<AssetEntity> __updateAdapterOfAssetEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllAssets;

  public AssetDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfAssetEntity = new EntityInsertionAdapter<AssetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `assets` (`id`,`name`,`category`,`assetTag`,`serialNumber`,`manufacturer`,`model`,`location`,`status`,`purchaseDate`,`purchasePrice`,`warrantyExpiry`,`description`,`createdAt`,`updatedAt`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final AssetEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getName());
        if (entity.getCategory() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getCategory());
        }
        if (entity.getAssetTag() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getAssetTag());
        }
        if (entity.getSerialNumber() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getSerialNumber());
        }
        if (entity.getManufacturer() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getManufacturer());
        }
        if (entity.getModel() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getModel());
        }
        if (entity.getLocation() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getLocation());
        }
        statement.bindString(9, entity.getStatus());
        if (entity.getPurchaseDate() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getPurchaseDate());
        }
        if (entity.getPurchasePrice() == null) {
          statement.bindNull(11);
        } else {
          statement.bindDouble(11, entity.getPurchasePrice());
        }
        if (entity.getWarrantyExpiry() == null) {
          statement.bindNull(12);
        } else {
          statement.bindLong(12, entity.getWarrantyExpiry());
        }
        if (entity.getDescription() == null) {
          statement.bindNull(13);
        } else {
          statement.bindString(13, entity.getDescription());
        }
        statement.bindLong(14, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(15);
        } else {
          statement.bindLong(15, entity.getUpdatedAt());
        }
      }
    };
    this.__deletionAdapterOfAssetEntity = new EntityDeletionOrUpdateAdapter<AssetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `assets` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final AssetEntity entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfAssetEntity = new EntityDeletionOrUpdateAdapter<AssetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `assets` SET `id` = ?,`name` = ?,`category` = ?,`assetTag` = ?,`serialNumber` = ?,`manufacturer` = ?,`model` = ?,`location` = ?,`status` = ?,`purchaseDate` = ?,`purchasePrice` = ?,`warrantyExpiry` = ?,`description` = ?,`createdAt` = ?,`updatedAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final AssetEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindString(2, entity.getName());
        if (entity.getCategory() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getCategory());
        }
        if (entity.getAssetTag() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getAssetTag());
        }
        if (entity.getSerialNumber() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getSerialNumber());
        }
        if (entity.getManufacturer() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getManufacturer());
        }
        if (entity.getModel() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getModel());
        }
        if (entity.getLocation() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getLocation());
        }
        statement.bindString(9, entity.getStatus());
        if (entity.getPurchaseDate() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getPurchaseDate());
        }
        if (entity.getPurchasePrice() == null) {
          statement.bindNull(11);
        } else {
          statement.bindDouble(11, entity.getPurchasePrice());
        }
        if (entity.getWarrantyExpiry() == null) {
          statement.bindNull(12);
        } else {
          statement.bindLong(12, entity.getWarrantyExpiry());
        }
        if (entity.getDescription() == null) {
          statement.bindNull(13);
        } else {
          statement.bindString(13, entity.getDescription());
        }
        statement.bindLong(14, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(15);
        } else {
          statement.bindLong(15, entity.getUpdatedAt());
        }
        statement.bindLong(16, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAllAssets = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM assets";
        return _query;
      }
    };
  }

  @Override
  public Object insertAsset(final AssetEntity asset, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfAssetEntity.insert(asset);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertAssets(final List<AssetEntity> assets,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfAssetEntity.insert(assets);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAsset(final AssetEntity asset, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfAssetEntity.handle(asset);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateAsset(final AssetEntity asset, final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfAssetEntity.handle(asset);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllAssets(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllAssets.acquire();
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
          __preparedStmtOfDeleteAllAssets.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<AssetEntity>> getAllAssets() {
    final String _sql = "SELECT * FROM assets";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"assets"}, new Callable<List<AssetEntity>>() {
      @Override
      @NonNull
      public List<AssetEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfAssetTag = CursorUtil.getColumnIndexOrThrow(_cursor, "assetTag");
          final int _cursorIndexOfSerialNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "serialNumber");
          final int _cursorIndexOfManufacturer = CursorUtil.getColumnIndexOrThrow(_cursor, "manufacturer");
          final int _cursorIndexOfModel = CursorUtil.getColumnIndexOrThrow(_cursor, "model");
          final int _cursorIndexOfLocation = CursorUtil.getColumnIndexOrThrow(_cursor, "location");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfPurchaseDate = CursorUtil.getColumnIndexOrThrow(_cursor, "purchaseDate");
          final int _cursorIndexOfPurchasePrice = CursorUtil.getColumnIndexOrThrow(_cursor, "purchasePrice");
          final int _cursorIndexOfWarrantyExpiry = CursorUtil.getColumnIndexOrThrow(_cursor, "warrantyExpiry");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<AssetEntity> _result = new ArrayList<AssetEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final AssetEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpCategory;
            if (_cursor.isNull(_cursorIndexOfCategory)) {
              _tmpCategory = null;
            } else {
              _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            }
            final String _tmpAssetTag;
            if (_cursor.isNull(_cursorIndexOfAssetTag)) {
              _tmpAssetTag = null;
            } else {
              _tmpAssetTag = _cursor.getString(_cursorIndexOfAssetTag);
            }
            final String _tmpSerialNumber;
            if (_cursor.isNull(_cursorIndexOfSerialNumber)) {
              _tmpSerialNumber = null;
            } else {
              _tmpSerialNumber = _cursor.getString(_cursorIndexOfSerialNumber);
            }
            final String _tmpManufacturer;
            if (_cursor.isNull(_cursorIndexOfManufacturer)) {
              _tmpManufacturer = null;
            } else {
              _tmpManufacturer = _cursor.getString(_cursorIndexOfManufacturer);
            }
            final String _tmpModel;
            if (_cursor.isNull(_cursorIndexOfModel)) {
              _tmpModel = null;
            } else {
              _tmpModel = _cursor.getString(_cursorIndexOfModel);
            }
            final String _tmpLocation;
            if (_cursor.isNull(_cursorIndexOfLocation)) {
              _tmpLocation = null;
            } else {
              _tmpLocation = _cursor.getString(_cursorIndexOfLocation);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Long _tmpPurchaseDate;
            if (_cursor.isNull(_cursorIndexOfPurchaseDate)) {
              _tmpPurchaseDate = null;
            } else {
              _tmpPurchaseDate = _cursor.getLong(_cursorIndexOfPurchaseDate);
            }
            final Double _tmpPurchasePrice;
            if (_cursor.isNull(_cursorIndexOfPurchasePrice)) {
              _tmpPurchasePrice = null;
            } else {
              _tmpPurchasePrice = _cursor.getDouble(_cursorIndexOfPurchasePrice);
            }
            final Long _tmpWarrantyExpiry;
            if (_cursor.isNull(_cursorIndexOfWarrantyExpiry)) {
              _tmpWarrantyExpiry = null;
            } else {
              _tmpWarrantyExpiry = _cursor.getLong(_cursorIndexOfWarrantyExpiry);
            }
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new AssetEntity(_tmpId,_tmpName,_tmpCategory,_tmpAssetTag,_tmpSerialNumber,_tmpManufacturer,_tmpModel,_tmpLocation,_tmpStatus,_tmpPurchaseDate,_tmpPurchasePrice,_tmpWarrantyExpiry,_tmpDescription,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getAssetById(final int id, final Continuation<? super AssetEntity> $completion) {
    final String _sql = "SELECT * FROM assets WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, id);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<AssetEntity>() {
      @Override
      @Nullable
      public AssetEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfCategory = CursorUtil.getColumnIndexOrThrow(_cursor, "category");
          final int _cursorIndexOfAssetTag = CursorUtil.getColumnIndexOrThrow(_cursor, "assetTag");
          final int _cursorIndexOfSerialNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "serialNumber");
          final int _cursorIndexOfManufacturer = CursorUtil.getColumnIndexOrThrow(_cursor, "manufacturer");
          final int _cursorIndexOfModel = CursorUtil.getColumnIndexOrThrow(_cursor, "model");
          final int _cursorIndexOfLocation = CursorUtil.getColumnIndexOrThrow(_cursor, "location");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfPurchaseDate = CursorUtil.getColumnIndexOrThrow(_cursor, "purchaseDate");
          final int _cursorIndexOfPurchasePrice = CursorUtil.getColumnIndexOrThrow(_cursor, "purchasePrice");
          final int _cursorIndexOfWarrantyExpiry = CursorUtil.getColumnIndexOrThrow(_cursor, "warrantyExpiry");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final AssetEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpCategory;
            if (_cursor.isNull(_cursorIndexOfCategory)) {
              _tmpCategory = null;
            } else {
              _tmpCategory = _cursor.getString(_cursorIndexOfCategory);
            }
            final String _tmpAssetTag;
            if (_cursor.isNull(_cursorIndexOfAssetTag)) {
              _tmpAssetTag = null;
            } else {
              _tmpAssetTag = _cursor.getString(_cursorIndexOfAssetTag);
            }
            final String _tmpSerialNumber;
            if (_cursor.isNull(_cursorIndexOfSerialNumber)) {
              _tmpSerialNumber = null;
            } else {
              _tmpSerialNumber = _cursor.getString(_cursorIndexOfSerialNumber);
            }
            final String _tmpManufacturer;
            if (_cursor.isNull(_cursorIndexOfManufacturer)) {
              _tmpManufacturer = null;
            } else {
              _tmpManufacturer = _cursor.getString(_cursorIndexOfManufacturer);
            }
            final String _tmpModel;
            if (_cursor.isNull(_cursorIndexOfModel)) {
              _tmpModel = null;
            } else {
              _tmpModel = _cursor.getString(_cursorIndexOfModel);
            }
            final String _tmpLocation;
            if (_cursor.isNull(_cursorIndexOfLocation)) {
              _tmpLocation = null;
            } else {
              _tmpLocation = _cursor.getString(_cursorIndexOfLocation);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Long _tmpPurchaseDate;
            if (_cursor.isNull(_cursorIndexOfPurchaseDate)) {
              _tmpPurchaseDate = null;
            } else {
              _tmpPurchaseDate = _cursor.getLong(_cursorIndexOfPurchaseDate);
            }
            final Double _tmpPurchasePrice;
            if (_cursor.isNull(_cursorIndexOfPurchasePrice)) {
              _tmpPurchasePrice = null;
            } else {
              _tmpPurchasePrice = _cursor.getDouble(_cursorIndexOfPurchasePrice);
            }
            final Long _tmpWarrantyExpiry;
            if (_cursor.isNull(_cursorIndexOfWarrantyExpiry)) {
              _tmpWarrantyExpiry = null;
            } else {
              _tmpWarrantyExpiry = _cursor.getLong(_cursorIndexOfWarrantyExpiry);
            }
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _result = new AssetEntity(_tmpId,_tmpName,_tmpCategory,_tmpAssetTag,_tmpSerialNumber,_tmpManufacturer,_tmpModel,_tmpLocation,_tmpStatus,_tmpPurchaseDate,_tmpPurchasePrice,_tmpWarrantyExpiry,_tmpDescription,_tmpCreatedAt,_tmpUpdatedAt);
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

  @NonNull
  public static List<Class<?>> getRequiredConverters() {
    return Collections.emptyList();
  }
}
