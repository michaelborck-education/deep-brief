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
from typing import Any

import numpy as np
from PIL import Image
from pydantic import BaseModel

from deep_brief.utils.api_keys import get_api_key_with_validation
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
            provider=self.provider,
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
        elif isinstance(image, Path) or isinstance(image, str):
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

    async def _caption_with_anthropic(
        self, image_base64: str
    ) -> dict[str, Any]:
        """Caption image using Anthropic Claude API."""
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required for API captioning. Install with: pip install anthropic"
            )

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

            caption = message.content[0].text
            tokens = message.usage.input_tokens + message.usage.output_tokens

            # Rough cost estimate (Claude 3.5 Sonnet pricing)
            cost = (message.usage.input_tokens / 1000 * 0.003) + (
                message.usage.output_tokens / 1000 * 0.015
            )

            return {
                "caption": caption.strip(),
                "tokens": tokens,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def _caption_with_openai(self, image_base64: str) -> dict[str, Any]:
        """Caption image using OpenAI GPT-4V API."""
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package required for API captioning. Install with: pip install openai"
            )

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

            caption = response.choices[0].message.content
            tokens = response.usage.total_tokens

            # Rough cost estimate (GPT-4V pricing)
            cost = tokens / 1000 * 0.01  # Approximate

            return {
                "caption": caption.strip(),
                "tokens": tokens,
                "cost": cost,
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def _caption_with_google(self, image_base64: str) -> dict[str, Any]:
        """Caption image using Google Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package required for API captioning. Install with: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)

        try:
            model = genai.GenerativeModel(self.model)

            # Decode base64 to bytes for Gemini
            image_bytes = base64.b64decode(image_base64)

            response = model.generate_content([
                self._get_caption_prompt(),
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])

            caption = response.text

            # Token counting not always available in Gemini
            tokens = None
            cost = None  # Gemini pricing varies

            return {
                "caption": caption.strip(),
                "tokens": tokens,
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

                cost = result.get('cost') or 0.0
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

    def caption_image(
        self, image: np.ndarray | Image.Image | Path
    ) -> APICaptionResult:
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

        async def caption_with_semaphore(image):
            async with semaphore:
                return await self._caption_single_image_async(image)

        # Caption all images concurrently
        tasks = [caption_with_semaphore(img) for img in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any errors
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to caption image {i}: {result}")
                # Create error result
                final_results.append(
                    APICaptionResult(
                        caption=f"Error: {str(result)}",
                        processing_time=0.0,
                        provider=self.provider,
                        model=self.model,
                        confidence=0.0,
                    )
                )
            else:
                final_results.append(result)

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
