# Error Handling Javítási Útmutató

**Dátum**: 2025.12.18  
**Cél**: Egységes error handling pattern implementálása minden service-ben

---

## 📋 JELENLEGI HELYZET

### Főbb problémák:

1. **Hiányzó `exc_info=True`**: Sok logger.error() és logger.warning() hívásban nincs exc_info=True, így nincs stack trace a logban
2. **Inkonzisztens error handling**: Különböző service-ekben más-más pattern van
3. **Hiányzó rollback logging**: Sok helyen van session.rollback(), de nincs log róla

---

## ✅ AJÁNLOTT PATTERN

### Standard Service Function Pattern

```python
def service_function(...):
    session, should_close = _get_session(session)
    try:
        # ... validáció, művelet ...
        
        session.commit()
        logger.info(f"Success: {operation_description}")
        return result
        
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except BusinessLogicError as e:
        session.rollback()
        logger.warning(f"Business logic error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except StateTransitionError as e:
        session.rollback()
        logger.warning(f"State transition error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in {__name__}.{service_function.__name__}: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()
```

### Secondary Operations (Notifications, Logging) Error Handling

Secondary műveleteknél (pl. notification küldés, log_action hívás) a hibák nem blokkolják a fő műveletet, szóval itt nem kell exc_info=True:

```python
# Notification küldés
try:
    from services.notification_service import notify_xxx
    notify_xxx(...)
except Exception as e:
    logger.warning(f"Error sending notification: {e}")  # ✅ OK, nincs exc_info

# Logging
try:
    from services.log_service import log_action
    log_action(...)
except Exception as e:
    logger.warning(f"Error logging action: {e}")  # ✅ OK, nincs exc_info
```

### Fő műveletek error handling (CRITICAL)

A fő műveleteknél (pl. database commit, validáció) MINDIG kell exc_info=True:

```python
try:
    # Fő művelet
    session.commit()
    return result
except Exception as e:
    session.rollback()
    logger.error(f"Error in {function_name}: {e}", exc_info=True)  # ✅ CRITICAL - exc_info=True
    raise
```

---

## 📝 JAVÍTANDÓ HELYEK (Prioritások szerint)

### P1: Fő műveletek error handling

**Fájlok:**
- `services/pm_service.py` - create_pm_task, update_pm_task, complete_pm_task fő except blokkok
- `services/worksheet_service.py` - create_worksheet, update_status fő except blokkok
- `services/inventory_service.py` - create_part, update_part, delete_part fő except blokkok
- `services/storage_service.py` - assign_part_to_location fő except blokk
- `services/asset_service.py` - create_machine, update_machine fő except blokkok

### P2: Secondary műveletek error handling

**Megjegyzés:** Ezeknél általában nincs szükség exc_info=True-ra, mert nem kritikusak.

### P3: Helper/decorator használata (opcionális)

Létrehozva: `utils/service_error_handler.py` - `handle_service_errors` decorator

Használható, de nem kötelező, mert a jelenlegi pattern is működik.

---

## 🔧 PÉLDA JAVÍTÁSOK

### Példa 1: PM Service - create_pm_task()

**Előtte:**
```python
def create_pm_task(...):
    session, should_close = _get_session(session)
    try:
        # ... művelet ...
        session.commit()
        return task
    finally:
        if should_close:
            session.close()
```

**Utána:**
```python
def create_pm_task(...):
    session, should_close = _get_session(session)
    try:
        # ... művelet ...
        session.commit()
        logger.info(f"PM Task created: {task.id} - {task.task_name}")
        return task
    except ValidationError as e:
        session.rollback()
        logger.warning(f"Validation error in pm_service.create_pm_task: {e}", exc_info=True)
        raise
    except NotFoundError as e:
        session.rollback()
        logger.warning(f"Not found error in pm_service.create_pm_task: {e}", exc_info=True)
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Unexpected error in pm_service.create_pm_task: {e}", exc_info=True)
        raise
    finally:
        if should_close:
            session.close()
```

---

## 📊 STATISZTIKA

**Fájlok száma:** ~42 service fájl
**Főbb service-ek (prioritásos):** 5-10 fájl
**Becsült munka:** 2-4 óra főbb service-eknél, 8-10 óra minden service-nél

---

## ✅ ELLENŐRZÉSI LISTA

- [ ] PM Service - fő except blokkok
- [ ] Worksheet Service - fő except blokkok
- [ ] Inventory Service - fő except blokkok
- [ ] Storage Service - fő except blokkok
- [ ] Asset Service - fő except blokkok
- [ ] Más service-ek - fő except blokkok

---

**Megjegyzés:** Ez egy folyamatos javítási folyamat. Az új service függvényeknél már használjuk az ajánlott pattern-t.

