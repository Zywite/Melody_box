"""Redis and arq helpers: connection pool, job enqueue, FFT cache."""

import os

from arq import create_pool
from arq.connections import RedisSettings

from app.core.constants import FFT_CACHE_KEY_PREFIX, FFT_CACHE_TTL_SECONDS

_redis_pool = None


def get_redis_settings() -> RedisSettings:
    """Build ``RedisSettings`` from ``REDIS_HOST``/``PORT``/``DB`` env vars.

    Defaults to ``localhost:6379`` database 0.
    """
    return RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        database=int(os.getenv("REDIS_DB", "0")),
    )


async def get_redis():
    """Return the lazily-created arq Redis pool, or None if unreachable."""
    global _redis_pool
    if _redis_pool is None:
        try:
            settings = get_redis_settings()
            _redis_pool = await create_pool(settings)
        except Exception:
            _redis_pool = None
    return _redis_pool


async def enqueue_job(func_name: str, *args, **kwargs) -> str | None:
    """Enqueue an arq job by registered function name.

    Returns:
        The arq ``job_id`` on success, or None if Redis is unavailable or
        the enqueue raised.
    """
    redis = await get_redis()
    if redis is None:
        return None
    try:
        job = await redis.enqueue_job(func_name, *args, **kwargs)
        return job.job_id if job else None
    except Exception:
        return None


async def cache_set_fft(song_id: str, fft_json: str) -> None:
    """Cache the FFT JSON for a song under ``fft:{song_id}`` for 24h.

    Failures are swallowed because the cache is a best-effort optimisation.
    """
    redis = await get_redis()
    if redis is None:
        return
    try:
        await redis.setex(f"{FFT_CACHE_KEY_PREFIX}{song_id}", FFT_CACHE_TTL_SECONDS, fft_json)
    except Exception:
        pass


async def cache_get_fft(song_id: str) -> str | None:
    """Return cached FFT JSON for a song, or None on miss or error."""
    redis = await get_redis()
    if redis is None:
        return None
    try:
        return await redis.get(f"{FFT_CACHE_KEY_PREFIX}{song_id}")
    except Exception:
        return None
