from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.payments import create_checkout_destination
from app.repository import get_subscription, upsert_subscription
from app.security import require_csrf, require_session


router = APIRouter(prefix="/api/billing")

PLANS = [
    {
        "name": "free",
        "price": 0,
        "currency": "USD",
        "run_limit": 1,
        "description": "Starter access for trying the product with a single owned run.",
    },
    {
        "name": "explorer",
        "price": 49,
        "currency": "USD",
        "run_limit": 3,
        "description": "Single-run starter tier for focused validation work.",
    },
    {
        "name": "builder",
        "price": 149,
        "currency": "USD",
        "run_limit": 20,
        "description": "Multi-run tier for founders iterating on multiple opportunities.",
    },
    {
        "name": "studio",
        "price": 499,
        "currency": "USD",
        "run_limit": 100,
        "description": "Ops-friendly team tier for more structured product validation work.",
    },
]


def get_plan_definition(plan_name: str) -> dict | None:
    return next((plan for plan in PLANS if plan["name"] == plan_name), None)


@router.get("/plans")
async def list_plans():
    return PLANS


@router.get("/subscription")
async def current_subscription(session=Depends(require_session)):
    subscription = get_subscription(session["email"])
    if subscription is None:
        plan = get_plan_definition("free")
        return {
            "email": session["email"],
            "plan_name": "free",
            "status": "inactive",
            "run_limit": plan["run_limit"] if plan else 1,
        }
    plan = get_plan_definition(subscription.plan_name)
    payload = subscription.model_dump(mode="json")
    payload["run_limit"] = plan["run_limit"] if plan else 0
    return payload


@router.post("/subscription/{plan_name}")
async def select_subscription(
    plan_name: str,
    session=Depends(require_session),
    _: None = Depends(require_csrf),
):
    chosen = get_plan_definition(plan_name)
    if chosen is None:
        return {"status": "invalid_plan"}
    if plan_name != "free" and session["role"] != "admin":
        return {"status": "payment_required"}
    subscription = upsert_subscription(session["email"], plan_name=plan_name, status="active")
    return subscription.model_dump(mode="json")


@router.post("/checkout/{plan_name}")
async def create_checkout(
    request: Request,
    plan_name: str,
    session=Depends(require_session),
    _: None = Depends(require_csrf),
):
    chosen = get_plan_definition(plan_name)
    if chosen is None or plan_name == "free":
        return {"status": "invalid_plan"}
    payload = create_checkout_destination(
        request.app.state.settings,
        plan_name=plan_name,
        email=session["email"],
    )
    return payload
