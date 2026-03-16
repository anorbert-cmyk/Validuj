# Validuj Project Architecture

## Overview

Validuj is a focused startup-validation web app built around a **six-stage expert workflow**.

The system takes a business idea, runs it through sequential specialist agents, and persists both:

- the user-visible markdown report
- the structured handoff state that flows from one agent to the next

This architecture is intentionally narrower than a full SaaS platform. It prioritizes the core differentiator:

1. research-backed analysis
2. stage-by-stage specialist handoff
3. model routing
4. live progress streaming
5. SEO-ready public pages

## Core product flow

1. User submits a business idea on the homepage or via API.
2. Server creates an `analysis_runs` row in SQLite.
3. Background runner starts a six-stage workflow.
4. Each stage:
   - reads the original idea
   - receives compact accumulated handoff from earlier stages
   - optionally performs web research
   - routes generation through the best available provider
   - persists markdown, summary, citations, and next-stage handoff
5. Run events are appended to the database and broadcast through SSE.
6. The run detail page streams live progress and reloads on completion.
7. Final report is stored in SQLite and remains available after restart.

## Six specialist stages

### 1. Market Scout

- identifies buyer profile
- clarifies pain points
- gathers demand signals with web research

### 2. Competitor Analyst

- examines direct and adjacent alternatives
- identifies whitespace
- frames differentiation

### 3. Strategy Architect

- defines beachhead segment
- recommends rollout priorities
- proposes positioning and milestones

### 4. Product Designer

- turns strategy into MVP workflow
- outlines information architecture
- emphasizes trust-aware UX

### 5. Edge-Case Reviewer

- stress-tests failure cases
- highlights compliance, trust, and review-state issues

### 6. Risk & Decision Analyst

- summarizes commercial, execution, and product risks
- proposes validation experiments
- produces the final recommendation

## Handoff model

Each completed stage stores:

- `summary`
- `key_findings`
- `next_focus`
- citations
- raw markdown

Only the compact `handoff` object is serialized forward into later prompts. The full markdown is stored for the report, but it is not blindly re-injected into every subsequent stage.

This keeps the pipeline predictable and mirrors the main value of more advanced recurrent-memory architectures without requiring a heavyweight orchestration framework.

## Runtime architecture

### Web layer

- **FastAPI backend**
- **Next.js frontend**

Public pages:

- Frontend:
  - `/`
  - `/how-it-works`
  - `/pricing`
  - `/demo-report`
  - `/security`
  - `/faq`
- Backend:
  - legacy SEO-ready public pages still exist during transition

Private run page:

- Frontend:
  - `/dashboard`
  - `/runs/{run_id}`
- Backend:
  - `/runs/{run_id}` remains available as the original server-rendered implementation

API endpoints:

- `GET /api/health`
- `GET /api/runs`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/stream/runs/{run_id}`
- `GET /robots.txt`
- `GET /sitemap.xml`

### Persistence

SQLite is used for reliability and zero external setup.

Tables:

- `analysis_runs`
- `stage_runs`
- `run_events`

This gives enough structure for:

- rerendering completed runs
- replaying SSE history
- inspecting per-stage provider/model choices

## Model routing

### Remote path

When `OPENROUTER_API_KEY` is configured, Validuj can route stage generation through OpenRouter.

Configured capabilities:

- research stages → research model
- strategy/risk stages → reasoning model
- design/edge-case stages → design model

### Local path

When no remote provider is configured, the app uses a **deterministic local synthesis engine**.

This local fallback is intentionally reliable and fast in a no-key development environment:

- no large model download required
- no GPU required
- produces stage-specific structured markdown
- still preserves the same six-stage handoff architecture

This means the product is always runnable, while remote best-in-class LLMs can be layered in through configuration.

## Search enrichment

Search is only applied where it adds real value:

- Market Scout
- Competitor Analyst

Provider order:

1. Tavily, when configured
2. DuckDuckGo search fallback

Search results are normalized into a consistent citation format:

- title
- URL
- snippet
- source

## Live streaming

The app uses:

- an in-memory event bus for current subscribers
- a persistent event log for replay

This supports two important UX paths:

1. live updates for an active run
2. event catch-up when the page reconnects after part of the run already finished

## Frontend layer

The repository now contains a dedicated `frontend/` Next.js application.

Current frontend responsibilities:

- marketing homepage
- methodology page
- pricing page
- demo report page
- security page
- FAQ page
- dashboard shell
- run detail shell with live SSE-backed updates

The frontend talks to the FastAPI backend over HTTP using:

- `GET /api/runs`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/stream/runs/{run_id}`

This is the first major step away from an all-in-one server-rendered product and toward a split frontend/backend production architecture.

## SEO architecture

SEO is intentionally scoped to the public product surface rather than user-generated pages.

### Indexable pages

- homepage
- methodology page
- pricing page
- demo report page
- security page
- FAQ page

These pages are:

- server-rendered
- semantically structured
- tagged with canonical, OG, Twitter, and description metadata
- included in `sitemap.xml`

### Non-indexable pages

- `/runs/{run_id}`

Run pages emit:

- `robots: noindex,nofollow`

This protects private, user-generated analysis pages from being indexed while keeping product discovery intact.

### Structured data

Public pages include JSON-LD for:

- `WebSite`
- `SoftwareApplication`
- `WebPage`
- `CreativeWork`

## Failure behavior

If a stage throws an exception:

- the current stage is marked failed
- the run is marked failed
- a `run_failed` event is stored and streamed

The system favors clarity over silent retries in this first version.

## Why this architecture

This design deliberately optimizes for:

- a real working product from an empty repository
- inspectable execution
- stable SEO behavior
- easy local development
- future upgrade paths to remote LLMs and more advanced orchestration

## Future extensions

Natural next steps include:

- authenticated private workspaces
- queued background workers
- richer multi-provider routing
- report export formats
- editable stage prompts
- validation experiment tracking
- blog/content engine on top of the existing SEO layer
