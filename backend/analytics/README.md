# Analytics 埋点模块

轻量级异步事件追踪，默认基于 SQLite 存储。

## 接口

```python
class EventTracker(Protocol):
    async def track(self, event: str, properties: dict | None = None) -> None
    async def query(self, event: str | None, start, end, limit=500) -> list[dict]
    async def count(self, event: str | None, start, end) -> int
    async def top(self, event: str, field: str, start, end, limit=20) -> list[dict]
    async def daily_series(self, event: str | None, start, end) -> list[dict]
```

## 快速使用

```python
from backend.analytics import get_tracker

tracker = get_tracker()
await tracker.track("download_start", {"ip": "1.2.3.4", "artwork_id": "abc123"})
```

## 替换存储后端

实现 `EventTracker` Protocol 即可，无需继承。例如替换为 PostgreSQL：

```python
class PgTracker:
    async def track(self, event, properties=None): ...
    # ... 其余方法
```

## 事件类型约定

| 事件 | 属性 |
|---|---|
| `page_view` | ip, user_agent, referer |
| `metadata_resolve` | ip, artwork_id, artwork_name, success |
| `download_start` | ip, artwork_id, level, resolution |
| `download_complete` | ip, artwork_id, file_size_mb, duration_sec |
| `download_error` | ip, artwork_id, error_message |
