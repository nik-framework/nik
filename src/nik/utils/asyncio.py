from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


async def run_sync_in_thread(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Run a synchronous callable in the default asyncio thread pool.
    ContextVars are automatically propagated by asyncio.to_thread.
    """
    return await asyncio.to_thread(func, *args, **kwargs)
