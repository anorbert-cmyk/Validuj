from __future__ import annotations

from fastapi import APIRouter, Depends

from app.repository import get_subscription, upsert_subscription
from app.security import require_session


router = APIRouter(prefix="/api/billing")

PLANS = [
    {
        "name": "explorer",
        "price": 49,
        "currency": "USD",
        "description": "Single-run starter tier for focused validation work.",
    },
    {
        "name": "builder",
        "price": 149,
        "currency": "USD",
        "description": "Multi-run tier for founders iterating on multiple opportunities.",
    },
    {
        "name": "studio",
        "price": 499,
        "currency": "USD",
        "description": "Ops-friendly team tier for more structured product validation work.",
    },
]


@router.get("/plans")
async def list_plans():
    return PLANS


@router.get("/subscription")
async def current_subscription(session=Depends(require_session)):
    subscription = get_subscription(session["email"])
    if subscription is None:
        return {
            "email": session["email"],
            "plan_name": "free",
            "status": "inactive",
        }
    return subscription.model_dump(mode="json")


@router.post("/subscription/{plan_name}")
async def select_subscription(plan_name: str, session=Depends(require_session)):
    chosen = next((plan for plan in PLANS if plan["name"] == plan_name), None)
    if chosen is None:
        return {"status": "invalid_plan"}
    subscription = upsert_subscription(session["email"], plan_name=plan_name, status="active")
    return subscription.model_dump(mode="json")
