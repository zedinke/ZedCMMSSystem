# Service Function Docstring Template

**Dátum**: 2025.12.18  
**Cél**: Egységes docstring formátum minden service függvényhez

---

## 📋 STANDARD DOCSTRING FORMÁTUM

### Teljes Formátum (Ajánlott fontos függvényekhez)

```python
def service_function(
    param1: Type,
    param2: Optional[Type] = None,
    session: Session = None
) -> ReturnType:
    """
    Rövid leírás (egy mondat).
    
    Részletes leírás, ha szükséges. Leírja, mit csinál a függvény,
    milyen műveleteket hajt végre, és milyen mellékhatásai vannak.
    
    Workflow/Process:
    1. Első lépés
    2. Második lépés
    3. Harmadik lépés
    
    Args:
        param1: Rövid leírás a paraméterről. Ha van validációs szabály,
                azt is jelezni (pl. "Must be positive integer").
        param2: Rövid leírás. Default érték magyarázata, ha releváns.
        session: Database session. Ha None, új session-t hoz létre
                és bezárja a művelet után.
    
    Returns:
        ReturnType: Rövid leírás, mit ad vissza. Ha komplex objektum,
                   jelezni, milyen mezőket tartalmaz.
    
    Raises:
        ValidationError: Mikor dobódik (pl. "If param1 is negative").
        NotFoundError: Mikor dobódik (pl. "If entity with param1 ID not found").
        BusinessLogicError: Mikor dobódik (pl. "If business rule violated").
        StateTransitionError: Mikor dobódik (pl. "If invalid state transition").
    
    Example:
        >>> result = service_function(123, param2="value")
        >>> print(result.id)
        456
    
    Note:
        Speciális megjegyzések, ha vannak (pl. "This function is deprecated").
    """
```

### Egyszerűsített Formátum (Egyszerű CRUD műveletekhez)

```python
def simple_function(param: Type, session: Session = None) -> ReturnType:
    """
    Rövid leírás (egy mondat).
    
    Args:
        param: Rövid leírás.
        session: Database session (optional).
    
    Returns:
        ReturnType: Rövid leírás.
    
    Raises:
        NotFoundError: Ha az entitás nem található.
    """
```

---

## 📝 PÉLDÁK

### Példa 1: Create Function

```python
def create_pm_task(
    machine_id: Optional[int],
    task_name: str,
    frequency_days: Optional[int],
    task_description: Optional[str] = None,
    assigned_to_user_id: Optional[int] = None,
    priority: str = "normal",
    status: str = "pending",
    due_date: Optional[datetime] = None,
    estimated_duration_minutes: Optional[int] = None,
    created_by_user_id: Optional[int] = None,
    location: Optional[str] = None,
    task_type: str = "recurring",
    session: Session = None
) -> PMTask:
    """
    Create a new PM (Preventive Maintenance) task.
    
    This function creates a PM task for a specific machine. The task can be either
    recurring (with frequency_days) or one-time (task_type="one_time").
    
    Workflow:
    1. Validates machine exists (if machine_id provided)
    2. Validates workflow state transition
    3. Creates PMTask record
    4. Sends notification (if assigned_to_user_id provided)
    5. Generates Work Request PDF
    6. Logs action to SystemLog
    
    Args:
        machine_id: ID of the machine this PM task is for. If None, location must be provided.
        task_name: Name/description of the PM task (required).
        frequency_days: How often this task should be performed (for recurring tasks).
        task_description: Detailed description of the task.
        assigned_to_user_id: User ID to assign the task to. If None, task is globally assigned.
        priority: Task priority. Must be one of: "low", "normal", "high", "urgent".
                 Default: "normal".
        status: Initial status. Must be valid PMTask state. Default: "pending".
        due_date: Due date for the task. If None, calculated from frequency_days.
        estimated_duration_minutes: Estimated time to complete in minutes.
        created_by_user_id: User ID who created this task.
        location: Location where task should be performed. Required if machine_id is None.
        task_type: "recurring" or "one_time". Default: "recurring".
        session: Database session. If None, creates new session and closes it after.
    
    Returns:
        PMTask: Created PM task object with all relationships loaded.
    
    Raises:
        NotFoundError: If machine with machine_id not found, or user with 
                      assigned_to_user_id/created_by_user_id not found.
        ValidationError: If machine_id and location both None, or invalid priority/status values.
        StateTransitionError: If invalid state transition for initial status.
        BusinessLogicError: If business rules violated.
    
    Example:
        >>> task = create_pm_task(
        ...     machine_id=1,
        ...     task_name="Monthly oil change",
        ...     frequency_days=30,
        ...     priority="normal",
        ...     created_by_user_id=1
        ... )
        >>> print(task.id)
        42
    
    Note:
        - Automatically generates Work Request PDF after creation.
        - Sends notification to assigned user (or all active users if globally assigned).
        - Logs action to SystemLog for audit trail.
    """
```

### Példa 2: Update Function

```python
def update_pm_task(task_id: int, **kwargs) -> PMTask:
    """
    Update an existing PM task.
    
    Updates specified fields of a PM task. Only provided fields are updated.
    Tracks changes for version history and logging.
    
    Args:
        task_id: ID of the PM task to update (required).
        **kwargs: Fields to update. Valid fields: task_name, status, priority,
                 assigned_to_user_id, due_date, etc. Only provided fields are updated.
    
    Returns:
        PMTask: Updated PM task object.
    
    Raises:
        NotFoundError: If PM task with task_id not found.
        ValidationError: If any provided field value is invalid.
        StateTransitionError: If status change violates workflow rules.
    
    Note:
        - If assigned_to_user_id changes, sends notification to new assignee.
        - Logs changes to SystemLog with change tracking.
    """
```

### Példa 3: Complex Function with Workflow

```python
def complete_pm_task(
    task_id: int,
    completed_by_user_id: int,
    notes: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    create_worksheet: bool = True,
    session: Session = None
) -> tuple[PMHistory, Optional[int]]:
    """
    Complete a PM task and optionally create a worksheet.
    
    This function marks a PM task as completed and optionally creates a worksheet
    for the maintenance work. It generates required documents (Work Request PDF,
    PM Worksheet PDF, Scrapping Documents if parts used).
    
    Workflow:
    1. Validates task exists and transition to "completed" is allowed
    2. Creates PMHistory record with completion details
    3. Updates task status and next_due_date (for recurring tasks)
    4. Creates Worksheet (if create_worksheet=True and machine_id set)
    5. Generates PM Worksheet PDF
    6. Sends completion notification
    7. Logs action to SystemLog
    
    Args:
        task_id: ID of the PM task to complete (required).
        completed_by_user_id: User ID who completed the task (required).
        notes: Completion notes/observations.
        duration_minutes: Actual duration in minutes.
        create_worksheet: If True, creates Worksheet for the completion.
                         Only created if task has machine_id set.
        session: Database session. If None, creates new session.
    
    Returns:
        Tuple of (PMHistory, worksheet_id):
        - PMHistory: Created history record with completion details.
        - worksheet_id: ID of created worksheet, or None if not created.
    
    Raises:
        NotFoundError: If PM task with task_id not found, or user not found.
        StateTransitionError: If transition from current status to "completed" is invalid.
        BusinessLogicError: If business rules violated.
    
    Example:
        >>> history, worksheet_id = complete_pm_task(
        ...     task_id=1,
        ...     completed_by_user_id=5,
        ...     notes="Completed successfully",
        ...     duration_minutes=120
        ... )
        >>> print(history.id)
        42
    
    Note:
        - For one-time tasks, marks task as inactive after completion.
        - For recurring tasks, calculates next_due_date from frequency_days.
        - Automatically generates PM Worksheet PDF.
        - Sends notification to completing user and shift leaders/managers.
    """
```

---

## 📋 KATEGÓRIÁK SZERINTI DOCSTRING KÖVETELMÉNYEK

### Create Functions (create_*)
- ✅ Rövid leírás
- ✅ Args részletesen (különösen required paraméterek)
- ✅ Workflow/Process lépések
- ✅ Returns részletesen
- ✅ Raises részletesen
- ✅ Example (opcionális, de ajánlott)

### Update Functions (update_*)
- ✅ Rövid leírás
- ✅ Args (különösen a változtatható mezők)
- ✅ Returns
- ✅ Raises
- ✅ Note (ha van change tracking, notification, stb.)

### Delete/Remove Functions
- ✅ Rövid leírás
- ✅ Args
- ✅ Returns (pl. bool, vagy None)
- ✅ Raises (különösen, ha van dependency check)
- ✅ Note (ha soft delete, vagy cascade)

### Query/List Functions (list_*, get_*, find_*)
- ✅ Rövid leírás
- ✅ Args (filters, pagination, stb.)
- ✅ Returns részletesen (mit tartalmaz a lista/objektum)
- ⚠️ Raises (általában nincs, vagy csak NotFoundError)

### Complex Functions (complete_*, process_*, calculate_*)
- ✅ Rövid leírás
- ✅ Részletes leírás
- ✅ Workflow/Process lépések (fontos!)
- ✅ Args részletesen
- ✅ Returns részletesen
- ✅ Raises részletesen
- ✅ Example (ajánlott)
- ✅ Note (speciális megjegyzések)

---

## ✅ ELLENŐRZÉSI LISTA

Minden függvény docstring-jének tartalmaznia kell:

- [ ] Rövid leírás (egy mondat)
- [ ] Args rész (legalább a required paraméterek)
- [ ] Returns rész
- [ ] Raises rész (ha van exception)
- [ ] Workflow/Process (komplex függvényeknél)
- [ ] Example (ajánlott fontos függvényeknél)
- [ ] Note (ha van speciális megjegyzés)

---

**Megjegyzés:** Ez egy folyamatos javítási folyamat. Az új függvényeknél már használjuk ezt a formátumot.

