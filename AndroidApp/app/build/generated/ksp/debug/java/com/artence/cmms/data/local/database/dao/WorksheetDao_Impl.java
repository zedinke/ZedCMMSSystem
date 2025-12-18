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
import com.artence.cmms.data.local.database.entities.WorksheetEntity;
import java.lang.Class;
import java.lang.Exception;
import java.lang.Integer;
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
public final class WorksheetDao_Impl implements WorksheetDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<WorksheetEntity> __insertionAdapterOfWorksheetEntity;

  private final EntityDeletionOrUpdateAdapter<WorksheetEntity> __deletionAdapterOfWorksheetEntity;

  private final EntityDeletionOrUpdateAdapter<WorksheetEntity> __updateAdapterOfWorksheetEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllWorksheets;

  public WorksheetDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfWorksheetEntity = new EntityInsertionAdapter<WorksheetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `worksheets` (`id`,`machineId`,`assignedToUserId`,`title`,`description`,`status`,`priority`,`createdAt`,`updatedAt`) VALUES (?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final WorksheetEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getMachineId() == null) {
          statement.bindNull(2);
        } else {
          statement.bindLong(2, entity.getMachineId());
        }
        if (entity.getAssignedToUserId() == null) {
          statement.bindNull(3);
        } else {
          statement.bindLong(3, entity.getAssignedToUserId());
        }
        statement.bindString(4, entity.getTitle());
        if (entity.getDescription() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDescription());
        }
        statement.bindString(6, entity.getStatus());
        if (entity.getPriority() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getPriority());
        }
        statement.bindLong(8, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(9);
        } else {
          statement.bindLong(9, entity.getUpdatedAt());
        }
      }
    };
    this.__deletionAdapterOfWorksheetEntity = new EntityDeletionOrUpdateAdapter<WorksheetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `worksheets` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final WorksheetEntity entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfWorksheetEntity = new EntityDeletionOrUpdateAdapter<WorksheetEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `worksheets` SET `id` = ?,`machineId` = ?,`assignedToUserId` = ?,`title` = ?,`description` = ?,`status` = ?,`priority` = ?,`createdAt` = ?,`updatedAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final WorksheetEntity entity) {
        statement.bindLong(1, entity.getId());
        if (entity.getMachineId() == null) {
          statement.bindNull(2);
        } else {
          statement.bindLong(2, entity.getMachineId());
        }
        if (entity.getAssignedToUserId() == null) {
          statement.bindNull(3);
        } else {
          statement.bindLong(3, entity.getAssignedToUserId());
        }
        statement.bindString(4, entity.getTitle());
        if (entity.getDescription() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDescription());
        }
        statement.bindString(6, entity.getStatus());
        if (entity.getPriority() == null) {
          statement.bindNull(7);
        } else {
          statement.bindString(7, entity.getPriority());
        }
        statement.bindLong(8, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(9);
        } else {
          statement.bindLong(9, entity.getUpdatedAt());
        }
        statement.bindLong(10, entity.getId());
      }
    };
    this.__preparedStmtOfDeleteAllWorksheets = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM worksheets";
        return _query;
      }
    };
  }

  @Override
  public Object insertWorksheet(final WorksheetEntity worksheet,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfWorksheetEntity.insert(worksheet);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertWorksheets(final List<WorksheetEntity> worksheets,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfWorksheetEntity.insert(worksheets);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteWorksheet(final WorksheetEntity worksheet,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfWorksheetEntity.handle(worksheet);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updateWorksheet(final WorksheetEntity worksheet,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfWorksheetEntity.handle(worksheet);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllWorksheets(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllWorksheets.acquire();
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
          __preparedStmtOfDeleteAllWorksheets.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<WorksheetEntity>> getAllWorksheets() {
    final String _sql = "SELECT * FROM worksheets";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"worksheets"}, new Callable<List<WorksheetEntity>>() {
      @Override
      @NonNull
      public List<WorksheetEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfTitle = CursorUtil.getColumnIndexOrThrow(_cursor, "title");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<WorksheetEntity> _result = new ArrayList<WorksheetEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final WorksheetEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final Integer _tmpMachineId;
            if (_cursor.isNull(_cursorIndexOfMachineId)) {
              _tmpMachineId = null;
            } else {
              _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            }
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpTitle;
            _tmpTitle = _cursor.getString(_cursorIndexOfTitle);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new WorksheetEntity(_tmpId,_tmpMachineId,_tmpAssignedToUserId,_tmpTitle,_tmpDescription,_tmpStatus,_tmpPriority,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getWorksheetById(final int id,
      final Continuation<? super WorksheetEntity> $completion) {
    final String _sql = "SELECT * FROM worksheets WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, id);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<WorksheetEntity>() {
      @Override
      @Nullable
      public WorksheetEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfTitle = CursorUtil.getColumnIndexOrThrow(_cursor, "title");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final WorksheetEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final Integer _tmpMachineId;
            if (_cursor.isNull(_cursorIndexOfMachineId)) {
              _tmpMachineId = null;
            } else {
              _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            }
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpTitle;
            _tmpTitle = _cursor.getString(_cursorIndexOfTitle);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _result = new WorksheetEntity(_tmpId,_tmpMachineId,_tmpAssignedToUserId,_tmpTitle,_tmpDescription,_tmpStatus,_tmpPriority,_tmpCreatedAt,_tmpUpdatedAt);
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
