from __future__ import annotations

from typing import Protocol

from app.schemas import ProviderResponse


class TextGenerationProvider(Protocol):
    provider_name: str

    async def generate(self, *, prompt: str, capability: str) -> ProviderResponse: ...
