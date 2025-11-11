"""Command-line interface for DeepBrief."""

import logging
import sys
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from deep_brief.core.exceptions import VideoProcessingError
from deep_brief.core.pipeline_coordinator import PipelineCoordinator
from deep_brief.utils.config import get_config, load_config
from deep_brief.utils.progress_display import CLIProgressTracker

console = Console()
app = typer.Typer(help="DeepBrief - Video Analysis Application")


@app.command()
def analyze(
    video_path: Path | None = typer.Argument(
        None, help="Path to video file to analyze"
    ),
    output_dir: Path | None = typer.Option(
        None, "--output", "-o", help="Output directory for reports"
    ),
    config_file: Path | None = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
) -> None:
    """
    Analyze a video file for presentation feedback.

    If no video path is provided, launches the web interface.
    """
    # Load configuration
    config = load_config(config_file) if config_file else get_config()

    # Set up logging
    logger = logging.getLogger("deep_brief")
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting DeepBrief analysis")

    console.print(
        Panel.fit(
            f"[bold blue]{config.app_name}[/bold blue]\n[dim]Video Analysis Application[/dim]",
            border_style="blue",
        )
    )

    if config.debug:
        console.print("[yellow]Debug mode enabled[/yellow]")
        logger.debug("Debug mode is active")

    if video_path:
        # CLI mode - analyze specific video
        _analyze_video_cli(
            video_path=video_path,
            output_dir=output_dir,
            config=config,
            config_file=config_file,
            verbose=verbose,
            logger=logger,
        )
    else:
        # Web UI mode
        logger.info("Launching web interface")
        console.print("[green]Launching web interface...[/green]")

        # TODO: Import and launch Gradio interface
        logger.warning("Web interface not yet implemented")
        console.print("[yellow]Web interface not yet implemented.[/yellow]")
        console.print("[dim]Run with --help for available options.[/dim]")


def _analyze_video_cli(
    video_path: Path,
    output_dir: Path | None,
    config: object,
    config_file: Path | None,
    verbose: bool,
    logger: logging.Logger,
) -> None:
    """
    Perform video analysis in CLI mode.

    Args:
        video_path: Path to video file
        output_dir: Optional output directory
        config: Configuration object
        config_file: Configuration file path (for logging)
        verbose: Verbose output flag
        logger: Logger instance
    """
    # Validate video path
    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        console.print(f"[red]✗ Error: Video file not found[/red] {video_path}")
        logger.error(f"Video file not found: {video_path}")
        sys.exit(1)

    if not video_path_obj.is_file():
        console.print(f"[red]✗ Error: Path is not a file[/red] {video_path}")
        logger.error(f"Path is not a file: {video_path}")
        sys.exit(1)

    # Set up output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[blue]Output directory:[/blue] {output_path}")
        logger.debug(f"Output directory: {output_path}")
    else:
        # Default output to current directory with video name
        output_path = Path.cwd() / video_path_obj.stem
        output_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[blue]Output directory:[/blue] {output_path} (default)")
        logger.debug(f"Output directory (default): {output_path}")

    if config_file:
        console.print(f"[blue]Config file:[/blue] {config_file}")
        logger.debug(f"Using config file: {config_file}")

    # Show relevant config info in debug mode
    if verbose:
        console.print(
            f"[dim]Max file size: {config.processing.max_video_size_mb}MB[/dim]"
        )
        console.print(
            f"[dim]Transcription model: {config.transcription.model}[/dim]"
        )

    logger.info(f"Starting analysis: {video_path}")
    console.print(f"[green]Analyzing video:[/green] {video_path}\n")

    # Initialize progress tracker and pipeline
    progress_tracker = CLIProgressTracker()
    pipeline = PipelineCoordinator(config=config, progress_tracker=None)

    # Define workflow operations
    operations = [
        ("validate", "Validating video", 0.05),
        ("audio", "Extracting audio", 0.25),
        ("scenes", "Detecting scenes", 0.35),
        ("frames", "Extracting frames", 0.35),
    ]

    progress_tracker.start_workflow(f"Analyzing {video_path_obj.name}", operations)

    try:
        # Track time
        start_time = time.time()

        # Perform analysis
        progress_tracker.start_operation("validate")
        result = pipeline.analyze_video(
            video_path=video_path_obj,
            extract_audio=True,
            detect_scenes=True,
            extract_frames=True,
            output_dir=output_path,
        )
        progress_tracker.complete_operation("validate")
        progress_tracker.complete_operation("audio")
        progress_tracker.complete_operation("scenes")
        progress_tracker.complete_operation("frames")

        processing_time = time.time() - start_time

        # Check if analysis was successful
        if not result.success:
            progress_tracker.fail_workflow(result.error_message or "Unknown error")
            if result.errors:
                for error in result.errors:
                    logger.error(f"Error: {error}")
            sys.exit(1)

        # Display results
        progress_tracker.complete_workflow()

        # Show summary
        console.print("[bold]Analysis Summary:[/bold]")
        console.print(f"  Video: {video_path_obj.name}")
        console.print(f"  Duration: {result.video_info.duration:.1f}s")
        console.print(f"  Resolution: {result.video_info.width}x{result.video_info.height}")
        console.print(f"  FPS: {result.video_info.fps:.1f}")

        if result.audio_info:
            console.print(
                f"  Audio: {result.audio_info.duration:.1f}s @ {result.audio_info.sample_rate}Hz"
            )

        if result.scene_result:
            console.print(f"  Scenes detected: {result.scene_result.total_scenes}")

        console.print(f"  Frames extracted: {len(result.frame_infos)}")
        console.print(f"  Processing time: {processing_time:.1f}s\n")

        console.print(f"[green]✓ Output saved to:[/green] {output_path}")
        logger.info(f"Analysis complete. Results saved to {output_path}")

    except VideoProcessingError as e:
        error_msg = str(e)
        progress_tracker.fail_workflow(error_msg)
        logger.error(f"Video processing error: {e}", exc_info=verbose)
        sys.exit(1)

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        progress_tracker.fail_workflow(error_msg)
        logger.error(error_msg, exc_info=True)
        sys.exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from deep_brief import __version__

    console.print(f"DeepBrief version {__version__}")


@app.command()
def config(
    show_all: bool = typer.Option(
        False, "--all", help="Show all configuration options"
    ),
    config_file: Path | None = typer.Option(
        None, "--config", "-c", help="Configuration file path"
    ),
) -> None:
    """Show current configuration."""
    if config_file:
        config_obj = load_config(config_file)
        console.print(f"[blue]Using config file:[/blue] {config_file}")
    else:
        config_obj = get_config()
        console.print("[blue]Using default configuration[/blue]")

    console.print("\n[bold]Application Configuration[/bold]")
    console.print(f"App Name: {config_obj.app_name}")
    console.print(f"Version: {config_obj.version}")
    console.print(f"Debug Mode: {config_obj.debug}")

    if show_all:
        console.print("\n[bold]Processing Settings[/bold]")
        console.print(f"Max Video Size: {config_obj.processing.max_video_size_mb}MB")
        console.print(
            f"Supported Formats: {', '.join(config_obj.processing.supported_formats)}"
        )
        console.print(f"Temp Directory: {config_obj.processing.temp_dir}")

        console.print("\n[bold]Transcription Settings[/bold]")
        console.print(f"Model: {config_obj.transcription.model}")
        console.print(f"Language: {config_obj.transcription.language}")
        console.print(f"Device: {config_obj.transcription.device}")

        console.print("\n[bold]Analysis Settings[/bold]")
        console.print(f"Target WPM: {config_obj.analysis.target_wpm_range}")
        console.print(
            f"Confidence Threshold: {config_obj.analysis.confidence_threshold}"
        )

        console.print("\n[bold]Logging Settings[/bold]")
        console.print(f"Level: {config_obj.logging.level}")
        console.print(f"File: {config_obj.logging.file_path}")
    else:
        console.print("\n[dim]Use --all to see all configuration options[/dim]")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    app()
