"""
限流接口与实现。

提供两种实现：
  MemoryLimiter  — 内存滑动窗口，进程重启后重置（开发 / 单机）
  SQLiteLimiter  — 持久化滑动窗口，重启不丢失（生产）

替换时只需实现 RateLimiter Protocol。
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiosqlite


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: float = 0.0


@runtime_checkable
class RateLimiter(Protocol):
    async def check(self, key: str, limit: int, window_sec: int) -> RateLimitResult: ...
    async def get_remaining(self, key: str, limit: int, window_sec: int) -> int: ...


class MemoryLimiter:
    """进程内滑动窗口限流。"""

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def check(self, key: str, limit: int, window_sec: int) -> RateLimitResult:
        now = time.time()
        bucket = self._buckets[key]
        self._buckets[key] = bucket = [t for t in bucket if now - t < window_sec]
        if len(bucket) >= limit:
            oldest = bucket[0]
            retry_after = window_sec - (now - oldest)
            return RateLimitResult(allowed=False, remaining=0, retry_after=max(retry_after, 0))
        bucket.append(now)
        return RateLimitResult(allowed=True, remaining=limit - len(bucket))

    async def get_remaining(self, key: str, limit: int, window_sec: int) -> int:
        now = time.time()
        bucket = self._buckets.get(key, [])
        active = [t for t in bucket if now - t < window_sec]
        return max(0, limit - len(active))


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS rate_events (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    key   TEXT NOT NULL,
    ts    REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_rate_key_ts ON rate_events (key, ts);
"""


class SQLiteLimiter:
    """基于 SQLite 的持久化滑动窗口限流。"""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._db: aiosqlite.Connection | None = None

    async def _conn(self) -> aiosqlite.Connection:
        if self._db is None:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            self._db = await aiosqlite.connect(self._db_path)
            self._db.row_factory = aiosqlite.Row
            await self._db.executescript(_CREATE_SQL)
        return self._db

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def check(self, key: str, limit: int, window_sec: int) -> RateLimitResult:
        db = await self._conn()
        now = time.time()
        cutoff = now - window_sec

        await db.execute("DELETE FROM rate_events WHERE ts < ?", (cutoff,))
        row = await db.execute_fetchall(
            "SELECT COUNT(*) as cnt FROM rate_events WHERE key = ? AND ts >= ?",
            (key, cutoff),
        )
        count = row[0]["cnt"] if row else 0

        if count >= limit:
            oldest_row = await db.execute_fetchall(
                "SELECT MIN(ts) as oldest FROM rate_events WHERE key = ? AND ts >= ?",
                (key, cutoff),
            )
            oldest = oldest_row[0]["oldest"] if oldest_row and oldest_row[0]["oldest"] else now
            retry_after = window_sec - (now - oldest)
            return RateLimitResult(allowed=False, remaining=0, retry_after=max(retry_after, 0))

        await db.execute("INSERT INTO rate_events (key, ts) VALUES (?, ?)", (key, now))
        await db.commit()
        return RateLimitResult(allowed=True, remaining=limit - count - 1)

    async def get_remaining(self, key: str, limit: int, window_sec: int) -> int:
        db = await self._conn()
        now = time.time()
        cutoff = now - window_sec
        row = await db.execute_fetchall(
            "SELECT COUNT(*) as cnt FROM rate_events WHERE key = ? AND ts >= ?",
            (key, cutoff),
        )
        count = row[0]["cnt"] if row else 0
        return max(0, limit - count)
