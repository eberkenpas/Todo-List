# Todo-List

A terminal-based Kanban board for personal task management, built in Python.

## Features

- Interactive full-screen TUI (Terminal User Interface)
- Three columns: Todo, Doing, Done
- Pick-up and place task movement with visual feedback
- Color-coded columns (Cyan, Yellow, Green)
- SQLite storage for persistence
- Responsive layout (scales to terminal size)
- Vim keybindings support
- Designed for future extension to a shared web application

## Installation

```bash
cd /path/to/Todo-List

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
./todo
```

The `./todo` launcher script handles the virtual environment automatically.

### Keyboard Controls

| Key | Action |
|-----|--------|
| `↑` `↓` | Navigate between tasks |
| `←` `→` | Move between columns |
| `Enter` | Pick up task / Place task |
| `Esc` | Cancel move |
| `A` | Add new task |
| `D` | Delete task |
| `Q` | Quit |

Vim keys (`h` `j` `k` `l`) also work for navigation.

### Moving Tasks

1. Navigate to a task and press `Enter` to pick it up
2. The task appears in magenta showing where it will move
3. Use `←` `→` to choose the destination column
4. Press `Enter` to place it, or `Esc` to cancel

### CLI Mode (Alternative)

A command-line interface is also available:

```bash
source venv/bin/activate
python3 main.py board          # Show board
python3 main.py add "Task"     # Add task
python3 main.py move 1 "Done"  # Move task by ID
python3 main.py list           # List all tasks
python3 main.py show 1         # Show task details
python3 main.py done 1         # Mark task as done
python3 main.py rm 1           # Delete task
```

## Project Structure

```
Todo-List/
├── todo              # Launcher script (no venv activation needed)
├── tui.py            # Interactive terminal UI
├── main.py           # CLI interface
├── models.py         # Task/Column data operations
├── db.py             # Database connection
├── schema.sql        # SQLite schema
├── requirements.txt  # Python dependencies
└── todo.db           # SQLite database (created on first run)
```

## Requirements

- Python 3.10+
- Dependencies: `rich`, `typer`, `textual`

## Roadmap

1. **Phase 1**: Terminal-based personal Kanban (current)
2. **Phase 2**: Web-based shared version for family use (planned)
   - FastAPI backend
   - Multi-user support
   - Shared boards
   - Deploy to AWS EC2
