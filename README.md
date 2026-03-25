# Treasure Fetch — 高清书画下载器

将深度缩放瓦片图 (Deep Zoom Tiles) 还原为完整高清图片，提供 Web UI 一键操作。

支持三种布局：单图（PIC）、拼合（COLL）、多页（PAGE → ZIP 打包）。

## 架构

```
┌──────────────────────────────────────────────────┐
│  Browser (前端)                                   │
│  URL 输入 → 元数据展示 → 分辨率选择 → 进度轮询     │
└──────┬───────────────────────────────────────────┘
       │ REST API
┌──────▼───────────────────────────────────────────┐
│  FastAPI (后端)                                    │
│  /api/metadata → /api/download → /api/progress    │
│  tile_service.py: CDN 签名 · 并发下载 · Pillow 拼接 │
└──────┬───────────────────────────────────────────┘
       │ HTTPS
┌──────▼───────────────────────────────────────────┐
│  Upstream CDN / API                               │
│  api.quanku.art + cag-ac.ltfc.net                 │
└──────────────────────────────────────────────────┘
```

## 快速启动

```bash
# 1. 克隆仓库
git clone git@github.com:zengchanghuan/treasure-fetch.git
cd treasure-fetch

# 2. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
uvicorn backend.app:app --reload --port 8899

# 5. 打开浏览器
open http://localhost:8899
```

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/metadata` | 解析 URL，返回作品元数据与可选分辨率 |
| POST | `/api/download` | 创建下载任务，返回 `task_id` |
| GET  | `/api/progress/{task_id}` | 轮询任务进度 |
| GET  | `/api/result/{task_id}` | 下载最终图片（JPEG 或 ZIP） |

## 工程边界

- **失败处理**：HTTP 请求均设超时；图块下载 12 路并发，单块 404 静默跳过不阻塞全局。
- **可观测性**：`DownloadProgress` 数据结构实时暴露状态，前端每 500ms 轮询。
- **可替换性**：核心逻辑 `tile_service.py` 不依赖 FastAPI，可独立调用或接入其他框架。
- **成本控制**：按需选择分辨率等级，避免不必要的高 Level 下载（图块数量指数增长）。
- **当前局限**：任务池存内存，进程重启即丢失。生产环境可替换为 Redis + Celery。

## License

MIT
