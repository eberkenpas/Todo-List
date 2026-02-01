#!/bin/bash
# Restore Todo-List database from backup

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_FILE="$SCRIPT_DIR/todo.db"
BACKUP_DIR="$HOME/.todo-backups"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Error: No backup directory found at $BACKUP_DIR"
    exit 1
fi

# List available backups
BACKUPS=($(ls -1t "$BACKUP_DIR"/todo_*.db 2>/dev/null))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo "Error: No backups found in $BACKUP_DIR"
    exit 1
fi

echo "Available backups:"
echo ""
for i in "${!BACKUPS[@]}"; do
    FILENAME=$(basename "${BACKUPS[$i]}")
    SIZE=$(du -h "${BACKUPS[$i]}" | cut -f1)
    echo "  $((i+1)). $FILENAME ($SIZE)"
done
echo ""

read -p "Select backup to restore (1-${#BACKUPS[@]}) or 'q' to quit: " CHOICE

if [ "$CHOICE" = "q" ]; then
    echo "Cancelled"
    exit 0
fi

# Validate input
if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt ${#BACKUPS[@]} ]; then
    echo "Error: Invalid selection"
    exit 1
fi

SELECTED="${BACKUPS[$((CHOICE-1))]}"

# Confirm restore
read -p "Restore $(basename "$SELECTED")? This will overwrite current database. (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "Cancelled"
    exit 0
fi

# Restore
cp "$SELECTED" "$DB_FILE"

if [ $? -eq 0 ]; then
    echo "Restored: $(basename "$SELECTED") -> todo.db"
else
    echo "Error: Restore failed"
    exit 1
fi
