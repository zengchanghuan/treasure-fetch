"""
事件追踪接口与 SQLite 默认实现。

接口 (Protocol):
    EventTracker.track()  — 记录一条事件
    EventTracker.query()  — 按事件名 + 时间范围查询
    EventTracker.count()  — 按事件名 + 时间范围计数
    EventTracker.top()    — 按属性字段分组 Top-N

替换实现时只需满足 EventTracker Protocol 即可，无需继承。
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiosqlite


@runtime_checkable
class EventTracker(Protocol):
    async def track(self, event: str, properties: dict | None = None) -> None: ...
    async def query(
        self, event: str | None, start: datetime, end: datetime, limit: int = 500
    ) -> list[dict]: ...
    async def count(self, event: str | None, start: datetime, end: datetime) -> int: ...
    async def top(
        self, event: str, field: str, start: datetime, end: datetime, limit: int = 20
    ) -> list[dict]: ...
    async def daily_series(
        self, event: str | None, start: datetime, end: datetime
    ) -> list[dict]: ...


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    event     TEXT    NOT NULL,
    ts        REAL    NOT NULL,
    props     TEXT    NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS idx_event_ts ON events (event, ts);
"""


class SQLiteTracker:
    """基于 aiosqlite 的异步事件追踪器。"""

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

    async def track(self, event: str, properties: dict | None = None) -> None:
        db = await self._conn()
        await db.execute(
            "INSERT INTO events (event, ts, props) VALUES (?, ?, ?)",
            (event, time.time(), json.dumps(properties or {}, ensure_ascii=False)),
        )
        await db.commit()

    async def query(
        self, event: str | None, start: datetime, end: datetime, limit: int = 500
    ) -> list[dict]:
        db = await self._conn()
        if event:
            sql = "SELECT * FROM events WHERE event = ? AND ts BETWEEN ? AND ? ORDER BY ts DESC LIMIT ?"
            params = (event, start.timestamp(), end.timestamp(), limit)
        else:
            sql = "SELECT * FROM events WHERE ts BETWEEN ? AND ? ORDER BY ts DESC LIMIT ?"
            params = (start.timestamp(), end.timestamp(), limit)
        rows = await db.execute_fetchall(sql, params)
        return [
            {"id": r["id"], "event": r["event"], "ts": r["ts"], "props": json.loads(r["props"])}
            for r in rows
        ]

    async def count(self, event: str | None, start: datetime, end: datetime) -> int:
        db = await self._conn()
        if event:
            sql = "SELECT COUNT(*) as cnt FROM events WHERE event = ? AND ts BETWEEN ? AND ?"
            params = (event, start.timestamp(), end.timestamp())
        else:
            sql = "SELECT COUNT(*) as cnt FROM events WHERE ts BETWEEN ? AND ?"
            params = (start.timestamp(), end.timestamp())
        row = await db.execute_fetchall(sql, params)
        return row[0]["cnt"] if row else 0

    async def top(
        self, event: str, field: str, start: datetime, end: datetime, limit: int = 20
    ) -> list[dict]:
        db = await self._conn()
        sql = """
            SELECT json_extract(props, ?) as val, COUNT(*) as cnt
            FROM events
            WHERE event = ? AND ts BETWEEN ? AND ?
              AND json_extract(props, ?) IS NOT NULL
            GROUP BY val ORDER BY cnt DESC LIMIT ?
        """
        key = f"$.{field}"
        rows = await db.execute_fetchall(
            sql, (key, event, start.timestamp(), end.timestamp(), key, limit)
        )
        return [{"value": r["val"], "count": r["cnt"]} for r in rows]

    async def daily_series(
        self, event: str | None, start: datetime, end: datetime
    ) -> list[dict]:
        db = await self._conn()
        if event:
            sql = """
                SELECT date(ts, 'unixepoch') as day, COUNT(*) as cnt
                FROM events WHERE event = ? AND ts BETWEEN ? AND ?
                GROUP BY day ORDER BY day
            """
            params = (event, start.timestamp(), end.timestamp())
        else:
            sql = """
                SELECT date(ts, 'unixepoch') as day, COUNT(*) as cnt
                FROM events WHERE ts BETWEEN ? AND ?
                GROUP BY day ORDER BY day
            """
            params = (start.timestamp(), end.timestamp())
        rows = await db.execute_fetchall(sql, params)
        return [{"day": r["day"], "count": r["cnt"]} for r in rows]
