"""
FastAPI 应用入口。

路由：
  GET  /                     → 前端页面
  POST /api/metadata         → 根据 URL 获取作品元数据
  POST /api/download         → 发起下载任务
  GET  /api/progress/{task}  → 轮询下载进度
  GET  /api/result/{task}    → 获取最终图片
"""

from __future__ import annotations

import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .tile_service import (
    ArtworkMeta,
    DownloadProgress,
    download_and_stitch,
    fetch_metadata,
    parse_url,
)

app = FastAPI(title="Treasure Fetch — 高清书画下载服务")

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


@app.post("/api/metadata")
async def get_metadata(req: MetadataRequest):
    try:
        art_type, art_id = parse_url(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        meta = await fetch_metadata(art_type, art_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"上游 API 错误: {e}")

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
async def start_download(req: DownloadRequest):
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

    task_id = uuid.uuid4().hex[:12]
    progress = DownloadProgress()
    _tasks[task_id] = {
        "progress": progress,
        "meta": meta,
        "result": None,
    }

    import asyncio

    async def _run():
        try:
            buf = await download_and_stitch(meta, req.level, progress)
            _tasks[task_id]["result"] = buf
        except Exception as e:
            progress.status = "error"
            progress.message = str(e)

    asyncio.create_task(_run())
    return TaskResponse(task_id=task_id)


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
