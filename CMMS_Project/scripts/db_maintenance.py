#!/usr/bin/env python
"""
Database Maintenance Utility Script
Performs common database maintenance tasks (cleanup, analysis, optimization).
"""

import sys
import os
import argparse
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.database_analyzer import DatabaseAnalyzer, print_database_health
from database.connection import engine


def analyze():
    """Run database analysis."""
    print("\n📊 ANALYZING DATABASE...")
    print("=" * 60)
    print_database_health()
    print("\nReport saved. Review the output for optimization opportunities.")


def vacuum():
    """Clean up database and reclaim space."""
    print("\n🧹 VACUUMING DATABASE...")
    print("=" * 60)
    try:
        result = DatabaseAnalyzer.vacuum_database()
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Error: {e}")


def analyze_tables():
    """Update table statistics."""
    print("\n📈 ANALYZING TABLE STATISTICS...")
    print("=" * 60)
    try:
        result = DatabaseAnalyzer.analyze_all()
        print(f"✅ {result}")
        print("\nTable statistics updated. Indexes will perform better now.")
    except Exception as e:
        print(f"❌ Error: {e}")


def reindex():
    """Rebuild all indexes."""
    print("\n🔧 REBUILDING INDEXES...")
    print("=" * 60)
    try:
        result = DatabaseAnalyzer.reindex_all()
        print(f"✅ {result}")
        print("\nAll indexes rebuilt. Query performance optimized.")
    except Exception as e:
        print(f"❌ Error: {e}")


def full_maintenance():
    """Run full maintenance cycle."""
    print("\n🚀 RUNNING FULL MAINTENANCE...")
    print("=" * 60)
    
    print("\n[1/4] Updating table statistics...")
    try:
        DatabaseAnalyzer.analyze_all()
        print("  ✅ Done")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n[2/4] Rebuilding indexes...")
    try:
        DatabaseAnalyzer.reindex_all()
        print("  ✅ Done")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n[3/4] Vacuuming database...")
    try:
        DatabaseAnalyzer.vacuum_database()
        print("  ✅ Done")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n[4/4] Running final analysis...")
    print_database_health()
    
    print("\n" + "=" * 60)
    print("✅ MAINTENANCE COMPLETE!")
    print("=" * 60 + "\n")


def list_indexes():
    """List all indexes."""
    print("\n🔍 DATABASE INDEXES")
    print("=" * 60)
    indexes = DatabaseAnalyzer.list_indexes()
    
    if not indexes:
        print("No indexes found!")
    else:
        # Group by table
        by_table = {}
        for idx in indexes:
            table = idx['table']
            if table not in by_table:
                by_table[table] = []
            by_table[table].append(idx)
        
        for table in sorted(by_table.keys()):
            print(f"\n{table}:")
            for idx in by_table[table]:
                print(f"  • {idx['name']}")
                if idx['sql']:
                    print(f"    {idx['sql'][:70]}...")


def show_recommendations():
    """Show optimization recommendations."""
    print("\n⚡ OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    recommendations = DatabaseAnalyzer.missing_indexes()
    
    print("\nConsider adding the following indexes:\n")
    for i, rec in enumerate(recommendations, 1):
        priority_icon = "🔴" if rec['priority'] == "HIGH" else "🟡"
        print(f"{priority_icon} [{rec['priority']}] {rec['table']}.{rec['column']}")
        print(f"   Reason: {rec['reason']}\n")


def get_stats():
    """Get database statistics."""
    print("\n📊 DATABASE STATISTICS")
    print("=" * 60)
    stats = DatabaseAnalyzer.table_stats()
    
    total_rows = 0
    print("\nTable Row Counts:\n")
    for table in sorted(stats.keys()):
        count = stats[table]['row_count']
        total_rows += count
        if count == 0:
            print(f"  {table:.<45} {count:>5} rows (empty)")
        elif count > 1000:
            print(f"  {table:.<45} {count:>5} rows ⚠️")
        else:
            print(f"  {table:.<45} {count:>5} rows ✅")
    
    print(f"\n{'Total Rows':.<45} {total_rows:>5}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Database Maintenance Utility for CMMS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/db_maintenance.py --analyze          # Show database health
  python scripts/db_maintenance.py --full             # Run all maintenance
  python scripts/db_maintenance.py --vacuum           # Clean up database
  python scripts/db_maintenance.py --stats            # Show table statistics
        """
    )
    
    parser.add_argument('--analyze', action='store_true', help='Analyze database and show recommendations')
    parser.add_argument('--vacuum', action='store_true', help='Vacuum database (cleanup/reclaim space)')
    parser.add_argument('--analyze-tables', action='store_true', help='Update table statistics')
    parser.add_argument('--reindex', action='store_true', help='Rebuild all indexes')
    parser.add_argument('--full', action='store_true', help='Run full maintenance (analyze + reindex + vacuum)')
    parser.add_argument('--list-indexes', action='store_true', help='List all indexes')
    parser.add_argument('--recommendations', action='store_true', help='Show optimization recommendations')
    parser.add_argument('--stats', action='store_true', help='Show table statistics')
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "=" * 60)
    print("🗄️  CMMS DATABASE MAINTENANCE UTILITY")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # If no action specified, show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # Execute requested action
    if args.analyze:
        analyze()
    elif args.vacuum:
        vacuum()
    elif args.analyze_tables:
        analyze_tables()
    elif args.reindex:
        reindex()
    elif args.full:
        full_maintenance()
    elif args.list_indexes:
        list_indexes()
    elif args.recommendations:
        show_recommendations()
    elif args.stats:
        get_stats()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
