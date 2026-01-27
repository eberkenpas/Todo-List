# Claude.md - Development Progress

## Project Overview

**Todo-List**: A Kanban-style todo list application in two phases:
1. Terminal-based personal tool (Python + Textual + SQLite)
2. Web-based shared tool for family (future)

## Architecture

### Tech Stack
- **Textual**: Full-screen terminal UI framework (built on Rich)
- **Rich**: Terminal formatting, colors, and panels
- **Typer**: CLI argument parsing (alternative interface)
- **SQLite**: Local database - portable, schema translates to PostgreSQL later

### Data Model
Designed with multi-user web extension in mind:
- `columns` table: Kanban columns with position ordering
- `tasks` table: Tasks with title, description, priority, due date, timestamps
- Foreign key relationship for task-to-column
- Schema ready for future `user_id` and sharing fields

### File Structure
```
Todo-List/
├── todo              # Launcher script
├── tui.py            # Interactive TUI (main interface)
├── main.py           # CLI interface (alternative)
├── models.py         # Data layer (CRUD operations)
├── db.py             # Database connection/init
├── schema.sql        # Database schema
├── requirements.txt  # Dependencies
├── README.md         # User documentation
└── Claude.md         # Development notes (this file)
```

## Progress

### Phase 1: Terminal Kanban

- [x] Project setup (README.md, Claude.md)
- [x] Data model design (SQLite schema)
- [x] Requirements (rich, typer, textual)
- [x] Database layer (db.py)
- [x] Core task CRUD operations (models.py)
- [x] CLI interface (main.py)
- [x] Interactive TUI (tui.py)
  - [x] Full-screen responsive layout
  - [x] Arrow key navigation
  - [x] Vim keybindings (hjkl)
  - [x] Color-coded columns (cyan/yellow/green)
  - [x] Pick-up/place task movement with visual preview
  - [x] Cancel move with Escape
  - [x] Add task modal
  - [x] Delete task with confirmation
  - [x] Status bar with contextual help
  - [x] Column count updates during move preview
- [x] Launcher script (./todo)
- [ ] Task editing in TUI (priority, due date)
- [ ] Column management (add/remove columns)

### Phase 2: Web Extension (Future)

- [ ] FastAPI backend serving REST API
- [ ] PostgreSQL database (or keep SQLite with WAL mode)
- [ ] User authentication
- [ ] Shared boards between family members
- [ ] Simple web frontend (HTML/HTMX or React)
- [ ] Deploy to EC2
- [ ] Both TUI and web app share same backend/database

## Session Log

### Session 1
- Created project structure and documentation
- Evaluated existing tools (kanban-python, python-kanban)
- Decided to build custom for full control and clean architecture
- Built CLI interface with Typer
- Built full TUI with Textual
  - DOS-style full-screen interface
  - Three columns: Todo, Doing, Done
  - Color coding: Cyan, Yellow, Green
  - Keyboard navigation with arrow keys and vim bindings
  - Modal dialogs for add/delete
- Improved UX: pick-up/place movement with visual feedback
  - Task shows in magenta in target column during move
  - Original position shows struck-through
  - Column counts show transition (e.g., "2→1")
  - Escape cancels and returns to original position
- Created launcher script to avoid venv activation hassle
- Discussed future architecture: EC2 hosting both web and TUI

## Design Decisions

### Why custom instead of forking existing tools?
- Full control over codebase
- Clean data model designed for future web extension
- Understand every line of code for maintenance

### Why Textual over curses/blessed?
- Modern, actively maintained
- Same team as Rich (consistent API)
- Handles responsive layouts automatically
- Built-in widget system

### Why SQLite?
- Zero configuration
- Single file, portable
- Schema translates directly to PostgreSQL when needed
- Sufficient for family-scale usage

## Next Steps

1. Test thoroughly and fix any bugs
2. Add task editing in TUI (priority, due date fields)
3. Consider search/filter functionality
4. Plan Phase 2 API design
