<template>
  <section id="changelog" class="changelog-section">
    <h2>更新记录</h2>
    <div class="timeline">
      <div v-for="entry in entries" :key="entry.date" class="entry">
        <div class="entry-date">{{ entry.date }}</div>
        <div class="entry-body">
          <div class="entry-version">{{ entry.version }}</div>
          <ul>
            <li v-for="item in entry.items" :key="item" v-html="item" />
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const entries = [
  {
    date: '2026-03-26',
    version: 'v0.5 — 商业化基础 & SPA 重构',
    items: [
      '前端迁移至 <strong>Vue 3 + Vite</strong>，拆分 12 个组件，首屏 Gzip 仅 36 KB',
      '新增 <strong>工具套餐定价</strong>：免费版 / Pro 版分层，收费点改为"工具使用次数"',
      '接入 <strong>Cloudflare CDN</strong>，大陆访问延迟从 ~200ms 降至 ~50ms',
      '扩充种子作品库至 <strong>25 件</strong>（齐白石、吴昌硕、张大千、弘一等）',
      '新增显著免责声明：本站不存储任何图片，仅提供技术还原工具',
    ],
  },
  {
    date: '2026-03-25',
    version: 'v0.4 — 管理后台 & SEO',
    items: [
      '自定义管理登录页，Cookie 会话 + HMAC 签名，替换 HTTP Basic Auth',
      '新增 <strong>SEO 详情页</strong>（/artwork/:id），含 JSON-LD 结构化数据',
      '动态 sitemap.xml 与 robots.txt',
      '前端埋点（sendBeacon）+ 管理后台数据看板（Chart.js）',
      '限流模块：内存滑窗 + SQLite 持久化，支持每日下载额度',
    ],
  },
  {
    date: '2026-03-25',
    version: 'v0.3 — 用户体验优化',
    items: [
      '逆向工程上游 API 认证（tourToken + appKey/appSec），解析成功率 100%',
      '新增微信内置浏览器检测横幅，引导跳出到系统浏览器',
      '友好错误提示（替换技术报错）',
      '首屏加载遮罩、Demo 示例链接、移动端触摸热区优化',
    ],
  },
  {
    date: '2026-03-25',
    version: 'v0.2 — 部署上线',
    items: [
      '部署至 AWS 新加坡，域名 moyun.art，HTTPS 证书自动续期',
      'GitHub Actions Push-to-Deploy，推送即部署',
      '支持 COLL / PAGE / PIC 三种布局类型，多页册页打包 ZIP',
    ],
  },
  {
    date: '2026-03-24',
    version: 'v0.1 — 首次发布',
    items: [
      '核心功能上线：瓦片图解析 → 并发下载 → 无损拼接',
      '单页前端，FastAPI 后端，Pillow 图片处理',
    ],
  },
]
</script>

<style scoped>
.changelog-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}
.changelog-section h2 {
  font-size: 1.1rem; color: var(--accent);
  margin-bottom: 24px; font-weight: 500;
}
.timeline { position: relative; padding-left: 20px; }
.timeline::before {
  content: '';
  position: absolute; left: 5px; top: 6px; bottom: 6px;
  width: 1px; background: var(--border);
}
.entry { position: relative; margin-bottom: 28px; }
.entry::before {
  content: '';
  position: absolute; left: -18px; top: 5px;
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent-dim);
  border: 1px solid var(--accent);
}
.entry-date {
  font-size: .75rem; color: var(--text2); margin-bottom: 4px;
}
.entry-version {
  font-size: .88rem; font-weight: 600; color: var(--text);
  margin-bottom: 8px;
}
.entry-body ul {
  list-style: none;
  padding: 0;
}
.entry-body ul li {
  font-size: .82rem; color: var(--text2); line-height: 1.7;
  padding: 3px 0 3px 14px;
  position: relative;
}
.entry-body ul li::before {
  content: '·';
  position: absolute; left: 4px;
  color: var(--accent-dim);
}
.entry-body ul li :deep(strong) { color: var(--text); }
</style>
