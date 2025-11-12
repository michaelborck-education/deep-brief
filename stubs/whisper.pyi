# Type stubs for openai-whisper
from typing import Any

import numpy as np
from torch import Tensor

class WhisperModel:
    def transcribe(
        self,
        audio: str | np.ndarray | Tensor,
        *,
        verbose: bool | None = None,
        temperature: float | tuple[float, ...] = (0, 0.2, 0.4, 0.6, 0.8, 1),
        compression_ratio_threshold: float | None = 2.4,
        logprob_threshold: float | None = -1,
        no_speech_threshold: float | None = 0.6,
        condition_on_previous_text: bool = True,
        initial_prompt: str | None = None,
        carry_initial_prompt: bool = False,
        word_timestamps: bool = False,
        prepend_punctuations: str = "\"'¿([{-",
        append_punctuations: str = "\"'.。,，!！?？:：\")]}、",
        clip_timestamps: str | list[float] = "0",
        hallucination_silence_threshold: float | None = None,
        **decode_options: Any,
    ) -> dict[str, str | list[dict[str, Any]]]: ...
    
    def detect_language(self, mel: Tensor) -> tuple[str, list[float]]: ...

def load_model(
    name: str,
    device: str | None = None,
    download_root: str | None = None,
    in_memory: bool = False,
) -> WhisperModel: ...

# Main module attributes
Whisper = WhisperModel  # type: ignore
