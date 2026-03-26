# Admin 管理后台模块

轻量级数据看板，HTTP Basic Auth 保护。

## 路由

| 路径 | 说明 |
|---|---|
| `GET /admin` | 仪表盘 HTML 页面 |
| `GET /admin/api/summary?days=7` | 汇总指标 |
| `GET /admin/api/daily?days=30&event=page_view` | 每日趋势 |
| `GET /admin/api/top_artworks?days=7` | 热门作品 Top 20 |
| `GET /admin/api/level_distribution?days=7` | 分辨率分布 |

## 配置

通过环境变量或 `.env` 设置管理员密码：

```
ADMIN_PASSWORD=your_secure_password
```

默认用户名固定为 `admin`。

## 挂载方式

```python
from backend.admin import admin_router
app.include_router(admin_router, prefix="/admin")
```

## 数据来源

所有数据从 `backend.analytics` 模块读取，不直接操作数据库。
