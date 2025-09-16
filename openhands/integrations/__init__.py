"""Integration helpers for OpenHands."""

from importlib import import_module
from typing import Any

__all__ = ['azure_openai']


def __getattr__(name: str) -> Any:
    if name == 'azure_openai':
        return import_module('openhands.integrations.azure_openai')
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
