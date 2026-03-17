from __future__ import annotations

from app.config import Settings
from app.providers.local_provider import LocalProvider
from app.providers.openrouter_provider import OpenRouterProvider
from app.schemas import ProviderResponse


class ModelRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._remote = OpenRouterProvider(settings) if settings.has_openrouter else None
        self._local = LocalProvider(settings)

    async def generate(self, *, prompt: str, capability: str) -> ProviderResponse:
        if self._remote is not None:
            try:
                return await self._remote.generate(prompt=prompt, capability=capability)
            except Exception:
                pass
        return await self._local.generate(prompt=prompt, capability=capability)
