"""HTML report renderer."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HTMLRenderer:
    """Render analysis reports as HTML."""

    def __init__(self, config: Any = None):
        """Initialize HTML renderer."""
        self.config = config
        logger.info("HTMLRenderer initialized")

    def render_report(self, report: dict[str, Any]) -> str:
        """Render report as HTML."""
        logger.info("Rendering HTML report")

        video = report.get("video", {})
        audio = report.get("audio", {})
        scenes = report.get("scenes", [])
        frames = report.get("frames", [])
        transcription = report.get("full_transcription_text", "")
        segments = report.get("transcription_segments", [])
        speech_metrics = report.get("speech_metrics", {})

        # Build frames HTML
        frames_html = ""
        for frame in frames:
            caption = frame.get("caption", "")
            ocr = frame.get("ocr_text", "")
            objects = frame.get("detected_objects", [])

            frame_path = frame.get("file_path", "")
            img_tag = (
                f'<img src="{frame_path}" style="max-width: 600px; border: 1px solid #ddd; margin: 10px 0;">'
                if frame_path
                else ""
            )

            frames_html += f"""
            <div class="frame" style="margin: 20px 0; padding: 15px; background: #f9f9f9; border-left: 4px solid #007bff;">
                <h4>Frame {frame.get('frame_number', 0)} @ {frame.get('timestamp', 0):.2f}s (Scene {frame.get('scene_number', 0)})</h4>
                {img_tag}
                <div><strong>Resolution:</strong> {frame.get('width', 0)}x{frame.get('height', 0)}</div>
                {"<div><strong>Caption:</strong> " + caption + f" <em>({frame.get('caption_model', 'unknown')})</em></div>" if caption else ""}
                {"<div><strong>Text (OCR):</strong> " + ocr + "</div>" if ocr else ""}
                {"<div><strong>Objects detected:</strong> " + ", ".join(objects) + "</div>" if objects else ""}
                {"<div><strong>Quality score:</strong> " + f"{frame.get('quality_score', 0):.2f}" + "</div>" if frame.get('quality_score') else ""}
            </div>
            """

        # Build transcription HTML
        transcription_html = ""
        if segments:
            transcription_html = "<h2>Transcription</h2>"
            transcription_html += f'<div style="margin-bottom: 20px;"><strong>Language:</strong> {report.get("language", "Unknown")}</div>'
            if speech_metrics:
                transcription_html += f"""
                <div style="background: #f0f0f0; padding: 15px; margin-bottom: 20px;">
                    <h3>Speech Metrics</h3>
                    <div><strong>Total Words:</strong> {speech_metrics.get('total_words', 0)}</div>
                    <div><strong>Speech Duration:</strong> {speech_metrics.get('total_speech_duration', 0):.1f}s</div>
                    <div><strong>Speaking Rate:</strong> {speech_metrics.get('speaking_rate_wpm', 0):.1f} WPM</div>
                    <div><strong>Average Confidence:</strong> {speech_metrics.get('average_confidence', 0):.2f}</div>
                </div>
                """
            for seg in segments:
                transcription_html += f"""
                <div style="margin: 10px 0; padding: 10px; background: #fafafa; border-left: 3px solid #28a745;">
                    <div><strong>[{seg.get('start_time', 0):.2f}s - {seg.get('end_time', 0):.2f}s]</strong></div>
                    <div style="margin-top: 5px;">{seg.get('text', '')}</div>
                </div>
                """

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Video Analysis Report</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #ffffff;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c2c2c;
            margin-top: 30px;
            border-bottom: 2px solid #6c757d;
            padding-bottom: 5px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }}
        .metric strong {{
            color: #495057;
            display: block;
            margin-bottom: 5px;
        }}
        .check {{
            color: #28a745;
            font-weight: bold;
        }}
        .cross {{
            color: #dc3545;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📹 Video Analysis Report</h1>

        <div class="summary">
            <div class="metric">
                <strong>Video File</strong>
                {video.get('file_path', 'Unknown')}
            </div>
            <div class="metric">
                <strong>Duration</strong>
                {video.get('duration', 0):.1f} seconds
            </div>
            <div class="metric">
                <strong>Resolution</strong>
                {video.get('width', 0)}x{video.get('height', 0)} @ {video.get('fps', 0):.1f} fps
            </div>
            <div class="metric">
                <strong>Scenes Detected</strong>
                {report.get('total_scenes', 0)}
            </div>
            <div class="metric">
                <strong>Frames Analyzed</strong>
                {report.get('total_frames', 0)}
            </div>
            <div class="metric">
                <strong>Analysis Features</strong>
                <div>Transcription: <span class="{'check' if report.get('has_transcription') else 'cross'}">{'✓' if report.get('has_transcription') else '✗'}</span></div>
                <div>Captions: <span class="{'check' if report.get('has_captions') else 'cross'}">{'✓' if report.get('has_captions') else '✗'}</span></div>
                <div>OCR: <span class="{'check' if report.get('has_ocr') else 'cross'}">{'✓' if report.get('has_ocr') else '✗'}</span></div>
            </div>
        </div>

        {transcription_html}

        <h2>Frame Analysis</h2>
        <div>{frames_html if frames_html else "<p>No frames analyzed</p>"}</div>

    </div>
</body>
</html>"""

        return html

    def save_html(self, html_content: str, output_path: Path) -> None:
        """Save HTML content to file."""
        logger.info(f"Saving HTML report to {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write(html_content)

        logger.info(f"HTML report saved: {output_path}")
