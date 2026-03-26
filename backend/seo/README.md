# SEO 模块

为每件作品生成搜索引擎友好的详情页，提升长尾搜索流量。

## 路由

| 路径 | 说明 |
|---|---|
| `GET /artwork/{artwork_id}` | 服务端渲染作品详情页 (SSR) |
| `GET /sitemap.xml` | 动态 sitemap |
| `GET /robots.txt` | 爬虫规则 |

## 作品详情页特性

- `<title>` / `<meta description>` 包含作者、作品名、朝代、收藏机构
- JSON-LD `VisualArtwork` 结构化数据（Google 富媒体搜索结果）
- Open Graph + Twitter Card meta（社交平台分享预览）
- 24 小时 HTTP 缓存
- CTA 按钮跳转首页并自动填入链接

## 种子作品列表

`seed_artworks.json` 维护初始热门作品 ID 列表，用于 sitemap 生成。
手动添加新条目即可扩展：

```json
[
  {"id": "647a19401977e748e6a9bfbe", "name": "行书詹同松磵亭轴", "author": "黄宾虹"}
]
```

## 挂载方式

```python
from backend.seo import seo_router
app.include_router(seo_router)
```

## 首页联动

首页支持 `?url=xxx` 参数自动填入输入框并触发解析：
`https://treasure.moyun.art/?url=https://g2.ltfc.net/view/SUHA/647a19401977e748e6a9bfbe`
