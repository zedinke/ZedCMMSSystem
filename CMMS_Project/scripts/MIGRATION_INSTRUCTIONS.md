# PM Task Attachments Migration Instructions

## SQL Migration File

A migration SQL fájl: `migrate_pm_task_attachments.sql`

## Futtatás

### Opció 1: Közvetlenül MySQL-ben
```bash
mysql -u zedin_cmms -p zedin_cmms < scripts/migrate_pm_task_attachments.sql
```

### Opció 2: SSH-n keresztül a szerveren
```bash
ssh -i ~/.ssh/zedhosting_server root@116.203.226.140
# A szerveren:
mysql -u zedin_cmms -p zedin_cmms < /path/to/migrate_pm_task_attachments.sql
```

### Opció 3: Python script-tel (amikor az adatbázis hozzáférés javítva)
```bash
python CMMS_Project/scripts/migrate_add_pm_task_attachments_table.py
```

## SQL Tartalom

```sql
CREATE TABLE IF NOT EXISTS pm_task_attachments (
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Megjegyzés

Az automatikus migration script nem futott le, mert az adatbázis hozzáférési hiba volt (1045 Access denied). Ez azt jelenti, hogy:
1. A MySQL jelszó nem megfelelő, VAGY
2. A MySQL csak bizonyos IP címekről engedélyezi a kapcsolatot

Javítsd az adatbázis hozzáférési beállításokat, vagy futtasd le manuálisan az SQL-t.

