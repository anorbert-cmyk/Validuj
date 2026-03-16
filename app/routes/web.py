from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.repository import create_run, get_run
from app.schemas import CreateRunRequest
from app.seo import demo_structured_data, homepage_structured_data, make_meta, methodology_structured_data
from app.services.analysis_runner import spawn_analysis


router = APIRouter()


DEMO_REPORT = """# Demo report

## Market context and demand
This example shows how Validuj structures a public-facing report with evidence, recommendations and clear handoff logic between specialists.

## Competitive landscape
- Identifies direct and indirect competitors
- Highlights differentiation opportunities

## Strategy and roadmap
- Focus on a narrow early-adopter use case
- Validate willingness to pay before feature expansion

## Product and UX concept
- Define one core workflow
- Reduce onboarding friction

## Edge cases and operational safeguards
- Plan for low-quality inputs
- Explain assumptions and missing evidence clearly

## Risk assessment and recommendation
- Primary risks: urgency, acquisition economics, and implementation complexity
- Suggested next step: run a two-week validation sprint
"""


@router.get("/")
async def homepage(request: Request):
    settings = request.app.state.settings
    meta = make_meta(
        settings,
        path="/",
        title="Validuj — six-agent startup validation with research, strategy and SEO-ready reports",
        description="Validate business ideas with six specialist AI agents that pass structured knowledge from market research to risk analysis.",
        structured_data=homepage_structured_data(settings),
    )
    return request.app.state.templates.TemplateResponse(
        "index.html",
        {"request": request, "meta": meta, "page_key": "home"},
    )


@router.get("/how-it-works")
async def how_it_works(request: Request):
    settings = request.app.state.settings
    meta = make_meta(
        settings,
        path="/how-it-works",
        title="How Validuj works — six specialist agents, structured handoff, and live research",
        description="Learn how Validuj combines web research, specialist agents, structured handoff, and risk analysis in one validation workflow.",
        structured_data=methodology_structured_data(settings),
    )
    return request.app.state.templates.TemplateResponse(
        "how_it_works.html",
        {"request": request, "meta": meta, "page_key": "how-it-works"},
    )


@router.get("/demo-report")
async def demo_report(request: Request):
    settings = request.app.state.settings
    meta = make_meta(
        settings,
        path="/demo-report",
        title="Validuj demo report — sample startup validation output",
        description="See the structure of a Validuj report, from market context to final risk recommendation.",
        og_type="article",
        structured_data=demo_structured_data(settings),
    )
    return request.app.state.templates.TemplateResponse(
        "demo_report.html",
        {"request": request, "meta": meta, "page_key": "demo-report", "demo_report": DEMO_REPORT},
    )


@router.post("/runs")
async def submit_run(request: Request, idea_text: str = Form(...)):
    payload = CreateRunRequest(idea_text=idea_text)
    run_id = create_run(payload.idea_text)
    spawn_analysis(run_id, request.app.state.analysis_runner)
    return RedirectResponse(url=f"/runs/{run_id}", status_code=303)


@router.get("/runs/{run_id}")
async def run_detail(request: Request, run_id: str):
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    settings = request.app.state.settings
    meta = make_meta(
        settings,
        path=f"/runs/{run_id}",
        title=f"Validuj run {run_id}",
        description="Private analysis run detail page.",
        robots="noindex,nofollow",
    )
    return request.app.state.templates.TemplateResponse(
        "run.html",
        {"request": request, "meta": meta, "page_key": "run-detail", "run": run},
    )
