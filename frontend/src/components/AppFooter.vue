<template>
  <footer>
    <div class="footer-trust">
      <div class="trust-item"><span class="ti-icon">🔒</span><span>不存储任何用户数据</span></div>
      <div class="trust-item"><span class="ti-icon">🖼️</span><span>图片直接推送至您的设备</span></div>
      <div class="trust-item"><span class="ti-icon">🌐</span><span>服务器部署于 AWS 新加坡</span></div>
      <div class="trust-item"><span class="ti-icon">📖</span><span>开源免费，仅供学习使用</span></div>
    </div>
    <div class="footer-divider" />
    <div class="footer-disclaimer">
      <p>本工具为非营利性学习工具，所下载内容版权归原博物馆及收藏机构所有，请勿用于商业用途。</p>
      <p class="copyright">&copy; 2026 Moyun Art &nbsp;·&nbsp; All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
footer {
  margin-top: auto; border-top: 1px solid var(--border);
  padding: 28px 24px 32px; font-size: .78rem; color: var(--text2); width: 100%;
}
.footer-trust { display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin-bottom: 16px; }
.trust-item { display: flex; align-items: center; gap: 6px; font-size: .82rem; opacity: .85; }
.ti-icon { font-size: 1rem; }
.footer-divider { width: 40px; height: 1px; background: var(--border); margin: 0 auto 14px; }
.footer-disclaimer { text-align: center; line-height: 1.8; opacity: .65; }
.footer-disclaimer a { color: var(--accent); text-decoration: none; }
.footer-disclaimer a:hover { text-decoration: underline; }
.copyright { margin-top: 6px; }
</style>
