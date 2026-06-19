"""Tests for Fireworks AI provider (OpenAI-compatible chat completions)."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api.models.anthropic import Message, MessagesRequest
from config.provider_catalog import FIREWORKS_DEFAULT_BASE
from providers.base import ProviderConfig
from providers.fireworks import FireworksProvider


@pytest.fixture
def fireworks_config():
    return ProviderConfig(
        api_key="test_fireworks_key",
        base_url=FIREWORKS_DEFAULT_BASE,
        rate_limit=10,
        rate_window=60,
        enable_thinking=True,
    )


@pytest.fixture(autouse=True)
def mock_rate_limiter():
    @asynccontextmanager
    async def _slot():
        yield

    with patch(
        "providers.transports.openai_chat.transport.GlobalRateLimiter"
    ) as mock:
        instance = mock.get_scoped_instance.return_value

        async def _passthrough(fn, *args, **kwargs):
            return await fn(*args, **kwargs)

        instance.execute_with_retry = AsyncMock(side_effect=_passthrough)
        instance.concurrency_slot.side_effect = _slot
        yield instance


@pytest.fixture
def fireworks_provider(fireworks_config):
    return FireworksProvider(fireworks_config)


def test_init(fireworks_config):
    provider = FireworksProvider(fireworks_config)
    assert provider._api_key == "test_fireworks_key"
    assert provider._base_url == FIREWORKS_DEFAULT_BASE.rstrip("/")


def test_base_url_constant():
    assert FIREWORKS_DEFAULT_BASE == "https://api.fireworks.ai/inference/v1"


def test_build_request_body_openai_shape(fireworks_provider):
    request = MessagesRequest(
        model="accounts/fireworks/models/gpt-oss-120b",
        max_tokens=100,
        messages=[Message(role="user", content="Hello")],
    )
    body = fireworks_provider._build_request_body(request)
    assert body["model"] == "accounts/fireworks/models/gpt-oss-120b"
    assert body["messages"][0]["role"] == "user"
    # OpenAI format uses max_tokens or max_completion_tokens, not native Anthropic shape
    assert "max_tokens" in body or "max_completion_tokens" in body


def test_build_request_body_global_disable_blocks_thinking():
    provider = FireworksProvider(
        ProviderConfig(
            api_key="k",
            base_url=FIREWORKS_DEFAULT_BASE,
            rate_limit=1,
            rate_window=1,
            enable_thinking=False,
        )
    )
    request = MessagesRequest.model_validate(
        {
            "model": "m",
            "messages": [{"role": "user", "content": "x"}],
            "thinking": {"type": "enabled", "budget_tokens": 1},
        }
    )
    body = provider._build_request_body(request)
    # With thinking disabled, no reasoning replay
    assert "thinking" not in body


def test_build_request_body_merges_extra_body(fireworks_provider):
    request = MessagesRequest.model_validate(
        {
            "model": "m",
            "messages": [{"role": "user", "content": "x"}],
            "extra_body": {"custom_param": "value"},
        }
    )
    body = fireworks_provider._build_request_body(request)
    assert body.get("extra_body", {}).get("custom_param") == "value"


@pytest.mark.asyncio
async def test_cleanup_closes_client(fireworks_provider):
    fireworks_provider._client = AsyncMock()

    await fireworks_provider.cleanup()

    fireworks_provider._client.close.assert_awaited_once()
