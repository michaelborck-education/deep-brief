# Type stubs for transformers
from typing import Any

import torch

class PreTrainedModel:
    def to(self, device: str | torch.device) -> PreTrainedModel: ...
    def eval(self) -> PreTrainedModel: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

class ProcessorMixin:
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

def pipeline(
    task: str,
    model: str | None = None,
    config: str | dict[str, Any] | None = None,
    tokenizer: Any = None,
    feature_extractor: Any = None,
    image_processor: Any = None,
    framework: str | None = None,
    revision: str | None = None,
    use_fast: bool = True,
    token: str | bool | None = None,
    device: str | int | None = None,
    device_map: str | dict[str, int | str | torch.device] | None = None,
    torch_dtype: torch.dtype | None = None,
    trust_remote_code: bool | None = None,
    model_kwargs: dict[str, Any] | None = None,
    pipeline_class: Any | None = None,
    **kwargs: Any,
) -> Any: ...
