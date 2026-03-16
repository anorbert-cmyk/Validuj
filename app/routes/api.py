from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.repository import (
    count_runs_for_owner,
    create_project,
    create_run,
    get_admin_overview,
    get_run,
    list_projects,
    list_runs,
    user_owns_project,
    user_owns_run,
)
from app.routes.billing import current_subscription
from app.security import mutation_rate_limit, require_admin, require_session
from app.schemas import CreateProjectRequest, CreateRunRequest
from app.services.analysis_runner import spawn_analysis


router = APIRouter(prefix="/api")


@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


@router.post("/runs")
async def create_run_api(
    request: Request,
    payload: CreateRunRequest,
    session=Depends(require_session),
    _: None = Depends(mutation_rate_limit),
):
    if payload.project_public_id and not user_owns_project(payload.project_public_id, session["email"]):
        raise HTTPException(status_code=403, detail="Project access denied")
    subscription = await current_subscription(session)
    run_limit = int(subscription.get("run_limit", 0))
    current_count = count_runs_for_owner(session["email"])
    if current_count >= run_limit:
        raise HTTPException(
            status_code=403,
            detail=f"Run limit reached for plan '{subscription.get('plan_name', 'free')}'.",
        )
    run_id = create_run(
        payload.idea_text,
        payload.project_public_id,
        owner_email=session["email"],
    )
    spawn_analysis(run_id, request.app.state.analysis_runner)
    return {"run_id": run_id, "status": "queued"}


@router.get("/projects")
async def list_projects_api(session=Depends(require_session)):
    return [project.model_dump(mode="json") for project in list_projects(owner_email=session["email"])]


@router.post("/projects")
async def create_project_api(
    request: Request,
    payload: CreateProjectRequest,
    session=Depends(require_session),
    _: None = Depends(mutation_rate_limit),
):
    project_id = create_project(payload, owner_email=session["email"])
    return {"project_id": project_id, "status": "created"}


@router.get("/runs")
async def list_runs_api(session=Depends(require_session)):
    return [run.model_dump(mode="json") for run in list_runs(owner_email=session["email"])]


@router.get("/admin/overview")
async def admin_overview_api(session=Depends(require_admin)):
    return get_admin_overview()


@router.get("/runs/{run_id}")
async def get_run_api(run_id: str, session=Depends(require_session)):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if session["role"] != "admin" and not user_owns_run(run_id, session["email"]):
        raise HTTPException(status_code=403, detail="Run access denied")
    return run.model_dump(mode="json")


@router.get("/runs/{run_id}/markdown", response_class=PlainTextResponse)
async def get_run_markdown_api(run_id: str, session=Depends(require_session)):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if session["role"] != "admin" and not user_owns_run(run_id, session["email"]):
        raise HTTPException(status_code=403, detail="Run access denied")
    if not run.final_markdown:
        raise HTTPException(status_code=409, detail="Run is not complete yet")
    return PlainTextResponse(
        content=run.final_markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{run_id}.md"',
        },
    )
