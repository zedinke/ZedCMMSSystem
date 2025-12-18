# Alembic Migration Guide for CMMS

This folder contains all database schema migrations managed by [Alembic](https://alembic.sqlalchemy.org/), a lightweight database migration tool for SQLAlchemy.

## Quick Reference

### Initialize Alembic (Already Done)
```bash
alembic init migrations
```

### Generate a New Migration
Whenever you modify a model in `database/models.py`:

```bash
alembic revision --autogenerate -m "Your migration message"
```

**Example:**
```bash
alembic revision --autogenerate -m "Add email_verified column to users"
```

This creates a new file in `migrations/versions/` with the migration code.

### Review Migration (IMPORTANT)
Always inspect the generated migration before applying:

```bash
# View the migration file
cat migrations/versions/<revision_id>.py
```

Edit the file if needed to fix auto-generation issues.

### Apply Migrations to Database
Upgrade to the latest schema:

```bash
alembic upgrade head
```

Apply a specific number of migrations:

```bash
alembic upgrade +2  # Apply next 2 migrations
```

### Rollback Migrations
Downgrade database schema:

```bash
alembic downgrade -1      # Rollback last migration
alembic downgrade <rev>   # Rollback to specific revision
alembic downgrade base    # Rollback all migrations
```

### View Migration Status
List all migrations and their status:

```bash
alembic history --verbose
```

Current database version:

```bash
alembic current
```

---

## File Structure

```
migrations/
├── README                           # This file
├── alembic.ini                      # Alembic configuration
├── env.py                           # Migration environment setup
├── script.py.mako                   # Migration template
└── versions/
    ├── 43f00839f94b_initial_schema_with_indexes.py
    ├── <revision_id>_description.py
    └── ... (future migrations)
```

## Migration File Format

Each migration file contains:

```python
"""Description of the change

Revision ID: <auto_id>
Revises: <parent_revision_id>
Create Date: <timestamp>
"""

from alembic import op
import sqlalchemy as sa

revision = '<auto_id>'
down_revision = '<parent_revision_id>'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Schema changes to apply (forward)"""
    # op.add_column('table_name', sa.Column(...))
    # op.create_index('idx_name', 'table_name', ['column'])


def downgrade() -> None:
    """Schema changes to reverse"""
    # op.drop_index('idx_name', 'table_name')
    # op.drop_column('table_name', 'column_name')
```

---

## Common Migration Operations

### Add a Column
```python
op.add_column('users', sa.Column('new_field', sa.String(100)))
```

### Drop a Column
```python
op.drop_column('users', 'old_field')
```

### Create an Index
```python
op.create_index('idx_username', 'users', ['username'])
```

### Drop an Index
```python
op.drop_index('idx_username', 'users')
```

### Create a Table
```python
op.create_table(
    'new_table',
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(100)),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'])
)
```

### Rename a Column
```python
op.alter_column('users', 'old_name', new_column_name='new_name')
```

---

## Best Practices

1. **Always Review Generated Migrations**
   - Auto-generated migrations aren't always perfect
   - Verify logic before applying

2. **Test on Staging First**
   - Apply migration to a test database before production
   - Verify rollback procedure works

3. **Meaningful Migration Messages**
   - Use clear, descriptive messages
   - Example: `"Add must_change_password flag to users"`

4. **Keep Migrations Atomic**
   - One logical change per migration
   - Easier to rollback if issues arise

5. **Document Complex Migrations**
   - Add comments in migration file explaining the change
   - Explain why (not just what) for future maintainers

6. **Version Control**
   - Commit migration files to git
   - Migrations are part of your codebase history

---

## Troubleshooting

### Migration Won't Apply
```bash
# Check current state
alembic current

# See all revisions
alembic history --verbose

# Check for conflicts in migration files
ls migrations/versions/ | sort
```

### Need to Redo a Migration
```bash
# Downgrade to before the problematic migration
alembic downgrade <previous_revision>

# Delete the problematic migration file

# Create a new migration with the correct changes
alembic revision --autogenerate -m "Fix: corrected migration"
```

### Database is Out of Sync
If your database is manually modified and out of sync:

```bash
# Backup current database
cp data.db data.db.backup

# Downgrade to base
alembic downgrade base

# Re-apply all migrations
alembic upgrade head
```

---

## Integration with CI/CD

In your deployment script:

```bash
#!/bin/bash
set -e

# Pull latest code
git pull

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start application
python main.py
```

---

## Next Steps

1. When you modify `database/models.py`, generate a migration:
   ```bash
   alembic revision --autogenerate -m "Your change"
   ```

2. Review and test the migration on your local database

3. Commit the migration file to git

4. When deploying, the migration will be applied automatically

---

## Resources

- [Alembic Official Docs](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/20/core/types.html)
- [SQLite ALTER TABLE Limitations](https://www.sqlite.org/lang_altertable.html)
