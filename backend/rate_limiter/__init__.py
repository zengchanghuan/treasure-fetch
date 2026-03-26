"""
Rate Limiter 限流模块。

用法::

    from backend.rate_limiter import get_limiter

    limiter = get_limiter()
    result = await limiter.check("dl:1.2.3.4", limit=5, window_sec=60)
    if not result.allowed:
        raise HTTPException(429)
"""

from __future__ import annotations

from .limiter import MemoryLimiter, RateLimiter, RateLimitResult, SQLiteLimiter

_instance: MemoryLimiter | None = None


def get_limiter() -> MemoryLimiter:
    """返回全局单例 Limiter。默认使用 MemoryLimiter（生产环境可切换为 SQLiteLimiter）。"""
    global _instance
    if _instance is None:
        _instance = MemoryLimiter()
    return _instance


__all__ = ["RateLimiter", "RateLimitResult", "MemoryLimiter", "SQLiteLimiter", "get_limiter"]
