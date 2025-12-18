"""
MySQL Szerver Optimalizálási Segédeszköz
Ellenőrzi és javasol optimalizálásokat a MySQL szerverhez
"""

import pymysql
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.app_config import get_database_config
except ImportError:
    # Fallback: try to read from .env file directly
    import urllib.parse
    
    def get_database_config(mode="production"):
        """Fallback database config reader"""
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
        
        if mode == "learning":
            host = os.getenv("DB_LEARN_HOST", "localhost")
            port = int(os.getenv("DB_LEARN_PORT", "3306"))
            user = os.getenv("DB_LEARN_USER", "root")
            password = os.getenv("DB_LEARN_PASSWORD", "")
            database = os.getenv("DB_LEARN_NAME", "cmms_learn")
        else:
            host = os.getenv("DB_PROD_HOST", "localhost")
            port = int(os.getenv("DB_PROD_PORT", "3306"))
            user = os.getenv("DB_PROD_USER", "root")
            password = os.getenv("DB_PROD_PASSWORD", "")
            database = os.getenv("DB_PROD_NAME", "cmms")
        
        encoded_password = urllib.parse.quote_plus(password)
        url = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        
        return {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "url": url
        }


def get_mysql_connection(mode: str = "production"):
    """Kapcsolódás a MySQL szerverhez"""
    config = get_database_config(mode)
    
    # Parse connection string
    url = config["url"]
    # Format: mysql+pymysql://user:password@host:port/database
    parts = url.replace("mysql+pymysql://", "").split("@")
    if len(parts) != 2:
        raise ValueError("Invalid database URL format")
    
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    
    if len(host_db) != 2:
        raise ValueError("Invalid database URL format")
    
    host_port = host_db[0].split(":")
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 3306
    database = host_db[1]
    
    user = user_pass[0]
    password = user_pass[1] if len(user_pass) > 1 else ""
    
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )


def check_buffer_pool(conn) -> Dict:
    """Ellenőrzi az InnoDB Buffer Pool beállításokat"""
    cursor = conn.cursor()
    
    # Buffer pool méret
    cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_size'")
    buffer_pool_size = cursor.fetchone()
    buffer_pool_size_bytes = int(buffer_pool_size['Value'])
    buffer_pool_size_gb = buffer_pool_size_bytes / (1024 ** 3)
    
    # Buffer pool instances
    cursor.execute("SHOW VARIABLES LIKE 'innodb_buffer_pool_instances'")
    instances = cursor.fetchone()
    instances_count = int(instances['Value'])
    
    # Buffer pool használat
    cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_total'")
    total_pages = cursor.fetchone()
    cursor.execute("SHOW STATUS LIKE 'Innodb_buffer_pool_pages_free'")
    free_pages = cursor.fetchone()
    
    total_pages_count = int(total_pages['Value']) if total_pages else 0
    free_pages_count = int(free_pages['Value']) if free_pages else 0
    used_pages_count = total_pages_count - free_pages_count
    usage_percent = (used_pages_count / total_pages_count * 100) if total_pages_count > 0 else 0
    
    # Ajánlás
    recommendations = []
    if buffer_pool_size_gb < 1:
        recommendations.append(
            f"⚠️ Buffer pool túl kicsi ({buffer_pool_size_gb:.2f}GB). "
            f"Ajánlott: legalább 1GB (ideális: RAM 70-80%-a)"
        )
    if instances_count < 4 and buffer_pool_size_gb >= 4:
        recommendations.append(
            f"⚠️ Buffer pool instances ({instances_count}) kevés. "
            f"Ajánlott: legalább 4 instance nagy buffer pool esetén"
        )
    
    return {
        "buffer_pool_size_gb": buffer_pool_size_gb,
        "instances": instances_count,
        "usage_percent": usage_percent,
        "recommendations": recommendations
    }


def check_connections(conn) -> Dict:
    """Ellenőrzi a kapcsolat beállításokat"""
    cursor = conn.cursor()
    
    # Max connections
    cursor.execute("SHOW VARIABLES LIKE 'max_connections'")
    max_conn = cursor.fetchone()
    max_connections = int(max_conn['Value'])
    
    # Current connections
    cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
    current_conn = cursor.fetchone()
    current_connections = int(current_conn['Value'])
    
    # Max used connections
    cursor.execute("SHOW STATUS LIKE 'Max_used_connections'")
    max_used = cursor.fetchone()
    max_used_connections = int(max_used['Value'])
    
    # Timeout settings
    cursor.execute("SHOW VARIABLES LIKE 'wait_timeout'")
    wait_timeout = cursor.fetchone()
    wait_timeout_seconds = int(wait_timeout['Value'])
    
    # Ajánlás
    recommendations = []
    if max_used_connections > max_connections * 0.8:
        recommendations.append(
            f"⚠️ Max connections ({max_connections}) közel van a maximumhoz "
            f"({max_used_connections} használva). Érdemes növelni."
        )
    if wait_timeout_seconds < 300:
        recommendations.append(
            f"⚠️ Wait timeout ({wait_timeout_seconds}s) túl alacsony. "
            f"Ajánlott: legalább 600s (10 perc)"
        )
    
    return {
        "max_connections": max_connections,
        "current_connections": current_connections,
        "max_used_connections": max_used_connections,
        "wait_timeout": wait_timeout_seconds,
        "recommendations": recommendations
    }


def check_slow_queries(conn) -> Dict:
    """Ellenőrzi a slow query beállításokat"""
    cursor = conn.cursor()
    
    # Slow query log
    cursor.execute("SHOW VARIABLES LIKE 'slow_query_log'")
    slow_log = cursor.fetchone()
    slow_query_log_enabled = slow_log['Value'] == 'ON'
    
    # Long query time
    cursor.execute("SHOW VARIABLES LIKE 'long_query_time'")
    long_query = cursor.fetchone()
    long_query_time = float(long_query['Value'])
    
    # Slow queries count
    cursor.execute("SHOW STATUS LIKE 'Slow_queries'")
    slow_queries = cursor.fetchone()
    slow_queries_count = int(slow_queries['Value']) if slow_queries else 0
    
    # Ajánlás
    recommendations = []
    if not slow_query_log_enabled:
        recommendations.append(
            "⚠️ Slow query log nincs engedélyezve. "
            "Ajánlott: engedélyezni a lassú query-k azonosításához"
        )
    if long_query_time > 2:
        recommendations.append(
            f"⚠️ Long query time ({long_query_time}s) túl magas. "
            f"Ajánlott: 2 másodperc alatt"
        )
    
    return {
        "slow_query_log_enabled": slow_query_log_enabled,
        "long_query_time": long_query_time,
        "slow_queries_count": slow_queries_count,
        "recommendations": recommendations
    }


def check_tmp_tables(conn) -> Dict:
    """Ellenőrzi a temp táblák beállításait"""
    cursor = conn.cursor()
    
    # Tmp table size
    cursor.execute("SHOW VARIABLES LIKE 'tmp_table_size'")
    tmp_size = cursor.fetchone()
    tmp_table_size_mb = int(tmp_size['Value']) / (1024 ** 2)
    
    # Max heap table size
    cursor.execute("SHOW VARIABLES LIKE 'max_heap_table_size'")
    heap_size = cursor.fetchone()
    max_heap_table_size_mb = int(heap_size['Value']) / (1024 ** 2)
    
    # Created tmp tables
    cursor.execute("SHOW STATUS LIKE 'Created_tmp_tables'")
    created_tmp = cursor.fetchone()
    created_tmp_tables = int(created_tmp['Value']) if created_tmp else 0
    
    # Created tmp disk tables
    cursor.execute("SHOW STATUS LIKE 'Created_tmp_disk_tables'")
    created_disk = cursor.fetchone()
    created_tmp_disk_tables = int(created_disk['Value']) if created_disk else 0
    
    # Ajánlás
    recommendations = []
    if tmp_table_size_mb < 64:
        recommendations.append(
            f"⚠️ Tmp table size ({tmp_table_size_mb:.0f}MB) túl kicsi. "
            f"Ajánlott: legalább 64MB (ideális: 128MB)"
        )
    if created_tmp_disk_tables > 0 and created_tmp_tables > 0:
        disk_ratio = (created_tmp_disk_tables / created_tmp_tables) * 100
        if disk_ratio > 25:
            recommendations.append(
                f"⚠️ Túl sok temp tábla kerül lemezre ({disk_ratio:.1f}%). "
                f"Növeld a tmp_table_size és max_heap_table_size értékét!"
            )
    
    return {
        "tmp_table_size_mb": tmp_table_size_mb,
        "max_heap_table_size_mb": max_heap_table_size_mb,
        "created_tmp_tables": created_tmp_tables,
        "created_tmp_disk_tables": created_tmp_disk_tables,
        "recommendations": recommendations
    }


def check_indexes(conn, database_name: str) -> Dict:
    """Ellenőrzi az indexeket"""
    cursor = conn.cursor()
    
    # Táblák listája
    cursor.execute(f"""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = '{database_name}'
        AND table_type = 'BASE TABLE'
    """)
    tables_result = cursor.fetchall()
    # Handle different column name formats (table_name vs TABLE_NAME)
    tables = []
    for row in tables_result:
        if isinstance(row, dict):
            table_name = row.get('table_name') or row.get('TABLE_NAME') or list(row.values())[0]
        else:
            table_name = row[0] if isinstance(row, (list, tuple)) else str(row)
        tables.append(table_name)
    
    # Indexek száma táblánként
    index_info = {}
    for table in tables:
        cursor.execute(f"""
            SELECT COUNT(*) as index_count
            FROM information_schema.statistics
            WHERE table_schema = '{database_name}'
            AND table_name = '{table}'
        """)
        result = cursor.fetchone()
        index_info[table] = result['index_count'] if result else 0
    
    # Ajánlás
    recommendations = []
    tables_without_indexes = [t for t, count in index_info.items() if count <= 1]
    if tables_without_indexes:
        recommendations.append(
            f"⚠️ {len(tables_without_indexes)} táblának nincs indexe vagy csak primary key-je van: "
            f"{', '.join(tables_without_indexes[:5])}"
        )
    
    return {
        "tables": len(tables),
        "index_info": index_info,
        "recommendations": recommendations
    }


def generate_optimization_report(mode: str = "production") -> str:
    """Generál egy optimalizálási jelentést"""
    try:
        conn = get_mysql_connection(mode)
        cursor = conn.cursor()
        
        # Database name
        cursor.execute("SELECT DATABASE()")
        db_result = cursor.fetchone()
        # Handle different result formats
        if isinstance(db_result, dict):
            db_name = db_result.get('DATABASE()') or db_result.get('database()') or list(db_result.values())[0]
        else:
            db_name = db_result[0] if isinstance(db_result, (list, tuple)) else str(db_result)
        
        report = []
        report.append("=" * 70)
        report.append("MySQL Szerver Optimalizálási Jelentés")
        report.append("=" * 70)
        report.append("")
        
        # Buffer pool
        report.append("📊 INNODB BUFFER POOL")
        report.append("-" * 70)
        buffer_info = check_buffer_pool(conn)
        report.append(f"Buffer Pool Méret: {buffer_info['buffer_pool_size_gb']:.2f} GB")
        report.append(f"Instances: {buffer_info['instances']}")
        report.append(f"Használat: {buffer_info['usage_percent']:.1f}%")
        if buffer_info['recommendations']:
            for rec in buffer_info['recommendations']:
                report.append(f"  {rec}")
        report.append("")
        
        # Connections
        report.append("🔌 KAPCSOLATOK")
        report.append("-" * 70)
        conn_info = check_connections(conn)
        report.append(f"Max Connections: {conn_info['max_connections']}")
        report.append(f"Jelenlegi Connections: {conn_info['current_connections']}")
        report.append(f"Max Használt: {conn_info['max_used_connections']}")
        report.append(f"Wait Timeout: {conn_info['wait_timeout']}s")
        if conn_info['recommendations']:
            for rec in conn_info['recommendations']:
                report.append(f"  {rec}")
        report.append("")
        
        # Slow queries
        report.append("🐌 SLOW QUERIES")
        report.append("-" * 70)
        slow_info = check_slow_queries(conn)
        report.append(f"Slow Query Log: {'Engedélyezve' if slow_info['slow_query_log_enabled'] else 'Letiltva'}")
        report.append(f"Long Query Time: {slow_info['long_query_time']}s")
        report.append(f"Slow Queries Száma: {slow_info['slow_queries_count']}")
        if slow_info['recommendations']:
            for rec in slow_info['recommendations']:
                report.append(f"  {rec}")
        report.append("")
        
        # Temp tables
        report.append("📋 TEMP TÁBLÁK")
        report.append("-" * 70)
        tmp_info = check_tmp_tables(conn)
        report.append(f"Tmp Table Size: {tmp_info['tmp_table_size_mb']:.0f} MB")
        report.append(f"Max Heap Table Size: {tmp_info['max_heap_table_size_mb']:.0f} MB")
        report.append(f"Létrehozott Temp Táblák: {tmp_info['created_tmp_tables']}")
        report.append(f"Létrehozott Disk Temp Táblák: {tmp_info['created_tmp_disk_tables']}")
        if tmp_info['recommendations']:
            for rec in tmp_info['recommendations']:
                report.append(f"  {rec}")
        report.append("")
        
        # Indexes
        report.append("🔍 INDEXEK")
        report.append("-" * 70)
        index_info = check_indexes(conn, db_name)
        report.append(f"Táblák Száma: {index_info['tables']}")
        report.append(f"Indexek Táblánként:")
        for table, count in list(index_info['index_info'].items())[:10]:
            report.append(f"  {table}: {count} index")
        if index_info['recommendations']:
            for rec in index_info['recommendations']:
                report.append(f"  {rec}")
        report.append("")
        
        report.append("=" * 70)
        report.append("")
        report.append("💡 TIPPEK:")
        report.append("1. A legfontosabb: növeld az innodb_buffer_pool_size értékét!")
        report.append("2. Engedélyezd a slow query log-ot a lassú query-k azonosításához")
        report.append("3. Futtasd az OPTIMIZE TABLE parancsokat rendszeresen")
        report.append("4. Lásd: docs/MYSQL_SERVER_OPTIMIZATION.md részletes útmutatásért")
        report.append("")
        
        conn.close()
        return "\n".join(report)
        
    except Exception as e:
        return f"Hiba a jelentés generálása során: {e}"


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "production"
    report = generate_optimization_report(mode)
    print(report)

