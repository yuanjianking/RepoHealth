import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status

from app.services.event_queue import RepoEvent, event_queue

logger = logging.getLogger(__name__)

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
    # Log incoming request for debugging
    logger.info(f"Received webhook request from {request.client.host if request.client else 'unknown'}")
    logger.info(f"Headers: {dict(request.headers)}")

    event_type = _get_event_type(request)
    logger.info(f"GitHub Event type: {event_type}")

    if not event_type:
        logger.error("Missing X-GitHub-Event header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-GitHub-Event header",
        )

    try:
        # Read the request body as text first for debugging
        body_bytes = await request.body()
        body_text = body_bytes.decode('utf-8')

        if not body_text or body_text.strip() == "":
            logger.error("Empty request body received")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty request body",
            )

        logger.info(f"Request body length: {len(body_text)} chars")
        logger.info(f"Request body preview: {body_text[:200]}")

        # Parse JSON
        payload: Dict[str, Any] = json.loads(body_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error reading request body: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing request: {str(e)}",
        )

    repository = _get_repository_name(payload)
    logger.info(f"Repository: {repository}")

    if not repository:
        logger.error("Missing repository information in payload")
        logger.error(f"Payload keys: {list(payload.keys())}")
        if 'repository' in payload:
            logger.error(f"Repository object: {payload['repository']}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing repository information in webhook payload",
        )

    try:
        background_tasks.add_task(
            event_queue.enqueue,
            RepoEvent(repository=repository, event_type=event_type, payload=payload),
        )
        logger.info(f"Event queued successfully: {event_type} for {repository}")
    except Exception as e:
        logger.error(f"Failed to enqueue event: {e}")
        # Still return 202 as the webhook was received, but log the error
        # This follows the GitHub webhook pattern - accept first, process later

    return {
        "message": "event queued",
        "repository": repository,
        "event": event_type,
    }
