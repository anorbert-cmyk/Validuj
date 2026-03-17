from __future__ import annotations

import asyncio

import httpx
from duckduckgo_search import DDGS

from app.config import Settings
from app.schemas import Citation, SearchResultBundle


class SearchService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def search(self, query: str, *, limit: int = 5) -> SearchResultBundle:
        if self.settings.has_tavily:
            try:
                return await self._search_tavily(query, limit=limit)
            except Exception:
                pass
        return await self._search_duckduckgo(query, limit=limit)

    async def _search_tavily(self, query: str, *, limit: int) -> SearchResultBundle:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.settings.tavily_api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": limit,
                },
            )
            response.raise_for_status()
            payload = response.json()
        results = [
            Citation(
                title=item.get("title") or item.get("url") or "Result",
                url=item.get("url") or "",
                snippet=item.get("content"),
                source="tavily",
            )
            for item in payload.get("results", [])
            if item.get("url")
        ]
        return SearchResultBundle(query=query, results=results)

    async def _search_duckduckgo(self, query: str, *, limit: int) -> SearchResultBundle:
        def _run() -> list[dict]:
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=limit))

        raw_results = await asyncio.to_thread(_run)
        results = [
            Citation(
                title=item.get("title") or item.get("href") or "Result",
                url=item.get("href") or "",
                snippet=item.get("body"),
                source="duckduckgo",
            )
            for item in raw_results
            if item.get("href")
        ]
        return SearchResultBundle(query=query, results=results)
