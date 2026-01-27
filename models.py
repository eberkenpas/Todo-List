"""Task and Column data operations."""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from db import get_connection


@dataclass
class Column:
    id: int
    name: str
    position: int
    created_at: datetime


@dataclass
class Task:
    id: int
    title: str
    description: Optional[str]
    column_id: int
    position: int
    priority: int
    due_date: Optional[date]
    created_at: datetime
    updated_at: datetime


# Column operations

def get_all_columns() -> list[Column]:
    """Get all columns ordered by position."""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM columns ORDER BY position")
    columns = [Column(**dict(row)) for row in cursor.fetchall()]
    conn.close()
    return columns


def get_column_by_name(name: str) -> Optional[Column]:
    """Get a column by name (case-insensitive)."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM columns WHERE LOWER(name) = LOWER(?)", (name,)
    )
    row = cursor.fetchone()
    conn.close()
    return Column(**dict(row)) if row else None


# Task operations

def get_tasks_by_column(column_id: int) -> list[Task]:
    """Get all tasks in a column ordered by position."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM tasks WHERE column_id = ? ORDER BY position",
        (column_id,)
    )
    tasks = [Task(**dict(row)) for row in cursor.fetchall()]
    conn.close()
    return tasks


def get_all_tasks() -> list[Task]:
    """Get all tasks."""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM tasks ORDER BY column_id, position")
    tasks = [Task(**dict(row)) for row in cursor.fetchall()]
    conn.close()
    return tasks


def get_task_by_id(task_id: int) -> Optional[Task]:
    """Get a task by ID."""
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return Task(**dict(row)) if row else None


def add_task(
    title: str,
    column_name: str = "Todo",
    description: Optional[str] = None,
    priority: int = 2,
    due_date: Optional[str] = None
) -> Task:
    """Add a new task to a column."""
    column = get_column_by_name(column_name)
    if not column:
        raise ValueError(f"Column '{column_name}' not found")

    conn = get_connection()

    # Get next position in column
    cursor = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM tasks WHERE column_id = ?",
        (column.id,)
    )
    position = cursor.fetchone()[0]

    cursor = conn.execute(
        """INSERT INTO tasks (title, description, column_id, position, priority, due_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, column.id, position, priority, due_date)
    )
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def move_task(task_id: int, target_column_name: str) -> Task:
    """Move a task to a different column."""
    task = get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    column = get_column_by_name(target_column_name)
    if not column:
        raise ValueError(f"Column '{target_column_name}' not found")

    conn = get_connection()

    # Get next position in target column
    cursor = conn.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM tasks WHERE column_id = ?",
        (column.id,)
    )
    position = cursor.fetchone()[0]

    conn.execute(
        """UPDATE tasks
           SET column_id = ?, position = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?""",
        (column.id, position, task_id)
    )
    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[int] = None,
    due_date: Optional[str] = None
) -> Task:
    """Update a task's details."""
    task = get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")

    conn = get_connection()

    updates = []
    params = []

    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        updates.append("due_date = ?")
        params.append(due_date)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(task_id)
        conn.execute(
            f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()

    conn.close()
    return get_task_by_id(task_id)


def delete_task(task_id: int) -> bool:
    """Delete a task."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
