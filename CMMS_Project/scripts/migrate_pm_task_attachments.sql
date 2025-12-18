-- Migration: Create pm_task_attachments table

-- Check if table exists and create if not
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

