# Központi Debug Rendszer Dokumentáció

## Áttekintés

A központi debug rendszer egy részletes, lépésről lépésre végigkövető debug infrastruktúra, amely automatikusan aktív, ha a `DEBUG=True` beállítás be van kapcsolva az `app_config.py`-ban vagy a `.env` fájlban. A rendszer minden debug üzenetet fájlba (`data/logs/debug.log`) és konzolra is ír.

## Használat

### Alapvető Import

```python
from utils.debug_helper import (
    debug_entry, debug_exit, debug_step, debug_variable, 
    debug_call, debug_return, debug_error, debug_exception,
    debug_ui, debug_db, debug_service, debug_context,
    is_debug_enabled
)
```

### Függvény Debug-olása

#### Manuális Debug Naplózás

```python
def my_function(param1, param2):
    module_name = "my_module"
    function_name = "my_function"
    
    # Függvény belépés
    debug_entry(module_name, function_name, {
        "param1": param1,
        "param2": param2
    })
    
    try:
        # Lépés naplózása
        debug_step(module_name, function_name, "Processing data")
        
        # Változó érték naplózása
        result = param1 + param2
        debug_variable(module_name, function_name, "result", result)
        
        # Service hívás naplózása
        debug_service(module_name, function_name, "external_service.process", {
            "input": result
        })
        external_result = external_service.process(result)
        debug_return(module_name, function_name, "external_service.process", external_result)
        
        # Függvény kilépés
        debug_exit(module_name, function_name, {"return": external_result})
        return external_result
        
    except Exception as e:
        # Kivétel naplózása
        debug_exception(module_name, function_name, e, {
            "param1": param1,
            "param2": param2
        })
        raise
```

#### Decorator Használata

```python
from utils.debug_helper import debug_function

@debug_function
def my_function(param1, param2):
    # Automatikusan naplózza a belépést, kilépést, paramétereket és visszatérési értéket
    result = param1 + param2
    return result
```

### Context Manager Használata

```python
from utils.debug_helper import debug_context

def my_function():
    module_name = "my_module"
    function_name = "my_function"
    
    with debug_context(module_name, function_name, "database_transaction", {"table": "users"}):
        # Ez a blokk automatikusan naplózva lesz
        db.execute("SELECT * FROM users")
```

### UI Interakciók Debug-olása

```python
def on_button_click(e):
    module_name = "my_screen"
    function_name = "on_button_click"
    
    debug_ui(module_name, function_name, "Button clicked", {
        "button_id": e.control.data,
        "timestamp": datetime.now()
    })
    
    # UI művelet...
```

### Adatbázis Műveletek Debug-olása

```python
def query_users():
    module_name = "user_service"
    function_name = "query_users"
    
    query = "SELECT * FROM users WHERE active = :active"
    params = {"active": True}
    
    debug_db(module_name, function_name, query, params)
    
    # Query végrehajtása...
```

### Service Hívások Debug-olása

```python
def call_external_api():
    module_name = "api_service"
    function_name = "call_external_api"
    
    debug_service(module_name, function_name, "external_api.get_data", {
        "endpoint": "/api/data",
        "params": {"id": 123}
    })
    
    # API hívás...
```

## Debug Szintek

A rendszer a következő debug szinteket támogatja:

- **ENTRY**: Függvény belépés
- **EXIT**: Függvény kilépés
- **STEP**: Lépés a függvényen belül
- **VARIABLE**: Változó érték
- **CALL**: Függvény hívás
- **RETURN**: Függvény visszatérési érték
- **ERROR**: Hiba
- **EXCEPTION**: Kivétel teljes stack trace-tel
- **UI**: UI interakció
- **DB**: Adatbázis művelet
- **SERVICE**: Service hívás

## Debug Formátum

A debug üzenetek a következő formátumban jelennek meg:

```
[DEBUG] [TIMESTAMP] [MODULE] [FUNCTION] [LEVEL] [MESSAGE]
[DATA]
{
  "key": "value",
  ...
}
```

Példa:

```
[DEBUG] [2025-01-16 14:30:45.123] [assets_screen] [open_correct_operating_hours_dialog] [ENTRY] Entering open_correct_operating_hours_dialog
[DATA]
{
  "machine_id": 123,
  "machine_name": "Machine 1",
  "machine_type": "Machine"
}
```

## Debug Aktiválása

A debug rendszer automatikusan aktív, ha:

1. A `DEBUG=True` be van állítva az `app_config.py`-ban, vagy
2. A `DEBUG=True` be van állítva a `.env` fájlban

Ellenőrzés:

```python
from utils.debug_helper import is_debug_enabled

if is_debug_enabled():
    # Debug kód...
```

## Best Practices

### 1. Konzisztens Modul és Függvény Nevek

Használj konzisztens modul és függvény neveket:

```python
module_name = "assets_screen"  # Mindig ugyanaz a modul név
function_name = "open_correct_operating_hours_dialog"  # Függvény neve
```

### 2. Paraméterek Naplózása

Mindig naplózd a függvény paramétereit:

```python
debug_entry(module_name, function_name, {
    "param1": param1,
    "param2": param2,
    "param3": param3
})
```

### 3. Kritikus Lépések Naplózása

Naplózd a kritikus lépéseket:

```python
debug_step(module_name, function_name, "Validating input")
debug_step(module_name, function_name, "Calling external service")
debug_step(module_name, function_name, "Processing response")
```

### 4. Változók Naplózása

Naplózd az fontos változókat:

```python
debug_variable(module_name, function_name, "user_id", user_id)
debug_variable(module_name, function_name, "result", result)
```

### 5. Kivételek Naplózása

Mindig naplózd a kivételeket teljes kontextussal:

```python
except Exception as e:
    debug_exception(module_name, function_name, e, {
        "param1": param1,
        "param2": param2,
        "additional_context": "value"
    })
    raise
```

### 6. Service Hívások Naplózása

Naplózd a service hívásokat paraméterekkel és visszatérési értékekkel:

```python
debug_service(module_name, function_name, "asset_service.get_machine", {
    "machine_id": machine_id
})
machine = asset_service.get_machine(machine_id)
debug_return(module_name, function_name, "asset_service.get_machine", {
    "machine_id": machine.id,
    "machine_name": machine.name
})
```

### 7. UI Interakciók Naplózása

Naplózd a UI interakciókat:

```python
debug_ui(module_name, function_name, "Dialog opened", {
    "dialog_type": "operating_hours",
    "machine_id": machine.id
})
```

## Jövőbeli Modulokra vonatkozó Irányelvek

### Új Screen Létrehozásakor

1. Importáld a debug helper-t:

```python
from utils.debug_helper import (
    debug_entry, debug_exit, debug_step, debug_variable,
    debug_ui, debug_exception
)
```

2. Definiáld a modul nevet:

```python
module_name = "new_screen"
```

3. Naplózd a `view()` metódust:

```python
def view(self, page):
    function_name = "view"
    debug_entry(module_name, function_name, {})
    
    try:
        # Screen létrehozása...
        debug_exit(module_name, function_name, {"success": True})
    except Exception as e:
        debug_exception(module_name, function_name, e, {})
        raise
```

4. Naplózd az UI interakciókat:

```python
def on_button_click(e):
    function_name = "on_button_click"
    debug_ui(module_name, function_name, "Button clicked", {
        "button_id": e.control.data
    })
    # ...
```

### Új Service Létrehozásakor

1. Importáld a debug helper-t:

```python
from utils.debug_helper import (
    debug_entry, debug_exit, debug_step, debug_variable,
    debug_service, debug_db, debug_exception
)
```

2. Definiáld a modul nevet:

```python
module_name = "new_service"
```

3. Naplózd a service függvényeket:

```python
def process_data(data):
    function_name = "process_data"
    debug_entry(module_name, function_name, {"data": data})
    
    try:
        debug_step(module_name, function_name, "Validating data")
        # Validáció...
        
        debug_step(module_name, function_name, "Processing data")
        result = process(data)
        debug_variable(module_name, function_name, "result", result)
        
        debug_exit(module_name, function_name, {"return": result})
        return result
    except Exception as e:
        debug_exception(module_name, function_name, e, {"data": data})
        raise
```

4. Naplózd az adatbázis műveleteket:

```python
def get_user(user_id):
    function_name = "get_user"
    debug_entry(module_name, function_name, {"user_id": user_id})
    
    query = "SELECT * FROM users WHERE id = :id"
    params = {"id": user_id}
    debug_db(module_name, function_name, query, params)
    
    # Query végrehajtása...
```

## Példa: Teljes Függvény Debug-olással

```python
from utils.debug_helper import (
    debug_entry, debug_exit, debug_step, debug_variable,
    debug_call, debug_return, debug_exception, debug_service
)

def update_operating_hours(machine_id, new_hours, user_id):
    module_name = "asset_service"
    function_name = "update_operating_hours"
    
    debug_entry(module_name, function_name, {
        "machine_id": machine_id,
        "new_hours": new_hours,
        "user_id": user_id
    })
    
    try:
        debug_step(module_name, function_name, "Getting machine from database")
        debug_call(module_name, function_name, "get_machine", {"machine_id": machine_id})
        machine = get_machine(machine_id)
        debug_return(module_name, function_name, "get_machine", {
            "machine_id": machine.id,
            "current_hours": machine.operating_hours
        })
        
        debug_variable(module_name, function_name, "old_hours", machine.operating_hours)
        debug_variable(module_name, function_name, "new_hours", new_hours)
        
        debug_step(module_name, function_name, "Updating operating hours in database")
        machine.operating_hours = new_hours
        db.session.commit()
        
        debug_step(module_name, function_name, "Logging the update")
        debug_service(module_name, function_name, "log_service.log_action", {
            "action": "update_operating_hours",
            "machine_id": machine_id,
            "user_id": user_id
        })
        log_service.log_action("update_operating_hours", machine_id, user_id)
        
        debug_exit(module_name, function_name, {"success": True})
        return machine
        
    except Exception as e:
        debug_exception(module_name, function_name, e, {
            "machine_id": machine_id,
            "new_hours": new_hours,
            "user_id": user_id
        })
        raise
```

## Teljesítmény Megfontolások

- A debug rendszer csak akkor aktív, ha `DEBUG=True`
- Ha `DEBUG=False`, a debug hívások azonnal visszatérnek, nincs teljesítmény hatás
- A fájl írás aszinkron, nem blokkolja a fő szálat
- A debug üzenetek strukturáltak, könnyen elemezhetők

## Hibakeresés

Ha a debug üzenetek nem jelennek meg:

1. Ellenőrizd, hogy `DEBUG=True` az `app_config.py`-ban vagy `.env` fájlban
2. Ellenőrizd, hogy a `data/logs/` könyvtár létezik és írható
3. Ellenőrizd a konzol kimenetet
4. Ellenőrizd a `data/logs/debug.log` fájlt

## Összefoglalás

A központi debug rendszer lehetővé teszi:

- Részletes, lépésről lépésre végigkövetés
- Minden változó állapot naplózása
- Service hívások paraméterekkel és visszatérési értékekkel
- UI interakciók naplózása
- Adatbázis műveletek naplózása
- Kivételek teljes stack trace-tel
- Fájlba és konzolra egyaránt írás
- Automatikus aktiválás DEBUG módban
- Teljesítmény hatás nélkül, ha DEBUG=False

Használd konzisztensen minden új modulban és függvényben!

