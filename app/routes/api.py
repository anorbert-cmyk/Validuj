from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.repository import create_run, get_run
from app.schemas import CreateRunRequest
from app.services.analysis_runner import spawn_analysis


router = APIRouter(prefix="/api")


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.post("/runs")
async def create_run_api(request: Request, payload: CreateRunRequest):
    run_id = create_run(payload.idea_text)
    spawn_analysis(run_id, request.app.state.analysis_runner)
    return {"run_id": run_id, "status": "queued"}


@router.get("/runs/{run_id}")
async def get_run_api(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.model_dump(mode="json")
