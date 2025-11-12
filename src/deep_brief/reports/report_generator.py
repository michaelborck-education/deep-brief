"""Report generator for creating structured analysis reports."""

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class VideoMetadata(BaseModel):
    """Video file metadata."""

    file_path: str
    duration: float
    width: int
    height: int
    fps: float
    format: str | None = None


class AudioMetadata(BaseModel):
    """Audio metadata."""

    duration: float
    sample_rate: int
    channels: int


class SceneReport(BaseModel):
    """Report for a single scene."""

    scene_number: int
    start_time: float
    end_time: float
    duration: float
    num_frames: int


class FrameReport(BaseModel):
    """Report for a single analyzed frame."""

    frame_number: int
    timestamp: float
    scene_number: int
    file_path: str | None
    width: int
    height: int

    # Caption
    caption: str | None = None
    caption_confidence: float | None = None
    caption_model: str | None = None
    caption_tokens: int | None = None  # Total tokens used for caption
    caption_cost: float | None = None  # Cost in USD for caption

    # OCR
    ocr_text: str | None = None
    ocr_confidence: float | None = None
    num_text_regions: int = 0

    # Object detection
    num_objects_detected: int = 0
    detected_objects: list[str] = []

    # Quality
    quality_score: float | None = None
    sharpness: float | None = None
    brightness: float | None = None


class TranscriptionSegment(BaseModel):
    """Transcription segment."""

    id: int
    text: str
    start_time: float
    end_time: float
    confidence: float | None = None
    num_words: int = 0


class SpeechMetrics(BaseModel):
    """Speech analysis metrics."""

    total_words: int
    total_speech_duration: float
    speaking_rate_wpm: float
    average_confidence: float


class APICostSummary(BaseModel):
    """Summary of API usage costs."""

    total_frames_processed: int = 0
    total_tokens_used: int = 0
    total_cost_usd: float = 0.0
    provider: str | None = None
    model: str | None = None


class AnalysisReport(BaseModel):
    """Complete video analysis report."""

    # Video metadata
    video: VideoMetadata

    # Audio metadata
    audio: AudioMetadata | None = None

    # Scenes
    scenes: list[SceneReport] = []
    total_scenes: int = 0

    # Frames
    frames: list[FrameReport] = []
    total_frames: int = 0

    # Transcription
    transcription_segments: list[TranscriptionSegment] = []
    full_transcription_text: str = ""
    language: str | None = None

    # Speech metrics
    speech_metrics: SpeechMetrics | None = None

    # API cost summary
    api_cost_summary: APICostSummary | None = None

    # Analysis metadata
    has_transcription: bool = False
    has_visual_analysis: bool = False
    has_captions: bool = False
    has_ocr: bool = False
    has_object_detection: bool = False


class ReportGenerator:
    """Generate analysis reports from video analysis data."""

    def __init__(self, config: Any = None):
        """Initialize report generator."""
        self.config = config
        logger.info("ReportGenerator initialized")

    def generate_report(self, analysis_data: dict[str, Any]) -> dict[str, Any]:
        """Generate analysis report from data."""
        logger.info("Generating analysis report")

        # Extract video info
        video_info = analysis_data.get("video_info")
        if not video_info:
            raise ValueError("Missing video_info in analysis data")

        video_metadata = VideoMetadata(
            file_path=str(video_info.file_path),
            duration=video_info.duration,
            width=video_info.width,
            height=video_info.height,
            fps=video_info.fps,
            format=getattr(video_info, "format", None),
        )

        # Extract audio info
        audio_info = analysis_data.get("audio_info")
        audio_metadata = None
        if audio_info:
            audio_metadata = AudioMetadata(
                duration=audio_info.duration,
                sample_rate=audio_info.sample_rate,
                channels=audio_info.channels,
            )

        # Extract scenes
        scenes = analysis_data.get("scenes", [])
        scene_reports: list[SceneReport] = []
        for scene in scenes:
            scene_reports.append(
                SceneReport(
                    scene_number=scene.scene_number,
                    start_time=scene.start_time,
                    end_time=scene.end_time,
                    duration=scene.duration,
                    num_frames=0,  # Will be updated from frame analysis
                )
            )

        # Extract frame analyses
        frame_analyses = analysis_data.get("frame_analyses", [])
        frame_reports: list[FrameReport] = []
        has_captions = False
        has_ocr = False
        has_object_detection = False

        # frame_analyses is a flat list of frame results
        for frame in frame_analyses:
            # Build frame report
            frame_report = FrameReport(
                frame_number=frame.frame_number,
                timestamp=frame.timestamp,
                scene_number=frame.scene_number,
                file_path=str(frame.file_path) if frame.file_path else None,
                width=frame.width,
                height=frame.height,
            )

            # Add caption if available
            if frame.caption_result:
                frame_report.caption = frame.caption_result.caption
                frame_report.caption_confidence = frame.caption_result.confidence
                frame_report.caption_model = frame.caption_result.model_used
                frame_report.caption_tokens = frame.caption_result.tokens_generated
                frame_report.caption_cost = frame.caption_result.cost_estimate
                has_captions = True

            # Add OCR if available
            if frame.ocr_result:
                # Use full_text if available, otherwise combine text regions
                frame_report.ocr_text = frame.ocr_result.full_text
                frame_report.ocr_confidence = frame.ocr_result.average_confidence
                frame_report.num_text_regions = len(frame.ocr_result.text_regions)
                has_ocr = True

            # Add object detection if available
            if frame.object_detection_result:
                frame_report.num_objects_detected = len(
                    frame.object_detection_result.detected_objects
                )
                frame_report.detected_objects = [
                    str(
                        obj.element_type.value
                        if hasattr(obj.element_type, "value")
                        else obj.element_type
                    )
                    for obj in frame.object_detection_result.detected_objects
                ]
                has_object_detection = True

            # Add quality metrics if available
            if frame.quality_metrics:
                frame_report.quality_score = frame.quality_metrics.overall_quality_score
                frame_report.sharpness = frame.quality_metrics.blur_score
                frame_report.brightness = frame.quality_metrics.brightness_score

            frame_reports.append(frame_report)

            # Update scene frame count
            scene_report: SceneReport
            for scene_report in scene_reports:
                if scene_report.scene_number == frame.scene_number:
                    scene_report.num_frames += 1
                    break

        # Extract transcription
        transcription = analysis_data.get("transcription")
        transcription_segments: list[TranscriptionSegment] = []
        full_text = ""
        language = None

        if transcription:
            language = transcription.language
            if transcription.segments:
                for seg in transcription.segments:
                    transcription_segments.append(
                        TranscriptionSegment(
                            id=seg.id,
                            text=seg.text,
                            start_time=seg.start,
                            end_time=seg.end,
                            confidence=getattr(seg, "confidence", None),
                            num_words=len(seg.words) if hasattr(seg, "words") else 0,
                        )
                    )
                full_text = " ".join(seg.text for seg in transcription.segments)

        # Extract speech metrics
        speech_analysis = analysis_data.get("speech_metrics")
        speech_metrics = None

        if speech_analysis and hasattr(speech_analysis, "overall_metrics"):
            overall = speech_analysis.overall_metrics
            speech_metrics = SpeechMetrics(
                total_words=overall.total_word_count,
                total_speech_duration=overall.total_speaking_time,
                speaking_rate_wpm=overall.average_wpm,
                average_confidence=getattr(overall, "average_confidence", 0.0),
            )

        # Calculate API cost summary
        api_cost_summary: APICostSummary | None = None
        total_tokens: int = 0
        total_cost: float = 0.0
        frames_with_cost = 0
        provider: str | None = None
        model: str | None = None

        frame_report: FrameReport
        for frame_report in frame_reports:
            if frame_report.caption_cost is not None and frame_report.caption_cost > 0:
                total_cost += frame_report.caption_cost
                frames_with_cost += 1
            if frame_report.caption_tokens is not None:
                total_tokens += frame_report.caption_tokens
            # Extract provider and model from first frame with caption
            if provider is None and frame_report.caption_model:
                provider = (
                    frame_report.caption_model.split(":")[0]
                    if ":" in frame_report.caption_model
                    else None
                )
                model = (
                    frame_report.caption_model.split(":", 1)[1]
                    if ":" in frame_report.caption_model
                    else frame_report.caption_model
                )

        if frames_with_cost > 0:
            api_cost_summary = APICostSummary(
                total_frames_processed=frames_with_cost,
                total_tokens_used=total_tokens,
                total_cost_usd=total_cost,
                provider=provider,
                model=model,
            )

        # Build final report
        report = AnalysisReport(
            video=video_metadata,
            audio=audio_metadata,
            scenes=scene_reports,
            total_scenes=len(scene_reports),
            frames=frame_reports,
            total_frames=len(frame_reports),
            transcription_segments=transcription_segments,
            full_transcription_text=full_text,
            language=language,
            speech_metrics=speech_metrics,
            api_cost_summary=api_cost_summary,
            has_transcription=len(transcription_segments) > 0,
            has_visual_analysis=len(frame_reports) > 0,
            has_captions=has_captions,
            has_ocr=has_ocr,
            has_object_detection=has_object_detection,
        )

        # Convert to dict for JSON serialization
        return report.model_dump()

    def save_json(self, report: dict[str, Any], output_path: Path) -> None:
        """Save report as JSON file."""
        logger.info(f"Saving JSON report to {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"JSON report saved: {output_path}")
