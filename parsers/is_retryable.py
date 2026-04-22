import aiohttp
import asyncio


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, aiohttp.ClientResponseError):
        return exc.status in {429, 500, 502, 503, 504}
    return isinstance(exc, (aiohttp.ClientConnectionError, asyncio.TimeoutError))
