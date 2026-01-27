"""Todo-List: A terminal-based Kanban board."""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from typing import Optional

import db
import models

app = typer.Typer(help="Todo-List: A terminal-based Kanban board")
console = Console()

PRIORITY_COLORS = {1: "dim", 2: "white", 3: "bold red"}
PRIORITY_LABELS = {1: "low", 2: "med", 3: "high"}


@app.callback()
def startup():
    """Initialize database on startup."""
    db.init_db()


@app.command()
def board():
    """Display the Kanban board."""
    columns = models.get_all_columns()

    panels = []
    for col in columns:
        tasks = models.get_tasks_by_column(col.id)

        # Build task list for this column
        task_lines = []
        for task in tasks:
            priority_style = PRIORITY_COLORS.get(task.priority, "white")
            due = f" [cyan]({task.due_date})[/]" if task.due_date else ""
            task_lines.append(
                f"[{priority_style}][{task.id}] {task.title}{due}[/]"
            )

        content = "\n".join(task_lines) if task_lines else "[dim]No tasks[/]"
        panel = Panel(
            content,
            title=f"[bold]{col.name}[/] ({len(tasks)})",
            border_style="blue",
            width=30,
            box=box.ROUNDED
        )
        panels.append(panel)

    console.print()
    console.print(Columns(panels, equal=True, expand=True))
    console.print()


@app.command()
def add(
    title: str = typer.Argument(..., help="Task title"),
    column: str = typer.Option("Todo", "-c", "--column", help="Target column"),
    description: Optional[str] = typer.Option(None, "-d", "--desc", help="Description"),
    priority: int = typer.Option(2, "-p", "--priority", min=1, max=3, help="Priority (1=low, 2=med, 3=high)"),
    due: Optional[str] = typer.Option(None, "--due", help="Due date (YYYY-MM-DD)")
):
    """Add a new task."""
    try:
        task = models.add_task(title, column, description, priority, due)
        console.print(f"[green]Added task [{task.id}]: {task.title}[/]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command()
def move(
    task_id: int = typer.Argument(..., help="Task ID"),
    column: str = typer.Argument(..., help="Target column name")
):
    """Move a task to a different column."""
    try:
        task = models.move_task(task_id, column)
        console.print(f"[green]Moved task [{task.id}] to {column}[/]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command()
def done(
    task_id: int = typer.Argument(..., help="Task ID")
):
    """Mark a task as done (move to Done column)."""
    try:
        task = models.move_task(task_id, "Done")
        console.print(f"[green]Completed task [{task.id}]: {task.title}[/]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command()
def edit(
    task_id: int = typer.Argument(..., help="Task ID"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "-d", "--desc", help="New description"),
    priority: Optional[int] = typer.Option(None, "-p", "--priority", min=1, max=3, help="New priority"),
    due: Optional[str] = typer.Option(None, "--due", help="New due date (YYYY-MM-DD)")
):
    """Edit a task."""
    try:
        task = models.update_task(task_id, title, description, priority, due)
        console.print(f"[green]Updated task [{task.id}][/]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)


@app.command()
def show(
    task_id: int = typer.Argument(..., help="Task ID")
):
    """Show task details."""
    task = models.get_task_by_id(task_id)
    if not task:
        console.print(f"[red]Task {task_id} not found[/]")
        raise typer.Exit(1)

    columns = {c.id: c.name for c in models.get_all_columns()}

    table = Table(show_header=False, box=box.SIMPLE)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("ID", str(task.id))
    table.add_row("Title", task.title)
    table.add_row("Description", task.description or "-")
    table.add_row("Column", columns.get(task.column_id, "Unknown"))
    table.add_row("Priority", PRIORITY_LABELS.get(task.priority, "?"))
    table.add_row("Due Date", str(task.due_date) if task.due_date else "-")
    table.add_row("Created", str(task.created_at))
    table.add_row("Updated", str(task.updated_at))

    console.print(table)


@app.command()
def rm(
    task_id: int = typer.Argument(..., help="Task ID"),
    force: bool = typer.Option(False, "-f", "--force", help="Skip confirmation")
):
    """Remove a task."""
    task = models.get_task_by_id(task_id)
    if not task:
        console.print(f"[red]Task {task_id} not found[/]")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Delete task [{task.id}] '{task.title}'?")
        if not confirm:
            console.print("[yellow]Cancelled[/]")
            raise typer.Exit(0)

    models.delete_task(task_id)
    console.print(f"[green]Deleted task [{task_id}][/]")


@app.command(name="list")
def list_tasks(
    column: Optional[str] = typer.Option(None, "-c", "--column", help="Filter by column")
):
    """List all tasks."""
    if column:
        col = models.get_column_by_name(column)
        if not col:
            console.print(f"[red]Column '{column}' not found[/]")
            raise typer.Exit(1)
        tasks = models.get_tasks_by_column(col.id)
    else:
        tasks = models.get_all_tasks()

    if not tasks:
        console.print("[dim]No tasks found[/]")
        return

    columns = {c.id: c.name for c in models.get_all_columns()}

    table = Table(box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Column")
    table.add_column("Priority")
    table.add_column("Due")

    for task in tasks:
        priority_style = PRIORITY_COLORS.get(task.priority, "white")
        table.add_row(
            str(task.id),
            task.title,
            columns.get(task.column_id, "?"),
            f"[{priority_style}]{PRIORITY_LABELS.get(task.priority, '?')}[/]",
            str(task.due_date) if task.due_date else "-"
        )

    console.print(table)


if __name__ == "__main__":
    app()
