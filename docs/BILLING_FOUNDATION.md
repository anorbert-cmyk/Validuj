# Billing Foundation

## Overview

Validuj now includes a billing foundation that supports:

- plan catalog
- authenticated subscription state
- plan-aware run limits
- checkout destination generation

This is not yet a full production payment integration, but it is intentionally structured so that a real card processor can be connected without redesigning the product shell.

## Current plan catalog

| Plan | Price | Run limit | Purpose |
|------|-------|-----------|---------|
| `free` | $0 | 1 | Trial usage |
| `explorer` | $49 | 3 | Starter validation work |
| `builder` | $149 | 20 | Repeated founder workflows |
| `studio` | $499 | 100 | Team / ops usage |

## Current backend endpoints

- `GET /api/billing/plans`
- `GET /api/billing/subscription`
- `POST /api/billing/subscription/{plan_name}`
- `POST /api/billing/checkout/{plan_name}`
- `POST /api/webhooks/stripe`

## Current behavior

### Subscription state

- if the user has no stored subscription, they are treated as `free`
- `run_limit` is returned as part of the subscription payload

### Run enforcement

- protected `POST /api/runs` checks the current plan’s run limit
- if the user has already reached the limit, the request is rejected with `403`

### Checkout mode

The checkout endpoint currently supports two modes:

#### 1. Mock mode

Used when Stripe keys are not configured.

Response example:

```json
{
  "provider": "mock",
  "checkout_url": "http://127.0.0.1:3000/settings?checkout=mock&plan=builder",
  "publishable_key": null
}
```

#### 2. Stripe-ready mode

Used when these values are configured:

- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`

Then the backend creates a Stripe Checkout Session and returns its URL.

## Webhook handling

The backend now includes a Stripe webhook endpoint:

- `POST /api/webhooks/stripe`

Behavior:

- verifies Stripe signature when Stripe env vars are configured
- records billing events into local persistence
- on `checkout.session.completed`, reads metadata and upgrades the matching subscription

Current expectation:

- the checkout session includes `plan_name` and `email` in metadata
- webhook reconciliation becomes the authoritative upgrade path once real Stripe is active

## Environment variables

```env
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
FRONTEND_BASE_URL=http://127.0.0.1:3000
```

## Security notes

- checkout requires authenticated session
- checkout mutation requires CSRF header + cookie match
- plan selection mutation also requires CSRF
- run creation is plan-gated server-side, not only in the UI

## Next steps for real payment integration

To move from foundation to real production billing:

1. persist Stripe customer IDs
2. map plan names to real Stripe Price IDs
3. add webhook processing for successful checkout / subscription updates
4. store billing events and reconciliation state
5. add billing portal link handling
6. lock premium capabilities behind confirmed billing state
