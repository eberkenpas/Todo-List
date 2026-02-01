#!/bin/bash
# Backup Todo-List database to home directory

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_FILE="$SCRIPT_DIR/todo.db"
BACKUP_DIR="$HOME/.todo-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/todo_$TIMESTAMP.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database not found at $DB_FILE"
    exit 1
fi

# Copy database
cp "$DB_FILE" "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup created: $BACKUP_FILE"

    # Show backup count and cleanup old backups (keep last 10)
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/todo_*.db 2>/dev/null | wc -l)
    echo "Total backups: $BACKUP_COUNT"

    if [ "$BACKUP_COUNT" -gt 10 ]; then
        # Remove oldest backups, keep last 10
        ls -1t "$BACKUP_DIR"/todo_*.db | tail -n +11 | xargs rm -f
        echo "Cleaned up old backups (keeping last 10)"
    fi
else
    echo "Error: Backup failed"
    exit 1
fi
