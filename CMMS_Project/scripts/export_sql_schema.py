"""
Export SQLAlchemy models to MySQL-compatible SQL schema
Generates complete CREATE TABLE statements with indexes and constraints
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, MetaData
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy.dialects import mysql
from database.models import Base
import re


def convert_sqlite_to_mysql_sql(sql: str) -> str:
    """
    Convert SQLite-specific SQL to MySQL-compatible SQL
    """
    # Remove SQLite-specific syntax
    sql = re.sub(r'\bINTEGER\b', 'INT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bTEXT\b', 'TEXT', sql, flags=re.IGNORECASE)
    
    # Convert AUTOINCREMENT to AUTO_INCREMENT
    sql = re.sub(r'\bAUTOINCREMENT\b', 'AUTO_INCREMENT', sql, flags=re.IGNORECASE)
    
    # Remove SQLite-specific column constraints that MySQL doesn't support
    # SQLite uses INTEGER PRIMARY KEY for auto-increment, MySQL uses AUTO_INCREMENT
    sql = re.sub(r'INTEGER PRIMARY KEY(?!\s+AUTO_INCREMENT)', 'INT PRIMARY KEY AUTO_INCREMENT', sql, flags=re.IGNORECASE)
    
    # Convert boolean defaults
    sql = re.sub(r"DEFAULT\s+1\b", "DEFAULT TRUE", sql, flags=re.IGNORECASE)
    sql = re.sub(r"DEFAULT\s+0\b", "DEFAULT FALSE", sql, flags=re.IGNORECASE)
    
    # MySQL uses different syntax for JSON - keep as JSON
    # MySQL 5.7+ supports JSON type
    
    # Convert datetime defaults
    # Remove SQLite-specific datetime functions if any
    
    return sql


def export_mysql_schema(output_file: Path):
    """
    Export all SQLAlchemy models to MySQL-compatible SQL
    """
    # Create a MySQL dialect for SQL generation (no actual connection needed)
    from sqlalchemy.dialects import mysql
    dialect = mysql.dialect()
    
    # Use a mock engine approach - compile SQL with dialect directly
    # This avoids needing actual database connection or pymysql driver
    
    # Get metadata from Base
    metadata = Base.metadata
    
    sql_statements = []
    
    # Add header
    sql_statements.append("-- CMMS Database Schema for MySQL")
    sql_statements.append("-- Generated from SQLAlchemy models")
    sql_statements.append("-- MySQL 5.7+ / MariaDB 10.2+ compatible")
    sql_statements.append("")
    sql_statements.append("SET FOREIGN_KEY_CHECKS=0;")
    sql_statements.append("SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';")
    sql_statements.append("SET AUTOCOMMIT=0;")
    sql_statements.append("START TRANSACTION;")
    sql_statements.append("SET time_zone='+00:00';")
    sql_statements.append("")
    
    # Generate CREATE TABLE statements
    # Sort tables to respect foreign key dependencies
    tables_to_create = []
    tables_created = set()
    
    def get_table_dependencies(table, visited=None):
        """Get list of tables this table depends on"""
        if visited is None:
            visited = set()
        
        # Prevent infinite recursion
        if table.name in visited:
            return set()
        
        visited.add(table.name)
        deps = set()
        
        for fk in table.foreign_keys:
            referenced_table = fk.column.table
            # Skip self-references (circular dependencies)
            if referenced_table.name != table.name and referenced_table.name not in tables_created:
                deps.add(referenced_table.name)
                # Recursively get dependencies, but skip already visited tables
                new_visited = visited.copy()
                deps.update(get_table_dependencies(referenced_table, new_visited))
        
        return deps
    
    # Sort tables by dependencies
    remaining_tables = list(metadata.tables.values())
    while remaining_tables:
        progress = False
        for table in remaining_tables[:]:
            deps = get_table_dependencies(table)
            if not deps or all(dep in tables_created for dep in deps):
                tables_to_create.append(table)
                tables_created.add(table.name)
                remaining_tables.remove(table)
                progress = True
        if not progress:
            # Circular dependency or orphaned table, just add it
            table = remaining_tables.pop(0)
            tables_to_create.append(table)
            tables_created.add(table.name)
    
    # Generate CREATE TABLE statements
    for table in tables_to_create:
        sql_statements.append(f"-- Table: {table.name}")
        
        # Create table statement - compile with MySQL dialect
        create_table_sql = str(CreateTable(table).compile(dialect=dialect))
        
        # Convert to MySQL syntax
        create_table_sql = convert_sqlite_to_mysql_sql(create_table_sql)
        
        # MySQL specific adjustments
        # Replace BOOL/BOOLEAN with TINYINT(1) for better MySQL compatibility
        create_table_sql = re.sub(r'\bBOOL\b', 'TINYINT(1)', create_table_sql, flags=re.IGNORECASE)
        create_table_sql = re.sub(r'\bBOOLEAN\b', 'TINYINT(1)', create_table_sql, flags=re.IGNORECASE)
        
        # Ensure AUTO_INCREMENT is properly placed
        if 'AUTO_INCREMENT' not in create_table_sql.upper():
            # Check if there's an INTEGER PRIMARY KEY
            if re.search(r'INT.*PRIMARY KEY', create_table_sql, re.IGNORECASE):
                create_table_sql = re.sub(
                    r'(INT\s+PRIMARY KEY)',
                    r'\1 AUTO_INCREMENT',
                    create_table_sql,
                    flags=re.IGNORECASE,
                    count=1
                )
        
        sql_statements.append(create_table_sql)
        sql_statements.append("")
    
    # Generate CREATE INDEX statements (for indexes defined in __table_args__)
    sql_statements.append("-- Indexes")
    sql_statements.append("")
    
    for table in metadata.tables.values():
        for index in table.indexes:
            # Skip indexes that are automatically created (unique constraints, etc.)
            if index.name.startswith('ix_') or index.name.startswith('idx_'):
                # Create index statement - compile with MySQL dialect
                create_index_sql = str(CreateIndex(index).compile(dialect=dialect))
                create_index_sql = convert_sqlite_to_mysql_sql(create_index_sql)
                sql_statements.append(create_index_sql)
    
    sql_statements.append("")
    sql_statements.append("SET FOREIGN_KEY_CHECKS=1;")
    sql_statements.append("COMMIT;")
    
    # Write to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_statements))
    
    print(f"✓ SQL schema exported to: {output_file}")
    print(f"✓ Total tables: {len(metadata.tables)}")


def main():
    """Main entry point"""
    output_file = PROJECT_ROOT / "database" / "cmms_schema.sql"
    
    print("Exporting SQLAlchemy models to MySQL schema...")
    print(f"Output file: {output_file}")
    
    try:
        export_mysql_schema(output_file)
        print("\n✓ Export completed successfully!")
        print(f"\nTo import into MySQL:")
        print(f"  mysql -u zedin_cmms -p zedin_cmms < {output_file}")
        
    except Exception as e:
        print(f"\n✗ Error exporting schema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

