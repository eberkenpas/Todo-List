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
- Remote access via SSH (run on EC2, access from anywhere)
- Designed for future extension to a shared web application

## Installation

### Local Installation

```bash
cd /path/to/Todo-List

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Remote Installation (EC2)

```bash
# SSH into your EC2 instance
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip

# Clone and set up
git clone <your-repo-url> ~/pyDev/Todo-List
cd ~/pyDev/Todo-List
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Quick Start (Local)

```bash
./todo
```

### Quick Start (Remote via SSH)

```bash
kanban
```

The `kanban` command (symlinked from `kanban-remote`) SSHs into the EC2 instance and launches the TUI.

To set up remote access on your local machine:

```bash
# Create symlink for easy access
sudo ln -s /path/to/Todo-List/kanban-remote /usr/local/bin/kanban

# Edit kanban-remote to configure your EC2 details:
# - REMOTE_HOST: Your EC2 IP address
# - REMOTE_USER: Your EC2 username (e.g., ubuntu)
# - REMOTE_PATH: Path to Todo-List on EC2
# - SSH_KEY: Path to your .pem key file
```

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
├── todo              # Local launcher script
├── kanban-remote     # Remote launcher (SSH into EC2)
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

1. **Phase 1**: Terminal-based personal Kanban ✓
2. **Phase 2**: Web-based shared version for family use (planned)
   - FastAPI backend
   - Multi-user support
   - Shared boards
   - Web frontend alongside TUI (both on EC2)
