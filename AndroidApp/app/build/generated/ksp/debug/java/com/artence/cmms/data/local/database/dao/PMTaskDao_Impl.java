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
import com.artence.cmms.data.local.database.entities.PMTaskEntity;
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
public final class PMTaskDao_Impl implements PMTaskDao {
  private final RoomDatabase __db;

  private final EntityInsertionAdapter<PMTaskEntity> __insertionAdapterOfPMTaskEntity;

  private final EntityDeletionOrUpdateAdapter<PMTaskEntity> __deletionAdapterOfPMTaskEntity;

  private final EntityDeletionOrUpdateAdapter<PMTaskEntity> __updateAdapterOfPMTaskEntity;

  private final SharedSQLiteStatement __preparedStmtOfDeleteAllPMTasks;

  public PMTaskDao_Impl(@NonNull final RoomDatabase __db) {
    this.__db = __db;
    this.__insertionAdapterOfPMTaskEntity = new EntityInsertionAdapter<PMTaskEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "INSERT OR REPLACE INTO `pm_tasks` (`id`,`machineId`,`machineName`,`taskName`,`description`,`frequency`,`lastExecuted`,`nextScheduled`,`status`,`assignedToUserId`,`assignedToUsername`,`priority`,`estimatedDuration`,`createdAt`,`updatedAt`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final PMTaskEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getMachineId());
        if (entity.getMachineName() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getMachineName());
        }
        statement.bindString(4, entity.getTaskName());
        if (entity.getDescription() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDescription());
        }
        statement.bindString(6, entity.getFrequency());
        if (entity.getLastExecuted() == null) {
          statement.bindNull(7);
        } else {
          statement.bindLong(7, entity.getLastExecuted());
        }
        statement.bindLong(8, entity.getNextScheduled());
        statement.bindString(9, entity.getStatus());
        if (entity.getAssignedToUserId() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getAssignedToUserId());
        }
        if (entity.getAssignedToUsername() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getAssignedToUsername());
        }
        if (entity.getPriority() == null) {
          statement.bindNull(12);
        } else {
          statement.bindString(12, entity.getPriority());
        }
        if (entity.getEstimatedDuration() == null) {
          statement.bindNull(13);
        } else {
          statement.bindLong(13, entity.getEstimatedDuration());
        }
        statement.bindLong(14, entity.getCreatedAt());
        if (entity.getUpdatedAt() == null) {
          statement.bindNull(15);
        } else {
          statement.bindLong(15, entity.getUpdatedAt());
        }
      }
    };
    this.__deletionAdapterOfPMTaskEntity = new EntityDeletionOrUpdateAdapter<PMTaskEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "DELETE FROM `pm_tasks` WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final PMTaskEntity entity) {
        statement.bindLong(1, entity.getId());
      }
    };
    this.__updateAdapterOfPMTaskEntity = new EntityDeletionOrUpdateAdapter<PMTaskEntity>(__db) {
      @Override
      @NonNull
      protected String createQuery() {
        return "UPDATE OR ABORT `pm_tasks` SET `id` = ?,`machineId` = ?,`machineName` = ?,`taskName` = ?,`description` = ?,`frequency` = ?,`lastExecuted` = ?,`nextScheduled` = ?,`status` = ?,`assignedToUserId` = ?,`assignedToUsername` = ?,`priority` = ?,`estimatedDuration` = ?,`createdAt` = ?,`updatedAt` = ? WHERE `id` = ?";
      }

      @Override
      protected void bind(@NonNull final SupportSQLiteStatement statement,
          @NonNull final PMTaskEntity entity) {
        statement.bindLong(1, entity.getId());
        statement.bindLong(2, entity.getMachineId());
        if (entity.getMachineName() == null) {
          statement.bindNull(3);
        } else {
          statement.bindString(3, entity.getMachineName());
        }
        statement.bindString(4, entity.getTaskName());
        if (entity.getDescription() == null) {
          statement.bindNull(5);
        } else {
          statement.bindString(5, entity.getDescription());
        }
        statement.bindString(6, entity.getFrequency());
        if (entity.getLastExecuted() == null) {
          statement.bindNull(7);
        } else {
          statement.bindLong(7, entity.getLastExecuted());
        }
        statement.bindLong(8, entity.getNextScheduled());
        statement.bindString(9, entity.getStatus());
        if (entity.getAssignedToUserId() == null) {
          statement.bindNull(10);
        } else {
          statement.bindLong(10, entity.getAssignedToUserId());
        }
        if (entity.getAssignedToUsername() == null) {
          statement.bindNull(11);
        } else {
          statement.bindString(11, entity.getAssignedToUsername());
        }
        if (entity.getPriority() == null) {
          statement.bindNull(12);
        } else {
          statement.bindString(12, entity.getPriority());
        }
        if (entity.getEstimatedDuration() == null) {
          statement.bindNull(13);
        } else {
          statement.bindLong(13, entity.getEstimatedDuration());
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
    this.__preparedStmtOfDeleteAllPMTasks = new SharedSQLiteStatement(__db) {
      @Override
      @NonNull
      public String createQuery() {
        final String _query = "DELETE FROM pm_tasks";
        return _query;
      }
    };
  }

  @Override
  public Object insertPMTask(final PMTaskEntity task,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfPMTaskEntity.insert(task);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object insertPMTasks(final List<PMTaskEntity> tasks,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __insertionAdapterOfPMTaskEntity.insert(tasks);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deletePMTask(final PMTaskEntity task,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __deletionAdapterOfPMTaskEntity.handle(task);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object updatePMTask(final PMTaskEntity task,
      final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        __db.beginTransaction();
        try {
          __updateAdapterOfPMTaskEntity.handle(task);
          __db.setTransactionSuccessful();
          return Unit.INSTANCE;
        } finally {
          __db.endTransaction();
        }
      }
    }, $completion);
  }

  @Override
  public Object deleteAllPMTasks(final Continuation<? super Unit> $completion) {
    return CoroutinesRoom.execute(__db, true, new Callable<Unit>() {
      @Override
      @NonNull
      public Unit call() throws Exception {
        final SupportSQLiteStatement _stmt = __preparedStmtOfDeleteAllPMTasks.acquire();
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
          __preparedStmtOfDeleteAllPMTasks.release(_stmt);
        }
      }
    }, $completion);
  }

  @Override
  public Flow<List<PMTaskEntity>> getAllPMTasks() {
    final String _sql = "SELECT * FROM pm_tasks ORDER BY nextScheduled ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"pm_tasks"}, new Callable<List<PMTaskEntity>>() {
      @Override
      @NonNull
      public List<PMTaskEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfMachineName = CursorUtil.getColumnIndexOrThrow(_cursor, "machineName");
          final int _cursorIndexOfTaskName = CursorUtil.getColumnIndexOrThrow(_cursor, "taskName");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfLastExecuted = CursorUtil.getColumnIndexOrThrow(_cursor, "lastExecuted");
          final int _cursorIndexOfNextScheduled = CursorUtil.getColumnIndexOrThrow(_cursor, "nextScheduled");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfAssignedToUsername = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUsername");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfEstimatedDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "estimatedDuration");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<PMTaskEntity> _result = new ArrayList<PMTaskEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PMTaskEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpMachineId;
            _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            final String _tmpMachineName;
            if (_cursor.isNull(_cursorIndexOfMachineName)) {
              _tmpMachineName = null;
            } else {
              _tmpMachineName = _cursor.getString(_cursorIndexOfMachineName);
            }
            final String _tmpTaskName;
            _tmpTaskName = _cursor.getString(_cursorIndexOfTaskName);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpFrequency;
            _tmpFrequency = _cursor.getString(_cursorIndexOfFrequency);
            final Long _tmpLastExecuted;
            if (_cursor.isNull(_cursorIndexOfLastExecuted)) {
              _tmpLastExecuted = null;
            } else {
              _tmpLastExecuted = _cursor.getLong(_cursorIndexOfLastExecuted);
            }
            final long _tmpNextScheduled;
            _tmpNextScheduled = _cursor.getLong(_cursorIndexOfNextScheduled);
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpAssignedToUsername;
            if (_cursor.isNull(_cursorIndexOfAssignedToUsername)) {
              _tmpAssignedToUsername = null;
            } else {
              _tmpAssignedToUsername = _cursor.getString(_cursorIndexOfAssignedToUsername);
            }
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final Integer _tmpEstimatedDuration;
            if (_cursor.isNull(_cursorIndexOfEstimatedDuration)) {
              _tmpEstimatedDuration = null;
            } else {
              _tmpEstimatedDuration = _cursor.getInt(_cursorIndexOfEstimatedDuration);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new PMTaskEntity(_tmpId,_tmpMachineId,_tmpMachineName,_tmpTaskName,_tmpDescription,_tmpFrequency,_tmpLastExecuted,_tmpNextScheduled,_tmpStatus,_tmpAssignedToUserId,_tmpAssignedToUsername,_tmpPriority,_tmpEstimatedDuration,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<List<PMTaskEntity>> getPMTasksByStatus(final String status) {
    final String _sql = "SELECT * FROM pm_tasks WHERE status = ? ORDER BY nextScheduled ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindString(_argIndex, status);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"pm_tasks"}, new Callable<List<PMTaskEntity>>() {
      @Override
      @NonNull
      public List<PMTaskEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfMachineName = CursorUtil.getColumnIndexOrThrow(_cursor, "machineName");
          final int _cursorIndexOfTaskName = CursorUtil.getColumnIndexOrThrow(_cursor, "taskName");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfLastExecuted = CursorUtil.getColumnIndexOrThrow(_cursor, "lastExecuted");
          final int _cursorIndexOfNextScheduled = CursorUtil.getColumnIndexOrThrow(_cursor, "nextScheduled");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfAssignedToUsername = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUsername");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfEstimatedDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "estimatedDuration");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<PMTaskEntity> _result = new ArrayList<PMTaskEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PMTaskEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpMachineId;
            _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            final String _tmpMachineName;
            if (_cursor.isNull(_cursorIndexOfMachineName)) {
              _tmpMachineName = null;
            } else {
              _tmpMachineName = _cursor.getString(_cursorIndexOfMachineName);
            }
            final String _tmpTaskName;
            _tmpTaskName = _cursor.getString(_cursorIndexOfTaskName);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpFrequency;
            _tmpFrequency = _cursor.getString(_cursorIndexOfFrequency);
            final Long _tmpLastExecuted;
            if (_cursor.isNull(_cursorIndexOfLastExecuted)) {
              _tmpLastExecuted = null;
            } else {
              _tmpLastExecuted = _cursor.getLong(_cursorIndexOfLastExecuted);
            }
            final long _tmpNextScheduled;
            _tmpNextScheduled = _cursor.getLong(_cursorIndexOfNextScheduled);
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpAssignedToUsername;
            if (_cursor.isNull(_cursorIndexOfAssignedToUsername)) {
              _tmpAssignedToUsername = null;
            } else {
              _tmpAssignedToUsername = _cursor.getString(_cursorIndexOfAssignedToUsername);
            }
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final Integer _tmpEstimatedDuration;
            if (_cursor.isNull(_cursorIndexOfEstimatedDuration)) {
              _tmpEstimatedDuration = null;
            } else {
              _tmpEstimatedDuration = _cursor.getInt(_cursorIndexOfEstimatedDuration);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new PMTaskEntity(_tmpId,_tmpMachineId,_tmpMachineName,_tmpTaskName,_tmpDescription,_tmpFrequency,_tmpLastExecuted,_tmpNextScheduled,_tmpStatus,_tmpAssignedToUserId,_tmpAssignedToUsername,_tmpPriority,_tmpEstimatedDuration,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<List<PMTaskEntity>> getPMTasksByMachine(final int machineId) {
    final String _sql = "SELECT * FROM pm_tasks WHERE machineId = ? ORDER BY nextScheduled ASC";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, machineId);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"pm_tasks"}, new Callable<List<PMTaskEntity>>() {
      @Override
      @NonNull
      public List<PMTaskEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfMachineName = CursorUtil.getColumnIndexOrThrow(_cursor, "machineName");
          final int _cursorIndexOfTaskName = CursorUtil.getColumnIndexOrThrow(_cursor, "taskName");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfLastExecuted = CursorUtil.getColumnIndexOrThrow(_cursor, "lastExecuted");
          final int _cursorIndexOfNextScheduled = CursorUtil.getColumnIndexOrThrow(_cursor, "nextScheduled");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfAssignedToUsername = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUsername");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfEstimatedDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "estimatedDuration");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<PMTaskEntity> _result = new ArrayList<PMTaskEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PMTaskEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpMachineId;
            _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            final String _tmpMachineName;
            if (_cursor.isNull(_cursorIndexOfMachineName)) {
              _tmpMachineName = null;
            } else {
              _tmpMachineName = _cursor.getString(_cursorIndexOfMachineName);
            }
            final String _tmpTaskName;
            _tmpTaskName = _cursor.getString(_cursorIndexOfTaskName);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpFrequency;
            _tmpFrequency = _cursor.getString(_cursorIndexOfFrequency);
            final Long _tmpLastExecuted;
            if (_cursor.isNull(_cursorIndexOfLastExecuted)) {
              _tmpLastExecuted = null;
            } else {
              _tmpLastExecuted = _cursor.getLong(_cursorIndexOfLastExecuted);
            }
            final long _tmpNextScheduled;
            _tmpNextScheduled = _cursor.getLong(_cursorIndexOfNextScheduled);
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpAssignedToUsername;
            if (_cursor.isNull(_cursorIndexOfAssignedToUsername)) {
              _tmpAssignedToUsername = null;
            } else {
              _tmpAssignedToUsername = _cursor.getString(_cursorIndexOfAssignedToUsername);
            }
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final Integer _tmpEstimatedDuration;
            if (_cursor.isNull(_cursorIndexOfEstimatedDuration)) {
              _tmpEstimatedDuration = null;
            } else {
              _tmpEstimatedDuration = _cursor.getInt(_cursorIndexOfEstimatedDuration);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new PMTaskEntity(_tmpId,_tmpMachineId,_tmpMachineName,_tmpTaskName,_tmpDescription,_tmpFrequency,_tmpLastExecuted,_tmpNextScheduled,_tmpStatus,_tmpAssignedToUserId,_tmpAssignedToUsername,_tmpPriority,_tmpEstimatedDuration,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Object getPMTaskById(final int id, final Continuation<? super PMTaskEntity> $completion) {
    final String _sql = "SELECT * FROM pm_tasks WHERE id = ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, id);
    final CancellationSignal _cancellationSignal = DBUtil.createCancellationSignal();
    return CoroutinesRoom.execute(__db, false, _cancellationSignal, new Callable<PMTaskEntity>() {
      @Override
      @Nullable
      public PMTaskEntity call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfMachineName = CursorUtil.getColumnIndexOrThrow(_cursor, "machineName");
          final int _cursorIndexOfTaskName = CursorUtil.getColumnIndexOrThrow(_cursor, "taskName");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfLastExecuted = CursorUtil.getColumnIndexOrThrow(_cursor, "lastExecuted");
          final int _cursorIndexOfNextScheduled = CursorUtil.getColumnIndexOrThrow(_cursor, "nextScheduled");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfAssignedToUsername = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUsername");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfEstimatedDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "estimatedDuration");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final PMTaskEntity _result;
          if (_cursor.moveToFirst()) {
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpMachineId;
            _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            final String _tmpMachineName;
            if (_cursor.isNull(_cursorIndexOfMachineName)) {
              _tmpMachineName = null;
            } else {
              _tmpMachineName = _cursor.getString(_cursorIndexOfMachineName);
            }
            final String _tmpTaskName;
            _tmpTaskName = _cursor.getString(_cursorIndexOfTaskName);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpFrequency;
            _tmpFrequency = _cursor.getString(_cursorIndexOfFrequency);
            final Long _tmpLastExecuted;
            if (_cursor.isNull(_cursorIndexOfLastExecuted)) {
              _tmpLastExecuted = null;
            } else {
              _tmpLastExecuted = _cursor.getLong(_cursorIndexOfLastExecuted);
            }
            final long _tmpNextScheduled;
            _tmpNextScheduled = _cursor.getLong(_cursorIndexOfNextScheduled);
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpAssignedToUsername;
            if (_cursor.isNull(_cursorIndexOfAssignedToUsername)) {
              _tmpAssignedToUsername = null;
            } else {
              _tmpAssignedToUsername = _cursor.getString(_cursorIndexOfAssignedToUsername);
            }
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final Integer _tmpEstimatedDuration;
            if (_cursor.isNull(_cursorIndexOfEstimatedDuration)) {
              _tmpEstimatedDuration = null;
            } else {
              _tmpEstimatedDuration = _cursor.getInt(_cursorIndexOfEstimatedDuration);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _result = new PMTaskEntity(_tmpId,_tmpMachineId,_tmpMachineName,_tmpTaskName,_tmpDescription,_tmpFrequency,_tmpLastExecuted,_tmpNextScheduled,_tmpStatus,_tmpAssignedToUserId,_tmpAssignedToUsername,_tmpPriority,_tmpEstimatedDuration,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<List<PMTaskEntity>> getUpcomingPMTasks(final int limit) {
    final String _sql = "SELECT * FROM pm_tasks WHERE status IN ('Overdue', 'Scheduled') ORDER BY nextScheduled ASC LIMIT ?";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 1);
    int _argIndex = 1;
    _statement.bindLong(_argIndex, limit);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"pm_tasks"}, new Callable<List<PMTaskEntity>>() {
      @Override
      @NonNull
      public List<PMTaskEntity> call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final int _cursorIndexOfId = CursorUtil.getColumnIndexOrThrow(_cursor, "id");
          final int _cursorIndexOfMachineId = CursorUtil.getColumnIndexOrThrow(_cursor, "machineId");
          final int _cursorIndexOfMachineName = CursorUtil.getColumnIndexOrThrow(_cursor, "machineName");
          final int _cursorIndexOfTaskName = CursorUtil.getColumnIndexOrThrow(_cursor, "taskName");
          final int _cursorIndexOfDescription = CursorUtil.getColumnIndexOrThrow(_cursor, "description");
          final int _cursorIndexOfFrequency = CursorUtil.getColumnIndexOrThrow(_cursor, "frequency");
          final int _cursorIndexOfLastExecuted = CursorUtil.getColumnIndexOrThrow(_cursor, "lastExecuted");
          final int _cursorIndexOfNextScheduled = CursorUtil.getColumnIndexOrThrow(_cursor, "nextScheduled");
          final int _cursorIndexOfStatus = CursorUtil.getColumnIndexOrThrow(_cursor, "status");
          final int _cursorIndexOfAssignedToUserId = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUserId");
          final int _cursorIndexOfAssignedToUsername = CursorUtil.getColumnIndexOrThrow(_cursor, "assignedToUsername");
          final int _cursorIndexOfPriority = CursorUtil.getColumnIndexOrThrow(_cursor, "priority");
          final int _cursorIndexOfEstimatedDuration = CursorUtil.getColumnIndexOrThrow(_cursor, "estimatedDuration");
          final int _cursorIndexOfCreatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "createdAt");
          final int _cursorIndexOfUpdatedAt = CursorUtil.getColumnIndexOrThrow(_cursor, "updatedAt");
          final List<PMTaskEntity> _result = new ArrayList<PMTaskEntity>(_cursor.getCount());
          while (_cursor.moveToNext()) {
            final PMTaskEntity _item;
            final int _tmpId;
            _tmpId = _cursor.getInt(_cursorIndexOfId);
            final int _tmpMachineId;
            _tmpMachineId = _cursor.getInt(_cursorIndexOfMachineId);
            final String _tmpMachineName;
            if (_cursor.isNull(_cursorIndexOfMachineName)) {
              _tmpMachineName = null;
            } else {
              _tmpMachineName = _cursor.getString(_cursorIndexOfMachineName);
            }
            final String _tmpTaskName;
            _tmpTaskName = _cursor.getString(_cursorIndexOfTaskName);
            final String _tmpDescription;
            if (_cursor.isNull(_cursorIndexOfDescription)) {
              _tmpDescription = null;
            } else {
              _tmpDescription = _cursor.getString(_cursorIndexOfDescription);
            }
            final String _tmpFrequency;
            _tmpFrequency = _cursor.getString(_cursorIndexOfFrequency);
            final Long _tmpLastExecuted;
            if (_cursor.isNull(_cursorIndexOfLastExecuted)) {
              _tmpLastExecuted = null;
            } else {
              _tmpLastExecuted = _cursor.getLong(_cursorIndexOfLastExecuted);
            }
            final long _tmpNextScheduled;
            _tmpNextScheduled = _cursor.getLong(_cursorIndexOfNextScheduled);
            final String _tmpStatus;
            _tmpStatus = _cursor.getString(_cursorIndexOfStatus);
            final Integer _tmpAssignedToUserId;
            if (_cursor.isNull(_cursorIndexOfAssignedToUserId)) {
              _tmpAssignedToUserId = null;
            } else {
              _tmpAssignedToUserId = _cursor.getInt(_cursorIndexOfAssignedToUserId);
            }
            final String _tmpAssignedToUsername;
            if (_cursor.isNull(_cursorIndexOfAssignedToUsername)) {
              _tmpAssignedToUsername = null;
            } else {
              _tmpAssignedToUsername = _cursor.getString(_cursorIndexOfAssignedToUsername);
            }
            final String _tmpPriority;
            if (_cursor.isNull(_cursorIndexOfPriority)) {
              _tmpPriority = null;
            } else {
              _tmpPriority = _cursor.getString(_cursorIndexOfPriority);
            }
            final Integer _tmpEstimatedDuration;
            if (_cursor.isNull(_cursorIndexOfEstimatedDuration)) {
              _tmpEstimatedDuration = null;
            } else {
              _tmpEstimatedDuration = _cursor.getInt(_cursorIndexOfEstimatedDuration);
            }
            final long _tmpCreatedAt;
            _tmpCreatedAt = _cursor.getLong(_cursorIndexOfCreatedAt);
            final Long _tmpUpdatedAt;
            if (_cursor.isNull(_cursorIndexOfUpdatedAt)) {
              _tmpUpdatedAt = null;
            } else {
              _tmpUpdatedAt = _cursor.getLong(_cursorIndexOfUpdatedAt);
            }
            _item = new PMTaskEntity(_tmpId,_tmpMachineId,_tmpMachineName,_tmpTaskName,_tmpDescription,_tmpFrequency,_tmpLastExecuted,_tmpNextScheduled,_tmpStatus,_tmpAssignedToUserId,_tmpAssignedToUsername,_tmpPriority,_tmpEstimatedDuration,_tmpCreatedAt,_tmpUpdatedAt);
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
  public Flow<Integer> getOverdueTaskCount() {
    final String _sql = "SELECT COUNT(*) FROM pm_tasks WHERE status = 'Overdue'";
    final RoomSQLiteQuery _statement = RoomSQLiteQuery.acquire(_sql, 0);
    return CoroutinesRoom.createFlow(__db, false, new String[] {"pm_tasks"}, new Callable<Integer>() {
      @Override
      @NonNull
      public Integer call() throws Exception {
        final Cursor _cursor = DBUtil.query(__db, _statement, false, null);
        try {
          final Integer _result;
          if (_cursor.moveToFirst()) {
            final int _tmp;
            _tmp = _cursor.getInt(0);
            _result = _tmp;
          } else {
            _result = 0;
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
