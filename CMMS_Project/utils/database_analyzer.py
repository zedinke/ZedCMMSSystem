"""
Database Analysis and Performance Monitoring Utilities
Provides tools for analyzing indexes, query performance, and optimization recommendations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from database.connection import engine
import json


class DatabaseAnalyzer:
    """Utility class for database analysis and optimization."""

    @staticmethod
    def list_indexes():
        """List all indexes in the database."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';"))
            indexes = []
            for row in result:
                indexes.append({
                    'name': row[0],
                    'table': row[1],
                    'sql': row[2]
                })
            return indexes

    @staticmethod
    def index_info(table_name: str):
        """Get detailed info on indexes for a specific table."""
        with engine.connect() as conn:
            result = conn.execute(text(f"PRAGMA index_info(idx_{table_name});"))
            columns = []
            for row in result:
                columns.append({
                    'sequence': row[0],
                    'column': row[1],
                    'order': row[2]
                })
            return columns

    @staticmethod
    def table_stats():
        """Get statistics on all tables (row counts, etc.)."""
        with engine.connect() as conn:
            # Get all table names
            tables_result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            )
            tables = [row[0] for row in tables_result]

            stats = {}
            for table in tables:
                count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                count = count_result.scalar()
                stats[table] = {'row_count': count}

            return stats

    @staticmethod
    def query_plan(sql: str):
        """Get EXPLAIN QUERY PLAN output for a SQL statement."""
        with engine.connect() as conn:
            result = conn.execute(text(f"EXPLAIN QUERY PLAN {sql};"))
            plan = []
            for row in result:
                plan.append({
                    'id': row[0],
                    'parent': row[1],
                    'notused': row[2],
                    'detail': row[3]
                })
            return plan

    @staticmethod
    def missing_indexes():
        """Identify potentially missing indexes based on common patterns."""
        recommendations = [
            {
                'table': 'users',
                'column': 'email',
                'reason': 'Used in login and uniqueness checks',
                'priority': 'HIGH'
            },
            {
                'table': 'worksheets',
                'column': 'assigned_to_user_id',
                'reason': 'Foreign key, used for filtering by user',
                'priority': 'MEDIUM'
            },
            {
                'table': 'parts',
                'column': 'supplier_id',
                'reason': 'Foreign key, used for inventory lookup',
                'priority': 'MEDIUM'
            },
            {
                'table': 'stock_transactions',
                'column': 'part_id',
                'reason': 'FK and heavily queried for history',
                'priority': 'HIGH'
            },
        ]
        return recommendations

    @staticmethod
    def analyze_all():
        """Run ANALYZE to gather table statistics."""
        with engine.connect() as conn:
            conn.execute(text("ANALYZE;"))
            conn.commit()
        return "Database analyzed successfully"

    @staticmethod
    def vacuum_database():
        """Run VACUUM to reclaim unused space."""
        with engine.connect() as conn:
            conn.execute(text("VACUUM;"))
            conn.commit()
        return "Database vacuumed successfully"

    @staticmethod
    def reindex_all():
        """Rebuild all indexes."""
        with engine.connect() as conn:
            conn.execute(text("REINDEX;"))
            conn.commit()
        return "All indexes rebuilt successfully"

    @staticmethod
    def generate_report():
        """Generate a comprehensive database analysis report."""
        report = {
            'indexes': DatabaseAnalyzer.list_indexes(),
            'table_stats': DatabaseAnalyzer.table_stats(),
            'recommendations': DatabaseAnalyzer.missing_indexes(),
            'timestamp': str(__import__('datetime').datetime.now().__import__('timezone').utc)
        }
        return report


def print_database_health():
    """Print a human-readable database health report."""
    analyzer = DatabaseAnalyzer()

    print("\n" + "="*60)
    print("DATABASE HEALTH REPORT")
    print("="*60)

    print("\n📊 TABLE STATISTICS:")
    print("-" * 60)
    stats = analyzer.table_stats()
    for table, data in sorted(stats.items()):
        print(f"  {table:.<40} {data['row_count']:>10} rows")

    print("\n🔍 INDEXES:")
    print("-" * 60)
    indexes = analyzer.list_indexes()
    if indexes:
        for idx in indexes:
            print(f"  {idx['name']:.<40} ON {idx['table']}")
    else:
        print("  No indexes found!")

    print("\n⚠️  OPTIMIZATION RECOMMENDATIONS:")
    print("-" * 60)
    recommendations = analyzer.missing_indexes()
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. [{rec['priority']}] {rec['table']}.{rec['column']}")
        print(f"     └─ {rec['reason']}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Example usage
    print_database_health()

    # Get detailed report
    analyzer = DatabaseAnalyzer()
    report = analyzer.generate_report()
    print("\nDetailed Report (JSON):")
    print(json.dumps(report, indent=2, default=str))
