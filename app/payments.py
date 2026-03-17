from __future__ import annotations

from typing import Any

import stripe

from app.config import Settings


def create_checkout_destination(settings: Settings, *, plan_name: str, email: str) -> dict[str, Any]:
    if settings.stripe_secret_key and settings.stripe_publishable_key:
        stripe.api_key = settings.stripe_secret_key
        session = stripe.checkout.Session.create(
            mode="payment",
            success_url=f"{settings.frontend_base_url}/settings?checkout=success&plan={plan_name}",
            cancel_url=f"{settings.frontend_base_url}/pricing?checkout=cancelled",
            customer_email=email,
            metadata={
                "plan_name": plan_name,
                "email": email,
            },
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Validuj {plan_name.title()} plan",
                        },
                        "unit_amount": _plan_amount(plan_name),
                    },
                    "quantity": 1,
                }
            ],
        )
        return {
            "provider": "stripe",
            "checkout_url": session.url,
            "publishable_key": settings.stripe_publishable_key,
        }

    return {
        "provider": "mock",
        "checkout_url": f"{settings.frontend_base_url}/settings?checkout=mock&plan={plan_name}",
        "publishable_key": None,
    }


def _plan_amount(plan_name: str) -> int:
    mapping = {
        "explorer": 4900,
        "builder": 14900,
        "studio": 49900,
    }
    return mapping.get(plan_name, 0)


def verify_stripe_webhook(settings: Settings, payload: bytes, signature: str):
    stripe.api_key = settings.stripe_secret_key
    if not settings.stripe_webhook_secret:
        raise ValueError("Missing Stripe webhook secret")
    return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
