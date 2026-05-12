import os
from typing import Optional
from arq import create_pool
from arq.connections import RedisSettings

_redis_pool = None


def get_redis_settings():
    return RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        database=int(os.getenv("REDIS_DB", "0")),
    )


async def get_redis():
    global _redis_pool
    if _redis_pool is None:
        try:
            settings = get_redis_settings()
            _redis_pool = await create_pool(settings)
        except Exception:
            _redis_pool = None
    return _redis_pool


async def enqueue_job(func_name: str, *args, **kwargs) -> Optional[str]:
    redis = await get_redis()
    if redis is None:
        return None
    try:
        job = await redis.enqueue_job(func_name, *args, **kwargs)
        return job.job_id if job else None
    except Exception:
        return None


async def cache_set_fft(song_id: str, fft_json: str) -> None:
    redis = await get_redis()
    if redis is None:
        return
    try:
        await redis.setex(f"fft:{song_id}", 86400, fft_json)
    except Exception:
        pass


async def cache_get_fft(song_id: str) -> Optional[str]:
    redis = await get_redis()
    if redis is None:
        return None
    try:
        return await redis.get(f"fft:{song_id}")
    except Exception:
        return None
