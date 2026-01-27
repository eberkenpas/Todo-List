-- Todo-List Database Schema
-- Designed for future multi-user/web extension

-- Kanban columns (e.g., Todo, In Progress, Done)
CREATE TABLE IF NOT EXISTS columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    column_id INTEGER NOT NULL,
    position INTEGER NOT NULL DEFAULT 0,
    priority INTEGER DEFAULT 2,  -- 1=low, 2=medium, 3=high
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (column_id) REFERENCES columns(id)
);

-- Default columns
INSERT INTO columns (name, position) VALUES
    ('Todo', 0),
    ('Doing', 1),
    ('Done', 2);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_tasks_column ON tasks(column_id);
CREATE INDEX IF NOT EXISTS idx_tasks_position ON tasks(column_id, position);
