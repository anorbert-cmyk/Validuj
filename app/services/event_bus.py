from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterator


class EventBus:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue[dict]]] = defaultdict(list)

    def publish(self, run_id: str, event: dict) -> None:
        for queue in list(self._queues.get(run_id, [])):
            queue.put_nowait(event)

    async def subscribe(self, run_id: str) -> AsyncIterator[dict]:
        queue: asyncio.Queue[dict] = asyncio.Queue()
        self._queues[run_id].append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            if queue in self._queues.get(run_id, []):
                self._queues[run_id].remove(queue)
            if not self._queues.get(run_id):
                self._queues.pop(run_id, None)


event_bus = EventBus()
