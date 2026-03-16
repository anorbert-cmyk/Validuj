from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.repository import create_project, create_run, get_admin_overview, get_run, list_projects, list_runs
from app.schemas import CreateProjectRequest, CreateRunRequest
from app.services.analysis_runner import spawn_analysis


router = APIRouter(prefix="/api")


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.post("/runs")
async def create_run_api(request: Request, payload: CreateRunRequest):
    run_id = create_run(payload.idea_text, payload.project_public_id)
    spawn_analysis(run_id, request.app.state.analysis_runner)
    return {"run_id": run_id, "status": "queued"}


@router.get("/projects")
async def list_projects_api():
    return [project.model_dump(mode="json") for project in list_projects()]


@router.post("/projects")
async def create_project_api(payload: CreateProjectRequest):
    project_id = create_project(payload)
    return {"project_id": project_id, "status": "created"}


@router.get("/runs")
async def list_runs_api():
    return [run.model_dump(mode="json") for run in list_runs()]


@router.get("/admin/overview")
async def admin_overview_api():
    return get_admin_overview()


@router.get("/runs/{run_id}")
async def get_run_api(run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.model_dump(mode="json")
