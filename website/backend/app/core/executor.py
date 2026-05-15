import asyncio

async def run_in_process(func, *args, **kwargs):
    """
    Utility to run ML tasks in a separate thread.
    Since pandas and scikit-learn release the GIL during heavy operations,
    this prevents FastAPI's event loop from blocking without the overhead
    of inter-process pickling (which breaks in-memory session objects).
    """
    return await asyncio.to_thread(func, *args, **kwargs)
