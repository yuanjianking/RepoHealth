import asyncio
from typing import Optional

from app.core.logger import get_logger
from app.services.event_history_service import EventHistoryService
from app.services.event_queue import RepoEvent, RepoEventQueue
from app.services.repo_event_service import RepoEventProcessor
from app.services.storage_service import StorageService

logger = get_logger()


async def run_event_worker(
    storage: StorageService,
    history_service: EventHistoryService,
    queue: RepoEventQueue,
) -> None:
    processor = RepoEventProcessor(storage, history_service)

    while True:
        try:
            event = await queue.dequeue()
            try:
                processor.process_event(event.repository, event.event_type, event.payload)
            except Exception as exc:
                logger.error(f"Event worker failed to process event: {exc}")
            finally:
                queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error(f"Unexpected event worker error: {exc}")
            await asyncio.sleep(1)
