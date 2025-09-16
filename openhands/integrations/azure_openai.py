"""Helpers for calling Azure-hosted OpenAI models used by OpenHands automations."""

from __future__ import annotations

import os
from typing import Iterable, List

try:  # pragma: no cover - optional dependency
    from openai import AzureOpenAI  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without Azure SDK
    AzureOpenAI = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from azure.identity import AzureCliCredential, get_bearer_token_provider  # type: ignore
except ImportError:  # pragma: no cover - fallback for environments without Azure SDK
    AzureCliCredential = None  # type: ignore
    get_bearer_token_provider = None  # type: ignore


def _format_prompt(prompt: Iterable[dict] | str, system_prompt: str = '') -> list[dict]:
    """Normalise prompts into the Chat Completions message list format."""

    if isinstance(prompt, list):
        if system_prompt and prompt and prompt[0].get('role') != 'system':
            return [{'role': 'system', 'content': system_prompt}, *prompt]
        return prompt

    base_message = {'role': 'user', 'content': prompt}
    if system_prompt:
        return [
            {'role': 'system', 'content': system_prompt},
            base_message,
        ]
    return [base_message]


def _call_gpt4o(messages: list[dict]) -> list[str] | None:
    """Call the GPT-4o deployment via the Azure OpenAI Chat Completions API."""

    if AzureOpenAI is None:
        raise ImportError('openai>=1.0 is required to call Azure OpenAI deployments')

    client = AzureOpenAI(
        azure_endpoint=os.getenv(
            'LLM_BASE_URL', 'https://deeppromptaustraliaeast.openai.azure.com'
        ),
        api_key=os.getenv('LLM_API_KEY'),
        api_version=os.getenv('LLM_API_VERSION', '2024-08-01-preview'),
    )

    completion = client.chat.completions.create(  # type: ignore[attr-defined]
        model=os.getenv('LLM_MODEL', 'deepprompt-gpt-4o-2024-05-13-global'),
        messages=messages,
        max_completion_tokens=16_384,
        stream=False,
    )

    if not completion.choices or not completion.choices[0].message.content:
        return None

    return [completion.choices[0].message.content.strip()]


def _call_o3mini(messages: list[dict]) -> list[str] | None:
    """Call the o3-mini deployment using Azure AD authentication."""

    if AzureOpenAI is None or AzureCliCredential is None or get_bearer_token_provider is None:
        raise ImportError(
            'azure-identity and openai packages are required to call Azure OpenAI deployments'
        )

    credential = AzureCliCredential()
    token_provider = get_bearer_token_provider(
        credential, 'https://cognitiveservices.azure.com/.default'
    )

    client = AzureOpenAI(
        azure_endpoint=os.getenv(
            'ENDPOINT_URL', 'https://aims-oai-research-inference-uks.openai.azure.com/'
        ),
        azure_ad_token_provider=token_provider,
        api_version=os.getenv('LLM_API_VERSION', '2025-01-01-preview'),
    )

    completion = client.chat.completions.create(  # type: ignore[attr-defined]
        model=os.getenv('DEPLOYMENT_NAME', 'o3-mini'),
        messages=messages,
        max_completion_tokens=100_000,
        stream=False,
    )

    if not completion.choices or not completion.choices[0].message.content:
        return None

    return [completion.choices[0].message.content.strip()]


def call_azure_chat(
    prompt: Iterable[dict] | str,
    *,
    system_prompt: str = '',
    model: str = 'o3-mini',
) -> List[str] | None:
    """Call an Azure OpenAI chat deployment and return the responses."""

    messages = _format_prompt(prompt, system_prompt)

    if model == 'gpt-4o':
        return _call_gpt4o(messages)
    if model == 'o3-mini':
        return _call_o3mini(messages)

    raise ValueError(f'Unsupported Azure OpenAI model: {model}')


__all__ = ['call_azure_chat', '_format_prompt']
