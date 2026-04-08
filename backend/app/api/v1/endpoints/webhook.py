from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.services.event_queue import RepoEvent, event_queue

router = APIRouter()


def _get_event_type(request: Request) -> str:
    return request.headers.get("X-GitHub-Event", request.headers.get("x-github-event", ""))


def _get_repository_name(payload: Dict[str, Any]) -> str:
    repository = payload.get("repository") or {}
    full_name = repository.get("full_name")
    if full_name:
        return full_name

    owner = repository.get("owner", {}).get("login")
    name = repository.get("name")
    if owner and name:
        return f"{owner}/{name}"

    return ""


@router.post("/webhook", status_code=status.HTTP_202_ACCEPTED)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    event_type = _get_event_type(request)
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-GitHub-Event header",
        )

    payload: Dict[str, Any] = await request.json()
    repository = _get_repository_name(payload)
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing repository information in webhook payload",
        )

    background_tasks.add_task(
        event_queue.enqueue,
        RepoEvent(repository=repository, event_type=event_type, payload=payload),
    )

    return {
        "message": "event queued",
        "repository": repository,
        "event": event_type,
    }
