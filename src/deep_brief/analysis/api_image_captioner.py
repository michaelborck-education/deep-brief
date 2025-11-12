"""API-based image captioning using LLM vision models.

This module provides image captioning using external API services like
Anthropic Claude, OpenAI GPT-4V, or Google Gemini, avoiding the need
for large local models and GPU resources.
"""

import asyncio
import base64
import logging
import time
from io import BytesIO
from pathlib import Path
from typing import Any, cast

import numpy as np
from PIL import Image
from pydantic import BaseModel

from deep_brief.utils.api_keys import APIProvider, get_api_key_with_validation
from deep_brief.utils.config import get_config

logger = logging.getLogger(__name__)


class APICaptionResult(BaseModel):
    """Result from API-based image captioning."""

    caption: str
    confidence: float = 1.0  # API responses assumed high confidence
    processing_time: float
    provider: str
    model: str
    tokens_used: int | None = None
    cost_estimate: float | None = None


class APIImageCaptioner:
    """API-based image captioning using vision LLMs."""

    def __init__(self, config: Any = None):
        """Initialize API image captioner."""
        self.config = config or get_config()
        self.provider = self.config.visual_analysis.api_provider
        self.model = self.config.visual_analysis.api_model
        self.max_concurrent = self.config.visual_analysis.api_max_concurrent
        self.timeout = self.config.visual_analysis.api_timeout
        self.max_retries = self.config.visual_analysis.api_max_retries

        # Get API key (don't use api_key_env_var config as it's provider-specific)
        # The get_api_key_with_validation will use the correct env var based on provider
        self.api_key, status_msg = get_api_key_with_validation(
            provider=cast("APIProvider", self.provider),
            env_var_name=None,  # Let it auto-detect based on provider
            log_result=True,
        )

        if not self.api_key:
            raise ValueError(f"API key not found: {status_msg}")

        logger.info(
            f"APIImageCaptioner initialized: provider={self.provider}, model={self.model}"
        )

    def _encode_image_base64(self, image: np.ndarray | Image.Image | Path) -> str:
        """
        Encode image to base64 string for API transmission.

        Args:
            image: Image as numpy array, PIL Image, or file path

        Returns:
            Base64-encoded image string
        """
        # Convert to PIL Image if needed
        if isinstance(image, np.ndarray):
            # Convert BGR to RGB if needed (OpenCV uses BGR)
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = image[:, :, ::-1]  # BGR to RGB
            pil_image = Image.fromarray(image)
        elif isinstance(image, (Path, str)):
            pil_image = Image.open(image)
        else:
            pil_image = image

        # Convert to JPEG and encode to base64
        buffer = BytesIO()
        pil_image.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode("utf-8")

    def _get_caption_prompt(self) -> str:
        """Get the prompt to send to the vision model."""
        return """Analyze this image and provide a concise, descriptive caption.

Focus on:
- Main subject or content
- Key visual elements
- Context (presentation slide, document, video frame, etc.)
- Any text visible in the image
- Overall purpose or message

Provide a single paragraph caption (2-4 sentences) that would help someone understand the content without seeing the image."""

    async def _caption_with_anthropic(self, image_base64: str) -> dict[str, Any]:
        """Caption image using Anthropic Claude API."""
        try:
            import anthropic
        except ImportError as e:
            raise ImportError(
                "anthropic package required for API captioning. Install with: pip install anthropic"
            ) from e

        client = anthropic.Anthropic(api_key=self.api_key)

        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64,
                                },
                            },
                            {"type": "text", "text": self._get_caption_prompt()},
                        ],
                    }
                ],
            )

            caption = message.content[0].text  # type: ignore
            tokens_in = message.usage.input_tokens  # type: ignore
            tokens_out = message.usage.output_tokens  # type: ignore
            tokens_total = tokens_in + tokens_out

            # Claude 4.x pricing (per million tokens)
            # Source: https://www.anthropic.com/pricing
            pricing = {
                "claude-haiku-4-5": (0.80, 4.00),  # $0.80 input, $4.00 output per MTok
                "claude-sonnet-4-5": (
                    3.00,
                    15.00,
                ),  # $3.00 input, $15.00 output per MTok
                "claude-opus-4-1": (
                    15.00,
                    75.00,
                ),  # $15.00 input, $75.00 output per MTok
                # Legacy 3.x models
                "claude-3-5-sonnet-20241022": (3.00, 15.00),
            }

            # Get pricing for current model, default to Sonnet if unknown
            input_price, output_price = pricing.get(self.model, (3.00, 15.00))

            # Calculate cost in dollars
            cost = (tokens_in / 1_000_000 * input_price) + (
                tokens_out / 1_000_000 * output_price
            )

            return {
                "caption": caption.strip(),
                "tokens": tokens_total,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def _caption_with_openai(self, image_base64: str) -> dict[str, Any]:
        """Caption image using OpenAI GPT-4V API."""
        try:
            import openai
        except ImportError as e:
            raise ImportError(
                "openai package required for API captioning. Install with: pip install openai"
            ) from e

        client = openai.OpenAI(api_key=self.api_key)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                },
                            },
                            {"type": "text", "text": self._get_caption_prompt()},
                        ],
                    }
                ],
                max_tokens=1024,
            )

            caption = response.choices[0].message.content or ""
            tokens_in = response.usage.prompt_tokens  # type: ignore
            tokens_out = response.usage.completion_tokens  # type: ignore
            tokens_total = response.usage.total_tokens  # type: ignore

            # OpenAI pricing (per million tokens)
            # Source: https://openai.com/api/pricing/
            pricing = {
                "gpt-4o": (2.50, 10.00),  # $2.50 input, $10.00 output per MTok
                "gpt-4o-mini": (0.150, 0.600),  # $0.15 input, $0.60 output per MTok
                "gpt-4-turbo": (10.00, 30.00),  # $10.00 input, $30.00 output per MTok
            }

            # Get pricing for current model, default to gpt-4o
            input_price, output_price = pricing.get(self.model, (2.50, 10.00))

            # Calculate cost in dollars
            cost = (tokens_in / 1_000_000 * input_price) + (
                tokens_out / 1_000_000 * output_price
            )

            return {
                "caption": caption.strip(),
                "tokens": tokens_total,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _caption_with_google(self, image_base64: str) -> dict[str, Any]:
        """Caption image using Google Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError as e:
            raise ImportError(
                "google-generativeai package required for API captioning. Install with: pip install google-generativeai"
            ) from e

        genai.configure(api_key=self.api_key)  # type: ignore

        try:
            model = genai.GenerativeModel(self.model)  # type: ignore

            # Decode base64 to bytes for Gemini
            image_bytes = base64.b64decode(image_base64)

            response = model.generate_content(
                [
                    self._get_caption_prompt(),
                    {"mime_type": "image/jpeg", "data": image_bytes},
                ]
            )

            caption = response.text

            # Get token usage from Gemini response
            tokens_in = (
                response.usage_metadata.prompt_token_count
                if hasattr(response, "usage_metadata")
                else None
            )
            tokens_out = (
                response.usage_metadata.candidates_token_count
                if hasattr(response, "usage_metadata")
                else None
            )
            tokens_total = (
                (tokens_in + tokens_out) if (tokens_in and tokens_out) else None
            )

            # Gemini pricing (per million tokens)
            # Source: https://ai.google.dev/pricing
            pricing = {
                "gemini-2.5-flash": (
                    0.075,
                    0.30,
                ),  # $0.075 input, $0.30 output per MTok
                "gemini-1.5-flash": (0.075, 0.30),  # Same pricing
                "gemini-1.5-pro": (1.25, 5.00),  # $1.25 input, $5.00 output per MTok
            }

            # Get pricing for current model
            input_price, output_price = pricing.get(self.model, (0.075, 0.30))

            # Calculate cost in dollars
            cost = None
            if tokens_in and tokens_out:
                cost = (tokens_in / 1_000_000 * input_price) + (
                    tokens_out / 1_000_000 * output_price
                )

            return {
                "caption": caption.strip(),
                "tokens": tokens_total,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise

    async def _caption_single_image_async(
        self, image: np.ndarray | Image.Image | Path
    ) -> APICaptionResult:
        """
        Caption a single image using the configured API.

        Args:
            image: Image to caption

        Returns:
            APICaptionResult with caption and metadata
        """
        start_time = time.time()

        # Encode image
        image_base64 = self._encode_image_base64(image)
        logger.debug(f"Encoded image to base64 ({len(image_base64)} chars)")

        # Call appropriate API
        retries = 0
        last_error = None

        while retries <= self.max_retries:
            try:
                if self.provider == "anthropic":
                    result = await self._caption_with_anthropic(image_base64)
                elif self.provider == "openai":
                    result = await self._caption_with_openai(image_base64)
                elif self.provider == "google":
                    result = await self._caption_with_google(image_base64)
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")

                processing_time = time.time() - start_time

                cost = result.get("cost") or 0.0
                logger.debug(
                    f"Caption generated in {processing_time:.2f}s, "
                    f"tokens={result.get('tokens')}, cost=${cost:.4f}"
                )

                return APICaptionResult(
                    caption=result["caption"],
                    processing_time=processing_time,
                    provider=self.provider,
                    model=self.model,
                    tokens_used=result.get("tokens"),
                    cost_estimate=result.get("cost"),
                )

            except Exception as e:
                last_error = e
                retries += 1
                if retries <= self.max_retries:
                    wait_time = 2**retries  # Exponential backoff
                    logger.warning(
                        f"API error (attempt {retries}/{self.max_retries}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)

        # All retries failed
        raise RuntimeError(
            f"Failed to caption image after {self.max_retries} retries: {last_error}"
        )

    def caption_image(self, image: np.ndarray | Image.Image | Path) -> APICaptionResult:
        """
        Caption a single image (synchronous wrapper).

        Args:
            image: Image to caption

        Returns:
            APICaptionResult with caption and metadata
        """
        return asyncio.run(self._caption_single_image_async(image))

    async def caption_images_batch(
        self, images: list[np.ndarray | Image.Image | Path]
    ) -> list[APICaptionResult]:
        """
        Caption multiple images concurrently.

        Args:
            images: List of images to caption

        Returns:
            List of APICaptionResult objects
        """
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def caption_with_semaphore(image: Any) -> APICaptionResult:
            async with semaphore:
                return await self._caption_single_image_async(image)

        # Caption all images concurrently
        tasks = [caption_with_semaphore(img) for img in images]
        results: list[APICaptionResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )

        # Handle any errors
        final_results: list[APICaptionResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to caption image {i}: {result}")
                # Create error result
                final_results.append(
                    APICaptionResult(
                        caption=f"Error: {str(result)}",
                        provider=self.provider,
                        model=self.model,
                        processing_time=0.0,
                    )
                )
            else:
                # result is APICaptionResult here (not BaseException)
                final_results.append(result)  # type: ignore

        return final_results

    def caption_images(
        self, images: list[np.ndarray | Image.Image | Path]
    ) -> list[APICaptionResult]:
        """
        Caption multiple images (synchronous wrapper).

        Args:
            images: List of images to caption

        Returns:
            List of APICaptionResult objects
        """
        return asyncio.run(self.caption_images_batch(images))

    def cleanup(self):
        """Clean up resources (no-op for API captioner)."""
        logger.info("APIImageCaptioner cleanup complete")
