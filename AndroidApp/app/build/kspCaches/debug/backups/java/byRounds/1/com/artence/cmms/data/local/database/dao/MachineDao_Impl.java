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
import com.artence.cmms.data.local.database.entities.MachineEntity;
import java.lang.Class;
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
public final class MachineDao_Impl implements MachineDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<MachineEntity> __insertionAdapterOfMachineEntity;

  private final EntityDeletionOrUpdateAdapter<MachineEntity> __deletionAdapterOfMachineEntity;

  private final EntityDeletionOrUpdateAdapter<MachineEntity> __updateAdapterOfMachineEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllMachines;

  public MachineDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfMachineEntity = new EntityInsertionAdapter<MachineEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `machines` (`id`,`productionLineId`,`name`,`serialNumber`,`model`,`manufacturer`,`status`,`assetTag`,`createdAt`,`updatedAt`) VALUES (?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final MachineEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getProductionLineId());
        statement.bindString(3, entity.getName());
        if (entity.getSerialNumber() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getSerialNumber());
        }
        if (entity.getModel() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getModel());
        }
        if (entity.getManufacturer() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getManufacturer());
        }
        statement.bindString(7, entity.getStatus());
        if (entity.getAssetTag() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getAssetTag());
        }
        statement.bindLong(9, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getUpdatedAt());
        }
      }
    };
    this.__deletionAdapterOfMachineEntity = new EntityDeletionOrUpdateAdapter<MachineEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `machines` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final MachineEntity entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfMachineEntity = new EntityDeletionOrUpdateAdapter<MachineEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `machines` SET `id` = ?,`productionLineId` = ?,`name` = ?,`serialNumber` = ?,`model` = ?,`manufacturer` = ?,`status` = ?,`assetTag` = ?,`createdAt` = ?,`updatedAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final MachineEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getProductionLineId());
        statement.bindString(3, entity.getName());
        if (entity.getSerialNumber() == null) {
          statement.bindNull(4);
        } else {
          statement.bindString(4, entity.getSerialNumber());
        }
        if (entity.getModel() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getModel());
        }
        if (entity.getManufacturer() == null) {
          statement.bindNull(6);
        } else {
          statement.bindString(6, entity.getManufacturer());
        }
        statement.bindString(7, entity.getStatus());
        if (entity.getAssetTag() == null) {
          statement.bindNull(8);
        } else {
          statement.bindString(8, entity.getAssetTag());
        }
        statement.bindLong(9, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getUpdatedAt());
        }
        statement.bindLong(11, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAllMachines = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM machines";
        return _query;
      }
    };
  }

  @Override
  public Object insertMachine(final MachineEntity machine,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfMachineEntity.insert(machine);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertMachines(final List<MachineEntity> machines,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfMachineEntity.insert(machines);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteMachine(final MachineEntity machine,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfMachineEntity.handle(machine);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateMachine(final MachineEntity machine,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfMachineEntity.handle(machine);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllMachines(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllMachines.acquire();
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
          __preparedStmtOfDeleteAllMachines.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<MachineEntity>> getAllMachines() {
    final String _sql = "SELECT * FROM machines";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"machines"}, new Callable<List<MachineEntity>>() {
      @Override
      @NonNull
      public List<MachineEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfProductionLineId = CursorUtil.getColumnIndexOrThrow(_cursor, "productionLineId");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfSerialNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "serialNumber");
          final int _cursorIndexOfModel = CursorUtil.getColumnIndexOrThrow(_cursor, "model");
          final int _cursorIndexOfManufacturer = CursorUtil.getColumnIndexOrThrow(_cursor, "manufacturer");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssetTag = CursorUtil.getColumnIndexOrThrow(_cursor, "assetTag");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<MachineEntity> _result = new ArrayList<MachineEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final MachineEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpProductionLineId;
            _tmpProductionLineId = _cursor.getInt(_cursorIndexOfProductionLineId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpSerialNumber;
            if (_cursor.isNull(_cursorIndexOfSerialNumber)) {
              _tmpSerialNumber = null;
            } else {
              _tmpSerialNumber = _cursor.getString(_cursorIndexOfSerialNumber);
            }
            final String _tmpModel;
            if (_cursor.isNull(_cursorIndexOfModel)) {
              _tmpModel = null;
            } else {
              _tmpModel = _cursor.getString(_cursorIndexOfModel);
            }
            final String _tmpManufacturer;
            if (_cursor.isNull(_cursorIndexOfManufacturer)) {
              _tmpManufacturer = null;
            } else {
              _tmpManufacturer = _cursor.getString(_cursorIndexOfManufacturer);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final String _tmpAssetTag;
            if (_cursor.isNull(_cursorIndexOfAssetTag)) {
              _tmpAssetTag = null;
            } else {
              _tmpAssetTag = _cursor.getString(_cursorIndexOfAssetTag);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new MachineEntity(_tmpId,_tmpProductionLineId,_tmpName,_tmpSerialNumber,_tmpModel,_tmpManufacturer,_tmpStatus,_tmpAssetTag,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getMachineById(final int id,
      final Continuation<? super MachineEntity> $completion) {
    final String _sql = "SELECT * FROM machines WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, id);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<MachineEntity>() {
      @Override
      @Nullable
      public MachineEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfProductionLineId = CursorUtil.getColumnIndexOrThrow(_cursor, "productionLineId");
          final int _cursorIndexOfName = CursorUtil.getColumnIndexOrThrow(_cursor, "name");
          final int _cursorIndexOfSerialNumber = CursorUtil.getColumnIndexOrThrow(_cursor, "serialNumber");
          final int _cursorIndexOfModel = CursorUtil.getColumnIndexOrThrow(_cursor, "model");
          final int _cursorIndexOfManufacturer = CursorUtil.getColumnIndexOrThrow(_cursor, "manufacturer");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssetTag = CursorUtil.getColumnIndexOrThrow(_cursor, "assetTag");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final MachineEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpProductionLineId;
            _tmpProductionLineId = _cursor.getInt(_cursorIndexOfProductionLineId);
            final String _tmpName;
            _tmpName = _cursor.getString(_cursorIndexOfName);
            final String _tmpSerialNumber;
            if (_cursor.isNull(_cursorIndexOfSerialNumber)) {
              _tmpSerialNumber = null;
            } else {
              _tmpSerialNumber = _cursor.getString(_cursorIndexOfSerialNumber);
            }
            final String _tmpModel;
            if (_cursor.isNull(_cursorIndexOfModel)) {
              _tmpModel = null;
            } else {
              _tmpModel = _cursor.getString(_cursorIndexOfModel);
            }
            final String _tmpManufacturer;
            if (_cursor.isNull(_cursorIndexOfManufacturer)) {
              _tmpManufacturer = null;
            } else {
              _tmpManufacturer = _cursor.getString(_cursorIndexOfManufacturer);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final String _tmpAssetTag;
            if (_cursor.isNull(_cursorIndexOfAssetTag)) {
              _tmpAssetTag = null;
            } else {
              _tmpAssetTag = _cursor.getString(_cursorIndexOfAssetTag);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _result = new MachineEntity(_tmpId,_tmpProductionLineId,_tmpName,_tmpSerialNumber,_tmpModel,_tmpManufacturer,_tmpStatus,_tmpAssetTag,_tmpCreatedAt,_tmpUpdatedAt);
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
