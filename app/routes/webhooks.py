from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request

from app.payments import verify_stripe_webhook
from app.repository import record_billing_event, upsert_subscription


router = APIRouter(prefix="/api/webhooks")


@router.post("/stripe")
async def stripe_webhook(request: Request):
    settings = request.app.state.settings
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not settings.stripe_secret_key or not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")
    if not signature:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        event = verify_stripe_webhook(settings, payload, signature)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Stripe webhook: {exc}") from exc

    event_type = event.get("type", "unknown")
    data_object = event.get("data", {}).get("object", {})
    reference_id = data_object.get("id")
    record_billing_event(
        provider="stripe",
        event_type=event_type,
        reference_id=reference_id,
        payload=json.loads(json.dumps(event)),
    )

    if event_type == "checkout.session.completed":
        metadata = data_object.get("metadata", {}) or {}
        email = data_object.get("customer_email") or metadata.get("email")
        plan_name = metadata.get("plan_name")
        if email and plan_name:
            upsert_subscription(email, plan_name=plan_name, status="active")

    return {"status": "ok"}
