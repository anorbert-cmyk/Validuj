# Validuj

Validuj is a working multi-agent startup validation app.

It takes a business idea, runs it through **six specialist stages**, passes structured handoff state between them, stores the full run in SQLite, streams progress via SSE, and exposes SEO-ready public pages for product discovery.

## What it does

- six-stage expert workflow
  1. Market Scout
  2. Competitor Analyst
  3. Strategy Architect
  4. Product Designer
  5. Edge-Case Reviewer
  6. Risk & Decision Analyst
- structured handoff between stages
- live web research in the first two stages
- model routing with remote provider support
- deterministic local fallback for no-key environments
- live run streaming over Server-Sent Events
- persistent reports in SQLite
- public SEO pages + private `noindex` run pages

## Stack

- Python 3.12
- FastAPI
- Jinja2 templates
- SQLite
- DuckDuckGo / Tavily search
- OpenRouter-compatible remote model routing

## Project structure

```text
app/
  agents/              # six stage specs
  providers/           # local + OpenRouter providers
  routes/              # web, api, stream, seo routes
  services/            # analysis runner, search, model router, handoff, event bus
  static/              # CSS + browser JS
  templates/           # server-rendered pages
docs/
  PROJECT_ARCHITECTURE.md
```

## Setup

### 1. Install dependencies

```bash
pip3 install --user -r requirements.txt
```

### 2. Optional configuration

Copy `.env.example` values into your shell environment if you want to use:

- OpenRouter remote models
- Tavily search

Without any keys, the app still works using the local synthesis engine and DuckDuckGo fallback.

### 3. Run the app

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/`

## Endpoints

### Public pages

- `/`
- `/how-it-works`
- `/demo-report`
- `/robots.txt`
- `/sitemap.xml`

### API

- `GET /api/health`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/stream/runs/{run_id}`

## Example API request

```bash
curl -X POST "http://127.0.0.1:8000/api/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "idea_text": "An AI copilot for independent physiotherapists that turns treatment notes into reimbursement-ready documentation and patient follow-up plans."
  }'
```

## SEO behavior

### Indexable

- homepage
- methodology page
- demo report

### Not indexable

- `/runs/{run_id}`

Run pages emit:

```html
<meta name="robots" content="noindex,nofollow" />
```

## Notes on model routing

### Remote

If `OPENROUTER_API_KEY` is present, the app can route:

- research stages to a research-focused model
- strategy/risk stages to a reasoning model
- design/edge-case stages to a design-friendly model

### Local

If no remote model is configured, the app uses a deterministic local synthesis engine. This keeps the app fully runnable and testable in development while preserving the same stage-by-stage orchestration.

## Architecture doc

See:

- `docs/PROJECT_ARCHITECTURE.md`
