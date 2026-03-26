# 大陆访问速度优化 — Cloudflare CDN 配置指南

## 背景

服务器部署在 AWS 新加坡 (ap-southeast-1)，中国大陆用户直连延迟约 150–300ms。  
接入 Cloudflare CDN 后，静态资源可通过亚太边缘节点分发，首屏加载提速 50%+。

---

## 一、迁移步骤（约 20 分钟）

### 1. 注册 Cloudflare 账号

访问 <https://dash.cloudflare.com/sign-up>，免费版即可。

### 2. 添加域名

在 Dashboard 点击 **Add a site** → 输入 `moyun.art` → 选择 **Free** 方案。

### 3. 修改 DNS 解析

Cloudflare 会列出当前 DNS 记录。确认以下记录已存在（橙色云朵 = 已代理）：

| 类型 | 名称 | 内容 | 代理状态 |
|------|------|------|----------|
| A | `@` | `54.169.182.124` | 已代理 (Proxied) |
| A | `treasure` | `54.169.182.124` | 已代理 (Proxied) |
| A | `www` | `54.169.182.124` | 已代理 (Proxied) |

### 4. 更换域名 NS 服务器

将 **腾讯云 DNS 控制台** 中 `moyun.art` 的 NS 记录改为 Cloudflare 分配的两个 NS。  
操作路径：腾讯云 → 域名注册 → `moyun.art` → 修改 DNS 服务器。

> ⚠️ NS 生效需 10 分钟到 48 小时，Cloudflare 会邮件通知。

### 5. 开启 SSL

进入 Cloudflare Dashboard → **SSL/TLS** → 选择 **Full (strict)**。  
因为服务器已有 Let's Encrypt 证书，使用 strict 模式安全最高。

---

## 二、推荐配置

### 缓存规则 (Caching)

| 路径 | 缓存策略 | 说明 |
|------|----------|------|
| `/assets/*` | Cache Everything, Edge TTL: 30d | Vite 构建的带 hash 静态资源 |
| `/api/*` | Bypass Cache | API 不缓存 |
| `/admin/*` | Bypass Cache | 管理后台不缓存 |
| `/artwork/*` | Cache Everything, Edge TTL: 1d | SEO 详情页缓存 1 天 |
| `/` | Cache Everything, Edge TTL: 4h | 首页适度缓存 |

操作路径：**Rules** → **Page Rules** (免费版 3 条) 或 **Cache Rules** (新版)。

推荐的 3 条 Page Rules：

```
1. *moyun.art/api/*           → Cache Level: Bypass
2. *moyun.art/admin/*         → Cache Level: Bypass
3. *moyun.art/assets/*        → Cache Level: Cache Everything, Edge Cache TTL: 1 month
```

### Speed 优化

1. **Speed** → **Optimization** → 开启：
   - Auto Minify (JS / CSS / HTML)
   - Brotli 压缩
   - Early Hints
   - Rocket Loader（谨慎开启，若 SPA 出问题关掉）

2. **Speed** → **Polish** (Pro 版)：
   - 自动优化图片格式为 WebP / AVIF

### 安全

1. **Security** → **WAF**：开启 Managed Rules
2. **Security** → **Bot Fight Mode**：开启
3. **Security** → **Settings** → Security Level: **Medium**

---

## 三、性能对比预估

| 指标 | 直连 AWS 新加坡 | Cloudflare CDN |
|------|-----------------|----------------|
| TTFB (北京) | ~200ms | ~50ms |
| 首页加载 (4G) | ~2.5s | ~1.2s |
| 静态资源 (JS/CSS) | 每次回源 | 边缘命中 |
| SSL 握手 | 1 次 (新加坡) | 1 次 (就近节点) |

---

## 四、验证

```bash
# 检查 CDN 是否生效（应返回 cf-ray 头）
curl -I https://treasure.moyun.art
# 预期: server: cloudflare, cf-ray: xxxxx

# 测试缓存命中
curl -I https://treasure.moyun.art/assets/index-xxxxx.js
# 预期: cf-cache-status: HIT
```

---

## 五、回滚方案

如果 Cloudflare 出现问题：
1. 腾讯云 DNS 改回原 NS 服务器
2. 或在 Cloudflare 将所有记录切为 **DNS Only**（灰色云朵），流量绕过 CDN
