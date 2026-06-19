"""Fireworks AI provider (OpenAI-compatible chat completions).

Endpoint: https://api.fireworks.ai/inference/v1/chat/completions
Docs: https://docs.fireworks.ai/api-reference/post-chatcompletions
"""

from __future__ import annotations

from typing import Any

from providers.base import ProviderConfig
from providers.defaults import FIREWORKS_DEFAULT_BASE
from providers.transports.openai_chat import OpenAIChatTransport

from .request import build_request_body


class FireworksProvider(OpenAIChatTransport):
    """Fireworks AI via ``https://api.fireworks.ai/inference/v1/chat/completions``."""

    def __init__(self, config: ProviderConfig):
        super().__init__(
            config,
            provider_name="FIREWORKS",
            base_url=config.base_url or FIREWORKS_DEFAULT_BASE,
            api_key=config.api_key,
        )

    def _build_request_body(
        self, request: Any, thinking_enabled: bool | None = None
    ) -> dict:
        return build_request_body(
            request,
            thinking_enabled=self._is_thinking_enabled(request, thinking_enabled),
        )
