# RepoHealth Backend

A FastAPI backend for RepoHealth that receives GitHub webhook events, stores event history in JSONL files, and exposes repository health endpoints.

## Features

- Accepts GitHub webhook events at `/api/v1/repo/webhook`
- Queues incoming webhook payloads for asynchronous processing
- Stores event history in per-repository JSONL files
- Generates `dashboard.jsonl` records from event history
- Exposes repo health APIs for frontend consumption
- Includes unit tests for storage, history, processing, and API behavior

## Requirements

- Python 3.10+
- Poetry-managed dependencies in `pyproject.toml`
- Virtual environment under `.venv`

## Setup

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r <(poetry export -f requirements.txt --without-hashes)
```

> If you use Poetry directly, run:
>
> ```bash
> cd backend
> poetry install
> ```

## Run

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open API docs at `http://localhost:8000/docs`.

## API Endpoints

- `GET /api/v1/repo/health/{owner}/{repo}`
- `GET /api/v1/repo/code-health/{owner}/{repo}`
- `GET /api/v1/repo/team-work/{owner}/{repo}`
- `GET /api/v1/repo/risk-analysis/{owner}/{repo}`
- `POST /api/v1/repo/webhook`

## Webhook Usage

Use GitHub webhook payload URL:

```text
https://<your-host>/api/v1/repo/webhook
```

Headers:

- `Content-Type: application/json`
- `X-GitHub-Event: <event-name>`

Supported event types:

- `issues`
- `pull_request`
- `issue_comment`
- `pull_request_review`
- `push`

The backend reads repository info from `payload.repository.full_name`.

## Data Storage

Data is stored under `backend/data/dashboard/<repo_name>/`.

Files include:

- `issues.jsonl` — GitHub `issues` event history
- `pull_requests.jsonl` — GitHub `pull_request` event history
- `issue_comments.jsonl` — GitHub `issue_comment` history
- `pull_request_reviews.jsonl` — GitHub `pull_request_review` history
- `pushes.jsonl` — GitHub `push` history
- `dashboard.jsonl` — generated dashboard snapshots

Each JSONL file stores one JSON object per line.

## Tests

Run backend tests with:

```bash
cd backend
.venv/bin/pytest -q tests
```

Current tests cover:

- storage service
- event history persistence
- dashboard generation from history
- webhook route acceptance
- repo API endpoints

## Notes

- The queue implementation is currently in-memory and works inside a single backend process.
- For production reliability, replace the in-memory queue with a persistent broker such as Redis or RabbitMQ.
