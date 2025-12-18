# Performance Optimization Guide

## Overview

This document outlines the performance optimizations implemented in the CMMS system, including query optimization, caching strategies, and file operation improvements.

## Database Query Optimization

### Eager Loading

All service functions use SQLAlchemy's `joinedload` to prevent N+1 query problems:

```python
from sqlalchemy.orm import joinedload

# Example: Loading worksheets with machine and parts
worksheets = session.query(Worksheet)\
    .options(
        joinedload(Worksheet.machine),
        joinedload(Worksheet.parts),
        joinedload(Worksheet.created_by)
    )\
    .filter(Worksheet.status == "Open")\
    .all()
```

### Index Usage

All critical columns are indexed:
- Foreign keys (automatic indexes)
- Frequently queried columns (username, email, status, dates)
- Composite indexes for common query patterns

See `DATABASE_OPTIMIZATION.md` for complete index list.

### Query Patterns

#### Pattern 1: List with Pagination
```python
# Limit results to avoid loading all records
query = session.query(Worksheet)\
    .options(joinedload(Worksheet.machine))\
    .order_by(Worksheet.created_at.desc())\
    .limit(50)\
    .offset(0)
```

#### Pattern 2: Count Instead of Load
```python
from sqlalchemy import func

# Use count() instead of loading all records
count = session.query(func.count(Worksheet.id))\
    .filter(Worksheet.status == "Open")\
    .scalar()
```

#### Pattern 3: Selective Column Loading
```python
from sqlalchemy import select

# Load only needed columns
stmt = select(User.username, User.email, User.role_id)\
    .where(User.is_active == True)
result = session.execute(stmt).all()
```

## Caching Strategy

### Current Implementation

The system uses in-memory caching for:
- **User sessions**: Cached in `context_service`
- **Role permissions**: Cached per session
- **Translation data**: Loaded once at startup

### Future Caching Opportunities

1. **Dashboard Statistics**: Cache for 5 minutes
2. **Report Data**: Cache for 1 hour
3. **Template Data**: Cache template file paths
4. **Settings**: Cache app settings

## File Operation Optimization

### Document Generation

1. **Template Loading**: Templates are loaded once and reused
2. **Streaming**: Large files are streamed instead of loaded into memory
3. **Temporary Files**: Cleaned up immediately after use

### Excel Export

1. **Batch Writing**: Data written in batches, not row-by-row
2. **Memory Management**: Large datasets processed in chunks
3. **Progress Indicators**: User feedback for long operations

### Image Processing

1. **Lazy Loading**: Images loaded only when needed
2. **Thumbnail Generation**: Thumbnails generated for large images
3. **Format Optimization**: Images optimized for display size

## Memory Management

### Session Management

- Database sessions are properly closed after use
- Context managers used for automatic cleanup
- No session leaks detected

### File Handles

- All file handles are closed using `with` statements
- Temporary files are cleaned up
- No file handle leaks detected

## Performance Monitoring

### Query Performance

Enable query logging in `config/app_config.py`:
```python
DEBUG = True  # Logs all SQL queries
```

### Memory Profiling

Use Python's `memory_profiler` for memory analysis:
```bash
pip install memory-profiler
python -m memory_profiler script.py
```

### Performance Tests

Run performance tests:
```bash
pytest tests/test_performance.py -v
```

## Optimization Checklist

### Database
- [x] All foreign keys indexed
- [x] Frequently queried columns indexed
- [x] Eager loading used (joinedload)
- [x] No N+1 query problems
- [x] Pagination implemented for large lists
- [x] Count queries optimized

### File Operations
- [x] Templates loaded once and reused
- [x] Large files streamed
- [x] Temporary files cleaned up
- [x] File handles properly closed

### Memory
- [x] Sessions properly closed
- [x] No memory leaks detected
- [x] Large datasets processed in chunks

### Caching
- [x] User sessions cached
- [x] Role permissions cached
- [x] Translation data cached
- [ ] Dashboard statistics cached (future)
- [ ] Report data cached (future)

## Performance Targets

### Query Performance
- **List queries**: < 500ms for 1000 records
- **Single record**: < 50ms
- **Count queries**: < 100ms
- **Complex joins**: < 1s

### File Operations
- **PDF generation**: < 5s
- **Excel export**: < 10s for 1000 rows
- **Image processing**: < 2s per image

### Memory Usage
- **Base memory**: < 100 MB
- **Peak memory**: < 500 MB
- **Memory leaks**: None

## Monitoring and Maintenance

### Regular Tasks

1. **Weekly**: Review slow query log
2. **Monthly**: Analyze database statistics
3. **Quarterly**: Review and optimize indexes
4. **Annually**: Full performance audit

### Tools

- **Database Analyzer**: `utils/database_analyzer.py`
- **Performance Tests**: `tests/test_performance.py`
- **Query Logging**: Enable DEBUG mode
- **Memory Profiler**: `memory_profiler` package

## Best Practices

1. **Always use eager loading** for relationships
2. **Filter before joining** for better performance
3. **Use pagination** for large lists
4. **Close sessions** properly
5. **Clean up temporary files**
6. **Monitor query performance** regularly
7. **Profile memory usage** for new features

---

**Last Updated**: 2025-12-14  
**Status**: Optimized

