"""
Remote migration script - to be run on server via SSH
This script will be executed on the remote server to create the table
"""

import sys
import os

# This will be run on remote server, so we need to handle imports differently
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    try:
        import MySQLdb
        MYSQL_AVAILABLE = True
    except ImportError:
        pass

def migrate_remote():
    """Create pm_task_attachments table - to be run on remote server"""
    if not MYSQL_AVAILABLE:
        print("ERROR: Neither pymysql nor MySQLdb is available")
        return False
    
    # Database connection details - passed as environment variables or command line args
    import os
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'zedin_cmms')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'zedin_cmms')
    
    try:
        if 'pymysql' in sys.modules or 'pymysql' in str(sys.modules):
            import pymysql
            conn = pymysql.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name,
                charset='utf8mb4'
            )
        else:
            import MySQLdb
            conn = MySQLdb.connect(
                host=db_host,
                user=db_user,
                passwd=db_password,
                db=db_name,
                charset='utf8mb4'
            )
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = 'pm_task_attachments'
        """)
        result = cursor.fetchone()
        table_exists = result[0] > 0 if result else False
        
        if table_exists:
            print("SKIP: Table pm_task_attachments already exists")
            cursor.close()
            conn.close()
            return True
        
        # Create table
        create_sql = """
            CREATE TABLE pm_task_attachments (
                id INT NOT NULL AUTO_INCREMENT,
                pm_history_id INT NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(50) NOT NULL,
                file_size INT,
                description TEXT,
                uploaded_at DATETIME,
                uploaded_by_user_id INT,
                PRIMARY KEY (id),
                FOREIGN KEY(pm_history_id) REFERENCES pm_histories (id) ON DELETE CASCADE,
                FOREIGN KEY(uploaded_by_user_id) REFERENCES users (id),
                INDEX idx_pm_attachment_history (pm_history_id),
                INDEX idx_pm_attachment_uploaded_at (uploaded_at)
            )
        """
        
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("SUCCESS: Table pm_task_attachments created successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_remote()
    sys.exit(0 if success else 1)

