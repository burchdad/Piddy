"""
Background Worker Template
===========================
Async task processor with graceful shutdown.

Usage:
    cp -r templates/worker/ src/workers/my_worker/
    # Implement process_task() with your logic
"""
import asyncio
import logging
import signal
from typing import Any

logger = logging.getLogger(__name__)

_shutdown = asyncio.Event()


async def process_task(task: Any) -> None:
    """Override this with your task processing logic."""
    logger.info(f"Processing: {task}")
    await asyncio.sleep(1)  # Simulate work


async def task_queue() -> asyncio.Queue:
    """Replace with your actual task source (Redis, RabbitMQ, DB polling, etc.)."""
    queue: asyncio.Queue = asyncio.Queue()
    # Example: pre-load some tasks
    for i in range(5):
        await queue.put(f"task-{i}")
    return queue


async def worker_loop(queue: asyncio.Queue, worker_id: int = 0) -> None:
    logger.info(f"Worker-{worker_id} started")
    while not _shutdown.is_set():
        try:
            task = await asyncio.wait_for(queue.get(), timeout=1.0)
            await process_task(task)
            queue.task_done()
        except asyncio.TimeoutError:
            continue
        except Exception:
            logger.exception("Task failed")
    logger.info(f"Worker-{worker_id} stopped")


async def main(num_workers: int = 3) -> None:
    queue = await task_queue()
    workers = [asyncio.create_task(worker_loop(queue, i)) for i in range(num_workers)]
    await _shutdown.wait()
    for w in workers:
        w.cancel()
    await asyncio.gather(*workers, return_exceptions=True)


def handle_signal(*_: Any) -> None:
    _shutdown.set()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    asyncio.run(main())
