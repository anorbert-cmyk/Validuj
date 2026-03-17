from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.repository import get_run, list_events, user_owns_run
from app.security import require_session
from app.services.event_bus import event_bus


router = APIRouter(prefix="/api/stream")


def _format_sse(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"


@router.get("/runs/{run_id}")
async def stream_run(request: Request, run_id: str, session=Depends(require_session)):
    if get_run(run_id) is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if session["role"] != "admin" and not user_owns_run(run_id, session["email"]):
        raise HTTPException(status_code=403, detail="Run access denied")

    async def event_generator():
        for existing in list_events(run_id):
            yield _format_sse(existing.event_type, existing.payload)

        subscription = event_bus.subscribe(run_id)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(subscription.__anext__(), timeout=15.0)
                    yield _format_sse(event["event_type"], event["payload"])
                except asyncio.TimeoutError:
                    yield _format_sse("heartbeat", {"ok": True})
        except StopAsyncIteration:
            return
        finally:
            await subscription.aclose()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
