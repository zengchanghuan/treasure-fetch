<template>
  <footer>
    <div class="footer-trust">
      <div class="trust-item"><span class="ti-icon">🔒</span><span>不存储任何用户数据</span></div>
      <div class="trust-item"><span class="ti-icon">🚫</span><span>本站不存储任何图片</span></div>
      <div class="trust-item"><span class="ti-icon">🖼️</span><span>优先整理作品资料与馆藏信息</span></div>
      <div class="trust-item"><span class="ti-icon">🌐</span><span>服务器部署于 AWS 新加坡</span></div>
      <div class="trust-item"><span class="ti-icon">📖</span><span>仅供个人学习研究使用</span></div>
    </div>
    <div class="footer-divider" />

    <!-- 显著免责声明 -->
    <div class="legal-notice">
      <p class="legal-title">⚠️ 免责声明</p>
      <p>本工具仅供个人学习研究使用，不得用于商业用途。用户需自行承担内容使用的法律责任。</p>
      <p>当前版本聚焦台北故宫博物院公开馆藏页面，提供资料整理与研究辅助。作品内容及相关权利归原机构或权利人所有；如需进一步使用，请以馆方规则与正式授权要求为准。</p>
    </div>

    <!-- FixEpub 导流 -->
    <div class="sister-tool">
      爱读书？试试我的另一个工具 👉
      <a href="https://fixepub.com" target="_blank" rel="noopener">FixEpub.com</a>
      — AI 电子书翻译与排版引擎
    </div>

    <div class="footer-divider" />
    <div class="footer-disclaimer">
      <p class="copyright">&copy; 2026 Yizhou Art &nbsp;·&nbsp; All rights reserved.</p>
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
.legal-notice {
  max-width: 640px; margin: 0 auto 16px;
  padding: 14px 18px;
  background: rgba(201, 169, 110, 0.06);
  border: 1px solid rgba(201, 169, 110, 0.2);
  border-radius: 10px;
  text-align: center;
  line-height: 1.8;
  font-size: .8rem;
  color: var(--text2);
}
.legal-title {
  font-weight: 600;
  color: var(--accent);
  margin-bottom: 6px;
  font-size: .85rem;
}
.legal-notice p { margin: 0; }
.legal-notice p + p { margin-top: 6px; }
.footer-disclaimer { text-align: center; line-height: 1.8; opacity: .55; }
.footer-disclaimer a { color: var(--accent); text-decoration: none; }
.footer-disclaimer a:hover { text-decoration: underline; }
.copyright { margin-top: 0; font-size: .75rem; }
.sister-tool {
  text-align: center;
  font-size: .8rem;
  color: var(--text2);
  margin-bottom: 14px;
  line-height: 1.8;
}
.sister-tool a {
  color: var(--accent);
  font-weight: 600;
  text-decoration: none;
}
.sister-tool a:hover { text-decoration: underline; }
</style>
