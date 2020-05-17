import asyncio


def create_task(coroutine):
    """Schedules a coroutine to be run."""
    return asyncio.get_event_loop().create_task(coroutine)
