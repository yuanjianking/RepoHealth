import asyncio
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RepoEvent:
    repository: str
    event_type: str
    payload: Dict[str, Any]


class RepoEventQueue:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[RepoEvent] = asyncio.Queue()

    async def enqueue(self, event: RepoEvent) -> None:
        await self._queue.put(event)

    async def dequeue(self) -> RepoEvent:
        return await self._queue.get()

    def task_done(self) -> None:
        self._queue.task_done()

    def qsize(self) -> int:
        return self._queue.qsize()


event_queue = RepoEventQueue()
