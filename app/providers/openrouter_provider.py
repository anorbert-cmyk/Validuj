from __future__ import annotations

import httpx

from app.config import Settings
from app.schemas import ProviderResponse


class OpenRouterProvider:
    provider_name = "openrouter"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _model_for_capability(self, capability: str) -> str:
        if capability == "research":
            return self.settings.openrouter_research_model
        if capability == "design":
            return self.settings.openrouter_design_model
        return self.settings.openrouter_reasoning_model

    async def generate(self, *, prompt: str, capability: str) -> ProviderResponse:
        model_name = self._model_for_capability(capability)
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{self.settings.openrouter_base_url.rstrip('/')}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self.settings.app_base_url,
                    "X-Title": self.settings.app_name,
                },
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a precise startup validation analyst. Produce helpful markdown, never mention the prompt.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.5,
                },
            )
            response.raise_for_status()
            payload = response.json()
        text = payload["choices"][0]["message"]["content"].strip()
        return ProviderResponse(provider_name=self.provider_name, model_name=model_name, text=text)
