"""
FastAPI 应用入口。

路由：
  GET  /                     → 前端页面
  POST /api/metadata         → 根据 URL 获取作品元数据
  POST /api/download         → 发起下载任务
  GET  /api/progress/{task}  → 轮询下载进度
  GET  /api/result/{task}    → 获取最终图片
  POST /api/event            → 前端埋点上报
  GET  /api/quota            → 查询 IP 剩余额度
"""

from __future__ import annotations

import asyncio
import time
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .admin import admin_router
from .analytics import get_tracker
from .config import settings
from .rate_limiter import get_limiter
from .seo import seo_router
from .tile_service import (
    ArtworkMeta,
    DownloadProgress,
    download_and_stitch,
    fetch_metadata,
    parse_url,
)

app = FastAPI(title="Treasure Fetch — 高清书画下载服务")
app.include_router(admin_router, prefix="/admin")
app.include_router(seo_router)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else "unknown")


STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── 内存任务池（轻量级；生产可换 Redis） ─────────────────────
_tasks: dict[str, dict] = {}


# ── 请求 / 响应模型 ──────────────────────────────────────────
class MetadataRequest(BaseModel):
    url: str


class DownloadRequest(BaseModel):
    url: str
    level: int


class TaskResponse(BaseModel):
    task_id: str


class ProgressResponse(BaseModel):
    total: int
    done: int
    status: str
    message: str
    filename: str = ""


# ── 路由 ─────────────────────────────────────────────────────
@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


class EventRequest(BaseModel):
    event: str
    properties: dict = {}


@app.post("/api/event")
async def track_event(req: EventRequest, request: Request):
    """前端埋点上报。"""
    props = {**req.properties, "ip": _get_client_ip(request)}
    await get_tracker().track(req.event, props)
    return {"ok": True}


@app.post("/api/metadata")
async def get_metadata(req: MetadataRequest, request: Request):
    ip = _get_client_ip(request)
    limiter = get_limiter()
    result = await limiter.check(f"meta:{ip}", settings.rate_limit_metadata_per_min, 60)
    if not result.allowed:
        raise HTTPException(status_code=429, detail=f"请求过于频繁，请 {result.retry_after:.0f} 秒后再试")

    try:
        art_type, art_id = parse_url(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        meta = await fetch_metadata(art_type, art_id)
    except Exception as e:
        await get_tracker().track("metadata_resolve", {"ip": ip, "artwork_id": "", "success": False, "error": str(e)})
        raise HTTPException(status_code=502, detail=f"上游 API 错误: {e}")

    await get_tracker().track("metadata_resolve", {
        "ip": ip, "artwork_id": art_id, "artwork_name": meta.name, "success": True,
    })

    filename = f"{meta.author}_{meta.name}"
    return {
        "name": meta.name,
        "author": meta.author,
        "filename": filename,
        "layout_type": meta.layout_type,
        "page_count": len(meta.pieces) if meta.layout_type == "PAGE" else 1,
        "age": meta.age,
        "age_detail": meta.age_detail,
        "desc": meta.desc,
        "owner": meta.owner,
        "size_cm": meta.size_cm,
        "width": meta.width,
        "height": meta.height,
        "thumb_url": meta.thumb_url,
        "tags": meta.tags,
        "levels": meta.available_levels,
    }


@app.post("/api/download", response_model=TaskResponse)
async def start_download(req: DownloadRequest, request: Request):
    ip = _get_client_ip(request)
    limiter = get_limiter()

    rate_result = await limiter.check(f"dl:{ip}", settings.rate_limit_download_per_min, 60)
    if not rate_result.allowed:
        raise HTTPException(status_code=429, detail=f"请求过于频繁，请 {rate_result.retry_after:.0f} 秒后再试")

    daily_result = await limiter.check(f"daily_dl:{ip}", settings.daily_download_standard, 86400)
    if not daily_result.allowed:
        raise HTTPException(status_code=429, detail="今日免费下载额度已用完，明日 0 点重置")

    try:
        art_type, art_id = parse_url(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        meta = await fetch_metadata(art_type, art_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"上游 API 错误: {e}")

    if req.level < meta.min_level or req.level > meta.max_level:
        raise HTTPException(status_code=400, detail="无效的缩放级别")

    is_hd = req.level >= meta.max_level
    if is_hd:
        hd_result = await limiter.check(f"daily_hd:{ip}", settings.daily_download_hd, 86400)
        if not hd_result.allowed:
            raise HTTPException(status_code=429, detail="今日高清下载额度已用完，请选择较低分辨率或明日再试")

    task_id = uuid.uuid4().hex[:12]
    progress = DownloadProgress()
    _tasks[task_id] = {
        "progress": progress,
        "meta": meta,
        "result": None,
    }

    dl_start_time = time.time()
    await get_tracker().track("download_start", {
        "ip": ip, "artwork_id": art_id, "level": req.level,
        "resolution": f"{meta.width}x{meta.height}", "is_hd": is_hd,
    })

    async def _run():
        try:
            buf = await download_and_stitch(meta, req.level, progress)
            _tasks[task_id]["result"] = buf
            await get_tracker().track("download_complete", {
                "ip": ip, "artwork_id": art_id,
                "duration_sec": round(time.time() - dl_start_time, 1),
            })
        except Exception as e:
            progress.status = "error"
            progress.message = str(e)
            await get_tracker().track("download_error", {
                "ip": ip, "artwork_id": art_id, "error_message": str(e),
            })

    asyncio.create_task(_run())
    return TaskResponse(task_id=task_id)


@app.get("/api/quota")
async def get_quota(request: Request):
    """查询当前 IP 剩余下载额度。"""
    ip = _get_client_ip(request)
    limiter = get_limiter()
    std_remaining = await limiter.get_remaining(f"daily_dl:{ip}", settings.daily_download_standard, 86400)
    hd_remaining = await limiter.get_remaining(f"daily_hd:{ip}", settings.daily_download_hd, 86400)
    return {"standard_remaining": std_remaining, "hd_remaining": hd_remaining}


@app.get("/api/progress/{task_id}", response_model=ProgressResponse)
async def get_progress(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    p = task["progress"]
    meta: ArtworkMeta = task["meta"]
    return ProgressResponse(
        total=p.total,
        done=p.done,
        status=p.status,
        message=p.message,
        filename=f"{meta.author}_{meta.name}",
    )


@app.get("/api/result/{task_id}")
async def get_result(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task["progress"].status != "done":
        raise HTTPException(status_code=409, detail="任务尚未完成")
    buf = task["result"]
    if not buf:
        raise HTTPException(status_code=500, detail="结果为空")

    meta: ArtworkMeta = task["meta"]
    buf.seek(0)

    if meta.layout_type == "PAGE":
        filename = f"{meta.author}_{meta.name}.zip"
        encoded = quote(filename)
        return StreamingResponse(
            buf,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
        )

    filename = f"{meta.author}_{meta.name}.jpg"
    encoded = quote(filename)
    return StreamingResponse(
        buf,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )
