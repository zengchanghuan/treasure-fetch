"""
管理后台路由。

- GET  /admin           → 登录页 或 仪表盘（根据 session 判断）
- POST /admin/login     → 验证密码，设置 cookie
- GET  /admin/logout    → 清除 cookie
- GET  /admin/api/*     → 仪表盘数据接口（cookie 鉴权）
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite
from fastapi import APIRouter, Cookie, HTTPException, Request, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

from backend.analytics import get_tracker
from backend.config import settings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_FEEDBACK_IMAGE_DIR = _PROJECT_ROOT / "data" / "feedback-images"

router = APIRouter(tags=["admin"])

_DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"
_LOGIN_HTML = Path(__file__).parent / "login.html"

_SESSION_SECRET = secrets.token_hex(32)
_SESSION_MAX_AGE = 86400


def _sign_token(ts: int) -> str:
    payload = f"admin:{ts}"
    sig = hmac.new(_SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:24]
    return f"{payload}:{sig}"


def _verify_token(token: str | None) -> bool:
    if not token:
        return False
    try:
        parts = token.rsplit(":", 1)
        if len(parts) != 2:
            return False
        payload, sig = parts
        expected = hmac.new(_SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:24]
        if not hmac.compare_digest(sig, expected):
            return False
        ts = int(payload.split(":")[1])
        return (time.time() - ts) < _SESSION_MAX_AGE
    except (ValueError, IndexError):
        return False


def _require_auth(admin_token: str | None = Cookie(None)):
    if not _verify_token(admin_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def _range(days: int = 7) -> tuple[datetime, datetime]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return start, end


@router.get("", response_class=HTMLResponse)
async def admin_index(admin_token: str | None = Cookie(None)):
    if _verify_token(admin_token):
        return HTMLResponse(_DASHBOARD_HTML.read_text(encoding="utf-8"))
    return HTMLResponse(_LOGIN_HTML.read_text(encoding="utf-8"))


@router.post("/login")
async def admin_login(request: Request):
    form = await request.form()
    password = form.get("password", "")
    if not secrets.compare_digest(str(password), settings.admin_password):
        html = _LOGIN_HTML.read_text(encoding="utf-8").replace(
            "<!--ERROR-->",
            '<div class="error">密码错误，请重试</div>',
        )
        return HTMLResponse(html, status_code=401)
    token = _sign_token(int(time.time()))
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie("admin_token", token, httponly=True, max_age=_SESSION_MAX_AGE, samesite="lax")
    return resp


@router.get("/logout")
async def admin_logout():
    resp = RedirectResponse("/admin", status_code=303)
    resp.delete_cookie("admin_token")
    return resp


@router.get("/api/summary")
async def summary(days: int = 7, admin_token: str | None = Cookie(None)):
    _require_auth(admin_token)
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
async def daily(days: int = 30, event: str | None = None, admin_token: str | None = Cookie(None)):
    _require_auth(admin_token)
    tracker = get_tracker()
    start, end = _range(days)
    series = await tracker.daily_series(event, start, end)
    return {"event": event, "series": series}


@router.get("/api/top_artworks")
async def top_artworks(days: int = 7, admin_token: str | None = Cookie(None)):
    _require_auth(admin_token)
    tracker = get_tracker()
    start, end = _range(days)
    return await tracker.top("download_start", "artwork_id", start, end, limit=20)


@router.get("/api/level_distribution")
async def level_distribution(days: int = 7, admin_token: str | None = Cookie(None)):
    _require_auth(admin_token)
    tracker = get_tracker()
    start, end = _range(days)
    return await tracker.top("download_start", "level", start, end, limit=10)


@router.get("/api/feedback")
async def list_feedback(limit: int = 50, admin_token: str | None = Cookie(None)):
    """返回最新用户反馈列表。"""
    _require_auth(admin_token)
    db_path = settings.db_abs_path
    async with aiosqlite.connect(str(db_path)) as db:
        db.row_factory = aiosqlite.Row
        try:
            cur = await db.execute(
                "SELECT id, ts, ip, text, image FROM feedback ORDER BY ts DESC LIMIT ?",
                (limit,),
            )
            rows = await cur.fetchall()
        except Exception:
            return []
    return [
        {
            "id": r["id"],
            "ts": r["ts"],
            "ip": r["ip"],
            "text": r["text"],
            "image": r["image"],
        }
        for r in rows
    ]


@router.get("/feedback-image/{filename}")
async def feedback_image(filename: str, admin_token: str | None = Cookie(None)):
    """鉴权后提供反馈图片。"""
    _require_auth(admin_token)
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400)
    path = _FEEDBACK_IMAGE_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(str(path))
