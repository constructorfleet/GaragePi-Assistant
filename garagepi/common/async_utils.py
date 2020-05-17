import asyncio
import functools


async def run_in_executor(function, *args, **kwargs):
    """Runs a function in an asynchronous executor."""
    loop = asyncio.get_event_loop()
    completed, pending = await asyncio.wait(
        [loop.run_in_executor(self.AD.executor, functools.partial(function, *args, **kwargs))])
    future = list(completed)[0]
    response = future.result()
    return response


def create_task(coroutine):
    """Schedules a coroutine to be run."""
    return asyncio.get_event_loop().create_task(coroutine)
