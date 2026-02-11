"""Todo-List: Interactive Terminal UI."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
from textual.widgets import Header, Footer, Static, Input, Button, Label
from textual.screen import ModalScreen
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel

from datetime import date
from pathlib import Path

import db
import models


# Color schemes for columns
COLUMN_STYLES = {
    "Todo": {"border": "cyan", "title": "bold cyan", "task": "white", "selected": "black on cyan", "moving": "bold magenta"},
    "Doing": {"border": "yellow", "title": "bold yellow", "task": "white", "selected": "black on yellow", "moving": "bold magenta"},
    "Done": {"border": "green", "title": "bold green", "task": "dim white", "selected": "black on green", "moving": "bold magenta"},
}


class AddTaskModal(ModalScreen[str | None]):
    """Modal dialog for adding a new task."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Container(id="add-dialog"):
            yield Label("Add New Task", id="add-title")
            yield Input(placeholder="Enter task title...", id="task-input")
            with Horizontal(id="add-buttons"):
                yield Button("Add", variant="primary", id="btn-add")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#task-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add":
            title = self.query_one("#task-input", Input).value.strip()
            if title:
                self.dismiss(title)
            else:
                self.dismiss(None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        title = event.value.strip()
        self.dismiss(title if title else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class EditTaskModal(ModalScreen[str | None]):
    """Modal dialog for editing a task title."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, task_title: str):
        super().__init__()
        self.task_title = task_title

    def compose(self) -> ComposeResult:
        with Container(id="edit-dialog"):
            yield Label("Edit Task", id="edit-title")
            yield Input(
                placeholder="Enter task title...",
                id="title-input",
                value=self.task_title
            )
            with Horizontal(id="edit-buttons"):
                yield Button("Save", variant="primary", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_mount(self) -> None:
        self.query_one("#title-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save":
            title = self.query_one("#title-input", Input).value.strip()
            self.dismiss(title if title else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        title = event.value.strip()
        self.dismiss(title if title else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class DeleteConfirmModal(ModalScreen[bool]):
    """Modal dialog for confirming task deletion."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
    ]

    def __init__(self, task_title: str):
        super().__init__()
        self.task_title = task_title

    def compose(self) -> ComposeResult:
        with Container(id="delete-dialog"):
            yield Label("Delete Task?", id="delete-title")
            yield Label(f'"{self.task_title}"', id="delete-task-name")
            with Horizontal(id="delete-buttons"):
                yield Button("Yes (Y)", variant="error", id="btn-yes")
                yield Button("No (N)", variant="default", id="btn-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class KanbanColumn(Static):
    """A single Kanban column."""

    def __init__(self, column: models.Column, tasks: list[models.Task],
                 is_active: bool = False, cursor_pos: int = 0,
                 moving_task: models.Task | None = None,
                 show_moving_task: bool = False):
        super().__init__()
        self.column = column
        self.tasks = tasks
        self.is_active = is_active
        self.cursor_pos = cursor_pos
        self.moving_task = moving_task
        self.show_moving_task = show_moving_task  # Show the moving task preview in this column

    def render(self) -> Panel:
        col_name = self.column.name
        styles = COLUMN_STYLES.get(col_name, COLUMN_STYLES["Todo"])

        # Calculate max length based on column width
        # Account for panel borders (2), padding, and prefix characters (5 for "→ ◆ " or "> ● ")
        available_width = self.size.width - 7 if self.size.width > 15 else 25
        max_len = max(15, available_width)  # Minimum 15 chars

        # Build task list
        lines = []

        # If we're showing the moving task preview at the top of this column
        if self.show_moving_task and self.moving_task:
            display = f"→ ◆ {self.moving_task.title}"
            if len(display) > max_len:
                display = display[:max_len-3] + "..."
            lines.append(Text(display, style=styles["moving"]))

        if not self.tasks and not (self.show_moving_task and self.moving_task):
            lines.append(Text("  (empty)", style="dim italic"))
        else:
            for i, task in enumerate(self.tasks):
                # Skip the moving task in its original column
                if self.moving_task and task.id == self.moving_task.id:
                    # Show it dimmed in original position
                    display = f"  ○ {task.title}"
                    if len(display) > max_len:
                        display = display[:max_len-3] + "..."
                    lines.append(Text(display, style="dim strike"))
                    continue

                is_cursor = self.is_active and i == self.cursor_pos
                prefix = ">" if is_cursor else " "
                title = task.title

                # Truncate if needed
                if len(title) > max_len - 5:  # Account for prefix and bullet
                    title = title[:max_len-8] + "..."

                display = f"{prefix} ● {title}"

                if is_cursor:
                    lines.append(Text(display, style=styles["selected"]))
                else:
                    lines.append(Text(display, style=styles["task"]))

        content = Text("\n").join(lines)

        border_style = "bold " + styles["border"] if self.is_active else styles["border"]
        title_style = styles["title"]

        # Show count (adjust if moving task is being previewed here)
        count = len(self.tasks)
        if self.show_moving_task and self.moving_task:
            # Task would be added here
            count_display = f"{count}→{count+1}"
        elif self.moving_task and any(t.id == self.moving_task.id for t in self.tasks):
            # Task is leaving this column
            count_display = f"{count}→{count-1}"
        else:
            count_display = str(count)

        title = Text(f" {col_name} ({count_display}) ", style=title_style)

        return Panel(
            content,
            title=title,
            border_style=border_style,
            height=None,
        )


class KanbanBoard(Static):
    """The main Kanban board container."""

    def __init__(self):
        super().__init__()
        self.columns: list[models.Column] = []
        self.tasks_by_column: dict[int, list[models.Task]] = {}
        self.active_column = 0
        self.cursor_positions: dict[int, int] = {}
        # Moving task state
        self.moving_task: models.Task | None = None
        self.original_column_idx: int | None = None
        self.refresh_data()

    def refresh_data(self) -> None:
        """Reload data from database."""
        self.columns = models.get_all_columns()
        self.tasks_by_column = {}
        for col in self.columns:
            self.tasks_by_column[col.id] = models.get_tasks_by_column(col.id)
            if col.id not in self.cursor_positions:
                self.cursor_positions[col.id] = 0
            # Clamp cursor to valid range
            tasks = self.tasks_by_column[col.id]
            if tasks:
                self.cursor_positions[col.id] = min(self.cursor_positions[col.id], len(tasks) - 1)
            else:
                self.cursor_positions[col.id] = 0

    def render(self) -> Text:
        return Text("")

    def compose(self) -> ComposeResult:
        with Horizontal(id="board-columns"):
            for i, col in enumerate(self.columns):
                tasks = self.tasks_by_column.get(col.id, [])
                cursor_pos = self.cursor_positions.get(col.id, 0)
                # Show moving task preview in active column (if different from original)
                show_moving = (self.moving_task is not None and
                              i == self.active_column and
                              self.original_column_idx != i)
                yield KanbanColumn(
                    col, tasks,
                    is_active=(i == self.active_column),
                    cursor_pos=cursor_pos,
                    moving_task=self.moving_task,
                    show_moving_task=show_moving
                )

    def rebuild(self) -> None:
        """Rebuild the board after data changes."""
        self.refresh_data()
        board_container = self.query_one("#board-columns", Horizontal)
        board_container.remove_children()
        for i, col in enumerate(self.columns):
            tasks = self.tasks_by_column.get(col.id, [])
            cursor_pos = self.cursor_positions.get(col.id, 0)
            show_moving = (self.moving_task is not None and
                          i == self.active_column and
                          self.original_column_idx != i)
            board_container.mount(KanbanColumn(
                col, tasks,
                is_active=(i == self.active_column),
                cursor_pos=cursor_pos,
                moving_task=self.moving_task,
                show_moving_task=show_moving
            ))

    def move_cursor_left(self) -> None:
        if self.active_column > 0:
            self.active_column -= 1
            self.rebuild()

    def move_cursor_right(self) -> None:
        if self.active_column < len(self.columns) - 1:
            self.active_column += 1
            self.rebuild()

    def move_cursor_up(self) -> None:
        # Don't allow vertical movement while moving a task
        if self.moving_task:
            return
        col = self.columns[self.active_column]
        tasks = self.tasks_by_column.get(col.id, [])
        if tasks:
            pos = self.cursor_positions.get(col.id, 0)
            if pos > 0:
                self.cursor_positions[col.id] = pos - 1
                self.rebuild()

    def move_cursor_down(self) -> None:
        # Don't allow vertical movement while moving a task
        if self.moving_task:
            return
        col = self.columns[self.active_column]
        tasks = self.tasks_by_column.get(col.id, [])
        if tasks:
            pos = self.cursor_positions.get(col.id, 0)
            if pos < len(tasks) - 1:
                self.cursor_positions[col.id] = pos + 1
                self.rebuild()

    def get_current_task(self) -> models.Task | None:
        """Get the task under the cursor."""
        col = self.columns[self.active_column]
        tasks = self.tasks_by_column.get(col.id, [])
        pos = self.cursor_positions.get(col.id, 0)
        if tasks and 0 <= pos < len(tasks):
            return tasks[pos]
        return None

    def start_moving_task(self) -> bool:
        """Start moving the current task. Returns True if started."""
        task = self.get_current_task()
        if task:
            self.moving_task = task
            self.original_column_idx = self.active_column
            self.rebuild()
            return True
        return False

    def confirm_move(self) -> bool:
        """Confirm the move of the selected task. Returns True if moved."""
        if self.moving_task is None:
            return False

        target_col = self.columns[self.active_column]

        if self.original_column_idx != self.active_column:
            # Actually move the task in the database
            models.move_task(self.moving_task.id, target_col.name)

        # Clear moving state
        self.moving_task = None
        self.original_column_idx = None
        self.refresh_data()

        # Update cursor position in target column
        tasks = self.tasks_by_column.get(target_col.id, [])
        self.cursor_positions[target_col.id] = max(0, len(tasks) - 1)

        self.rebuild()
        return True

    def cancel_move(self) -> bool:
        """Cancel the current move. Returns True if was moving."""
        if self.moving_task is None:
            return False

        # Return to original column
        if self.original_column_idx is not None:
            self.active_column = self.original_column_idx

        self.moving_task = None
        self.original_column_idx = None
        self.rebuild()
        return True

    def is_moving(self) -> bool:
        """Check if currently moving a task."""
        return self.moving_task is not None

    def add_task(self, title: str) -> None:
        """Add a new task to the current column."""
        col = self.columns[self.active_column]
        models.add_task(title, col.name)
        self.refresh_data()
        tasks = self.tasks_by_column.get(col.id, [])
        self.cursor_positions[col.id] = max(0, len(tasks) - 1)
        self.rebuild()

    def delete_current_task(self) -> bool:
        """Delete the task under cursor. Returns True if deleted."""
        task = self.get_current_task()
        if task:
            models.delete_task(task.id)
            self.refresh_data()
            col = self.columns[self.active_column]
            tasks = self.tasks_by_column.get(col.id, [])
            pos = self.cursor_positions.get(col.id, 0)
            if pos >= len(tasks) and tasks:
                self.cursor_positions[col.id] = len(tasks) - 1
            self.rebuild()
            return True
        return False


class TodoApp(App):
    """Main Todo-List application."""

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Footer {
        background: $primary-darken-2;
    }

    #board-columns {
        width: 100%;
        height: 1fr;
        padding: 1;
        overflow-y: auto;
    }

    KanbanColumn {
        width: 1fr;
        height: 100%;
        margin: 0 1;
        overflow-y: auto;
    }

    #add-dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: tall $primary;
    }

    #add-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
        width: 100%;
    }

    #task-input {
        width: 100%;
        margin-bottom: 1;
    }

    #add-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #add-buttons Button {
        margin: 0 1;
    }

    #delete-dialog {
        width: 45;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: tall $error;
    }

    #delete-title {
        text-align: center;
        text-style: bold;
        color: $error;
        padding-bottom: 1;
        width: 100%;
    }

    #delete-task-name {
        text-align: center;
        text-style: italic;
        padding-bottom: 1;
        width: 100%;
    }

    #delete-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #delete-buttons Button {
        margin: 0 1;
    }

    #edit-dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $surface;
        border: tall $primary;
    }

    #edit-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding-bottom: 1;
        width: 100%;
    }

    #title-input {
        width: 100%;
        margin-bottom: 1;
    }

    #edit-buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    #edit-buttons Button {
        margin: 0 1;
    }

    #task-detail {
        dock: bottom;
        height: 1;
        background: $surface-darken-1;
        color: $text;
        padding: 0 1;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary-darken-1;
        color: $text;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_task", "Add"),
        Binding("e", "edit_task", "Edit"),
        Binding("d", "delete_task", "Delete"),
        Binding("enter", "confirm", "Select/Place"),
        Binding("escape", "cancel", "Cancel", show=False),
        Binding("left", "move_left", "←", show=False),
        Binding("right", "move_right", "→", show=False),
        Binding("up", "move_up", "↑", show=False),
        Binding("down", "move_down", "↓", show=False),
        Binding("x", "export_column", "eXport"),
        Binding("h", "move_left", "←", show=False),
        Binding("l", "move_right", "→", show=False),
        Binding("k", "move_up", "↑", show=False),
        Binding("j", "move_down", "↓", show=False),
    ]

    TITLE = "Todo-List"

    def __init__(self):
        super().__init__()
        db.init_db()

    def compose(self) -> ComposeResult:
        yield Header()
        yield KanbanBoard()
        yield Static("", id="task-detail")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.update_status()

    def update_status(self, message: str = "") -> None:
        """Update the status bar and task detail bar."""
        board = self.query_one(KanbanBoard)
        task = board.get_current_task()

        # Task detail bar — full task info
        if task:
            detail = f"● {task.title}"
            if task.description:
                detail += f" — {task.description}"
            if task.due_date:
                detail += f"  (due: {task.due_date})"
            priority_labels = {1: "low", 2: "med", 3: "high"}
            detail += f"  [{priority_labels.get(task.priority, '?')}]"
        else:
            detail = ""
        self.query_one("#task-detail", Static).update(detail)

        # Status bar — commands/messages
        if message:
            status = message
        elif board.is_moving():
            moving = board.moving_task
            status = f"Moving: {moving.title} │ ←→ choose column │ Enter: place │ Esc: cancel"
        else:
            if task:
                status = "Enter: pick up │ A: add │ E: edit │ D: delete │ X: export │ Q: quit"
            else:
                status = "No tasks │ Press 'A' to add a task"

        self.query_one("#status-bar", Static).update(status)

    def action_move_left(self) -> None:
        self.query_one(KanbanBoard).move_cursor_left()
        self.update_status()

    def action_move_right(self) -> None:
        self.query_one(KanbanBoard).move_cursor_right()
        self.update_status()

    def action_move_up(self) -> None:
        self.query_one(KanbanBoard).move_cursor_up()
        self.update_status()

    def action_move_down(self) -> None:
        self.query_one(KanbanBoard).move_cursor_down()
        self.update_status()

    def action_confirm(self) -> None:
        """Enter key: pick up task or place it."""
        board = self.query_one(KanbanBoard)
        if board.is_moving():
            if board.confirm_move():
                self.update_status("Task moved!")
            else:
                self.update_status()
        else:
            if board.start_moving_task():
                self.update_status()
            else:
                self.update_status("No task to move")

    def action_cancel(self) -> None:
        """Escape key: cancel current move."""
        board = self.query_one(KanbanBoard)
        if board.cancel_move():
            self.update_status("Move cancelled")
        else:
            self.update_status()

    def action_add_task(self) -> None:
        # Don't allow adding while moving
        board = self.query_one(KanbanBoard)
        if board.is_moving():
            self.update_status("Finish moving first (Enter or Esc)")
            return

        def handle_result(title: str | None) -> None:
            if title:
                self.query_one(KanbanBoard).add_task(title)
                self.update_status(f"Added: {title}")

        self.push_screen(AddTaskModal(), handle_result)

    def action_edit_task(self) -> None:
        """Edit the title of the current task."""
        board = self.query_one(KanbanBoard)

        # Don't allow editing while moving
        if board.is_moving():
            self.update_status("Finish moving first (Enter or Esc)")
            return

        task = board.get_current_task()
        if not task:
            self.update_status("No task to edit")
            return

        def handle_result(new_title: str | None) -> None:
            if new_title:
                models.update_task(task.id, title=new_title)
                board.refresh_data()
                board.rebuild()
                self.update_status(f"Updated: {new_title}")

        self.push_screen(EditTaskModal(task.title), handle_result)

    def action_delete_task(self) -> None:
        board = self.query_one(KanbanBoard)

        # Don't allow deleting while moving
        if board.is_moving():
            self.update_status("Finish moving first (Enter or Esc)")
            return

        task = board.get_current_task()
        if not task:
            self.update_status("No task to delete")
            return

        def handle_result(confirmed: bool) -> None:
            if confirmed:
                board.delete_current_task()
                self.update_status("Task deleted")

        self.push_screen(DeleteConfirmModal(task.title), handle_result)

    def action_export_column(self) -> None:
        """Export the current column's tasks to a dated text file."""
        board = self.query_one(KanbanBoard)

        if board.is_moving():
            self.update_status("Finish moving first (Enter or Esc)")
            return

        col = board.columns[board.active_column]
        tasks = board.tasks_by_column.get(col.id, [])

        datecode = date.today().strftime("%Y-%m-%d")
        filename = f"{datecode}-{col.name}.md"
        filepath = Path(__file__).parent / filename

        lines = [f"{col.name} - {datecode}", "=" * 30, ""]
        for task in tasks:
            lines.append(f"- {task.title}")

        filepath.write_text("\n".join(lines) + "\n")
        self.update_status(f"Exported {len(tasks)} tasks to {filename}")


def main():
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
