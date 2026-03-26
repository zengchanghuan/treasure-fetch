"""
管理后台路由。

- GET  /admin        → 仪表盘页面（Basic Auth 保护）
- GET  /admin/api/*  → 仪表盘数据接口
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from backend.analytics import get_tracker
from backend.config import settings

router = APIRouter(tags=["admin"])
_security = HTTPBasic()

_DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"


def _verify(creds: HTTPBasicCredentials = Depends(_security)) -> str:
    correct = secrets.compare_digest(creds.password, settings.admin_password)
    if not (creds.username == "admin" and correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return creds.username


def _range(days: int = 7) -> tuple[datetime, datetime]:
    """返回最近 N 天的时间范围（UTC）。"""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return start, end


@router.get("", response_class=HTMLResponse)
async def dashboard(_user: str = Depends(_verify)):
    return HTMLResponse(_DASHBOARD_HTML.read_text(encoding="utf-8"))


@router.get("/api/summary")
async def summary(days: int = 7, _user: str = Depends(_verify)):
    tracker = get_tracker()
    start, end = _range(days)
    pv = await tracker.count("page_view", start, end)
    resolves = await tracker.count("metadata_resolve", start, end)
    downloads = await tracker.count("download_start", start, end)
    completes = await tracker.count("download_complete", start, end)
    errors = await tracker.count("download_error", start, end)
    return {
        "days": days,
        "page_views": pv,
        "resolves": resolves,
        "downloads": downloads,
        "completes": completes,
        "errors": errors,
        "error_rate": round(errors / max(downloads, 1) * 100, 1),
    }


@router.get("/api/daily")
async def daily(days: int = 30, event: str | None = None, _user: str = Depends(_verify)):
    tracker = get_tracker()
    start, end = _range(days)
    series = await tracker.daily_series(event, start, end)
    return {"event": event, "series": series}


@router.get("/api/top_artworks")
async def top_artworks(days: int = 7, _user: str = Depends(_verify)):
    tracker = get_tracker()
    start, end = _range(days)
    return await tracker.top("download_start", "artwork_id", start, end, limit=20)


@router.get("/api/level_distribution")
async def level_distribution(days: int = 7, _user: str = Depends(_verify)):
    tracker = get_tracker()
    start, end = _range(days)
    return await tracker.top("download_start", "level", start, end, limit=10)
