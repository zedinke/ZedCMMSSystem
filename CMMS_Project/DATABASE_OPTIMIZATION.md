# Database Optimization Guide

## Overview
This document outlines the database optimization strategies, indexing scheme, and migration management for the CMMS system.

---

## 1. Database Indexes

### Implemented Indexes

#### User Table (`users`)
- **Index on `username`** – Used for login queries and user lookups
  ```sql
  CREATE INDEX idx_username ON users(username);
  ```
- **Unique constraint on `email`** – Ensures email uniqueness; provides index coverage
- **Foreign key on `role_id`** – Implicit index via FK constraint

**Rationale:** Username and email are high-traffic lookup fields in authentication.

#### Machine Table (`machines`)
- **Index on `production_line_id`** – Links machines to production lines
- **Index on `serial_number`** – For asset lookup by serial

**Rationale:** Common filtering by production line and serial number searches.

#### Worksheet Table (`worksheets`)
- **Index on `machine_id`** – Link to machines
- **Index on `status`** – Filter by Open/Waiting/Closed
- **Index on `created_at`** – Time-based queries and sorting

**Rationale:** Worksheets are frequently queried by machine, status, and date range.

#### Audit Logs (`audit_logs`)
- **Index on `timestamp`** – Time range queries for audit trails
- **Composite index on `(entity_type, entity_id)`** – Entity-specific audit lookup

**Rationale:** Audit queries typically filter by entity type and time range.

#### Inventory Tables (`parts`, `stock_transactions`)
- **Index on `sku`** – SKU lookups for parts
- **Index on `part_id`** in `stock_transactions` – Trace stock history
- **Composite index on `(reference_id, reference_type)`** – Link transactions to worksheets

**Rationale:** Inventory is a frequent lookup hot-spot for stock checks.

#### Preventive Maintenance (`pm_tasks`, `pm_histories`)
- **Index on `next_due_date`** in `pm_tasks` – Find overdue PM tasks
- **Index on `executed_date`** in `pm_histories` – Historical PM data

**Rationale:** PM scheduling requires fast retrieval of upcoming or overdue tasks.

---

## 2. Query Optimization

### SQLAlchemy Best Practices

#### Eager Loading
Always use `.options(joinedload(...))` to avoid N+1 queries:

```python
# Good: Single query with JOIN
users = session.query(User).options(joinedload(User.role)).all()

# Avoid: N+1 queries (one per user)
users = session.query(User).all()
for u in users:
    print(u.role.name)  # Triggers separate query
```

#### Selective Column Loading
Use `select()` with specific columns when full entities aren't needed:

```python
from sqlalchemy import select

# Load only username and email
stmt = select(User.username, User.email).where(User.is_active == True)
result = session.execute(stmt).all()
```

#### Filter Before Join
Apply filters on parent entity before joining:

```python
# Good: Filter early
query = session.query(Worksheet)\
    .filter(Worksheet.status == "Open")\
    .options(joinedload(Worksheet.machine))

# Less efficient: Filter after join
query = session.query(Worksheet)\
    .options(joinedload(Worksheet.machine))\
    .filter(Worksheet.status == "Open")  # Applied later
```

---

## 3. Database Migration Management (Alembic)

### Quick Start

#### Create a New Migration
When you modify models (add column, create table, etc.):

```bash
cd CMMS_Project
alembic revision --autogenerate -m "Add new_column to users table"
```

This generates a migration file in `migrations/versions/`.

#### Review Migration
Always review the generated migration before applying:

```bash
# View migration file
cat migrations/versions/<migration_id>.py
```

Edit if needed to fix auto-generation limitations.

#### Apply Migrations
To update the database schema:

```bash
alembic upgrade head
```

#### Rollback Migrations
Revert to a previous version:

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>
```

#### View Migration History
List all applied migrations:

```bash
alembic history
```

---

## 4. Performance Monitoring

### Query Logging
Enable query logging by setting `DEBUG=True` in `config/app_config.py`:

```python
DEBUG = True  # SQLAlchemy will echo all queries
```

Monitor logs to identify slow queries and missing indexes.

### Index Usage Analysis
For SQLite, check if indexes are being used:

```sql
EXPLAIN QUERY PLAN
SELECT * FROM users WHERE username = 'admin';
```

If output shows a table scan instead of index, consider adding/optimizing the index.

---

## 5. Common Optimization Patterns

### Pattern 1: List with Relationships
```python
# Efficient: Single query with all relationships
users = session.query(User)\
    .options(
        joinedload(User.role),
        joinedload(User.worksheets)
    )\
    .all()
```

### Pattern 2: Count with Filters
```python
# Efficient: Use count() on filtered query
from sqlalchemy import func

count = session.query(func.count(Worksheet.id))\
    .filter(Worksheet.status == "Open")\
    .scalar()
```

### Pattern 3: Bulk Updates
```python
# Efficient: Single update statement
session.query(InventoryLevel)\
    .filter(InventoryLevel.quantity_on_hand < Part.safety_stock)\
    .update({InventoryLevel.quantity_reserved: 0})
session.commit()
```

---

## 6. Database Maintenance

### Periodic Tasks

1. **Analyze Table Statistics** (Weekly)
   ```sql
   ANALYZE;
   ```

2. **Vacuum Database** (Monthly)
   ```sql
   VACUUM;
   ```
   Reclaims unused space and optimizes file size.

3. **Rebuild Indexes** (Quarterly)
   ```sql
   REINDEX;
   ```
   Rebuilds all indexes to maintain performance.

---

## 7. Index Size Monitoring

For SQLite, check index sizes:

```sql
SELECT
    name,
    SUM(pgsize) as size_bytes
FROM dbstat
WHERE name LIKE 'idx_%'
GROUP BY name
ORDER BY size_bytes DESC;
```

Remove unused indexes to reduce memory footprint.

---

## 8. Migration Naming Conventions

Follow this pattern for migration messages:

- `"Add column X to table Y"`
- `"Create table Z"`
- `"Add index on table.column"`
- `"Drop unused column"`
- `"Rename table X to Y"`

Example:
```bash
alembic revision --autogenerate -m "Add composite index on worksheet(machine_id, status)"
```

---

## 9. Rollout Checklist

Before deploying database changes:

- [ ] Review migration file for correctness
- [ ] Test migration on staging database
- [ ] Verify rollback procedure works
- [ ] Communicate downtime to users (if needed)
- [ ] Backup production database
- [ ] Apply migration
- [ ] Monitor performance after deployment

---

## 10. References

- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLite Query Planner](https://www.sqlite.org/queryplanner.html)
- [Index Design Best Practices](https://use-the-index-luke.com/)
