# Rate Limiter 限流模块

滑动窗口限流器，支持分钟级和日级额度控制。

## 接口

```python
class RateLimiter(Protocol):
    async def check(self, key: str, limit: int, window_sec: int) -> RateLimitResult
    async def get_remaining(self, key: str, limit: int, window_sec: int) -> int
```

`RateLimitResult` 包含：
- `allowed: bool` — 是否放行
- `remaining: int` — 窗口内剩余次数
- `retry_after: float` — 若被拒，建议等待秒数

## 实现

| 实现 | 场景 |
|---|---|
| `MemoryLimiter` | 进程内 dict，开发/单机，重启后重置 |
| `SQLiteLimiter` | 持久化，重启不丢失，适合生产单机 |

## 用法示例

```python
from backend.rate_limiter import get_limiter

limiter = get_limiter()

# 每分钟限 5 次
result = await limiter.check("dl:1.2.3.4", limit=5, window_sec=60)

# 每日限 10 次
result = await limiter.check("daily_dl:1.2.3.4", limit=10, window_sec=86400)

# 查询剩余次数
remaining = await limiter.get_remaining("daily_dl:1.2.3.4", limit=10, window_sec=86400)
```

## 切换为 SQLiteLimiter

修改 `__init__.py` 中的 `get_limiter()`，改为返回 `SQLiteLimiter(db_path)`。
