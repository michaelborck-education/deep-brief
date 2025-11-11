"""CLI progress display utilities for real-time workflow visualization."""

from dataclasses import dataclass, field
from typing import Callable

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    ProgressColumn,
    Task,
    TextColumn,
    TimeRemainingColumn,
)
from rich.text import Text

console = Console()


@dataclass
class OperationProgress:
    """Track progress for a single operation."""

    name: str
    total_steps: float = 1.0
    current_step: float = 0.0

    def update(self, progress: float) -> None:
        """Update progress (0.0 to 1.0)."""
        self.current_step = min(progress, self.total_steps)

    def get_percentage(self) -> int:
        """Get progress as percentage."""
        return int((self.current_step / self.total_steps) * 100)


class CLIProgressTracker:
    """Tracks and displays progress for video analysis workflow."""

    def __init__(self):
        """Initialize progress tracker."""
        self.operations: dict[str, OperationProgress] = {}
        self.current_operation: str | None = None
        self.progress: Progress | None = None
        self.tasks: dict[str, int] = {}

    def start_workflow(
        self, workflow_name: str, operations: list[tuple[str, str, float]]
    ) -> None:
        """
        Start a new workflow with named operations.

        Args:
            workflow_name: Name of the workflow
            operations: List of (op_id, op_name, weight) tuples
        """
        self.operations = {}
        self.tasks = {}

        # Display workflow header
        console.print(f"\n[bold blue]▶ {workflow_name}[/bold blue]\n")

        # Create progress bar
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        )

        # Register operations
        for op_id, op_name, weight in operations:
            self.operations[op_id] = OperationProgress(op_name, total_steps=weight)

    def start_operation(self, operation_id: str) -> None:
        """Mark an operation as started."""
        if not self.progress:
            return

        self.current_operation = operation_id
        if operation_id in self.operations:
            op = self.operations[operation_id]
            if operation_id not in self.tasks:
                task_id = self.progress.add_task(op.name, total=100)
                self.tasks[operation_id] = task_id

    def update_progress(
        self, progress: float, current_step: str | None = None
    ) -> None:
        """
        Update current operation progress.

        Args:
            progress: Progress value (0.0 to 1.0)
            current_step: Optional description of current step
        """
        if not self.progress or not self.current_operation:
            return

        op_id = self.current_operation
        if op_id in self.operations:
            self.operations[op_id].update(progress)
            task_id = self.tasks.get(op_id)
            if task_id is not None:
                percentage = int(progress * 100)
                desc = self.operations[op_id].name
                if current_step:
                    desc = f"{desc} • {current_step}"
                self.progress.update(task_id, completed=percentage, description=desc)

    def complete_operation(self, operation_id: str) -> None:
        """Mark an operation as complete."""
        if not self.progress:
            return

        if operation_id in self.tasks:
            task_id = self.tasks[operation_id]
            self.progress.update(task_id, completed=100)

    def complete_workflow(self) -> None:
        """Complete the workflow and display completion message."""
        if self.progress:
            self.progress.stop()
        console.print("[green]✓ Analysis complete![/green]\n")

    def fail_workflow(self, error_message: str) -> None:
        """Fail the workflow with an error message."""
        if self.progress:
            self.progress.stop()
        console.print(f"[red]✗ Analysis failed: {error_message}[/red]\n")


def create_progress_callback(
    tracker: CLIProgressTracker,
) -> Callable[[float], None]:
    """
    Create a progress callback function for the PipelineCoordinator.

    Args:
        tracker: CLIProgressTracker instance

    Returns:
        Callback function accepting progress (0.0-1.0)
    """

    def callback(progress: float) -> None:
        tracker.update_progress(progress)

    return callback
