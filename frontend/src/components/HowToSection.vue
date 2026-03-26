<template>
  <div class="how-to-section">
    <h3>如何获取画作链接？</h3>
    <ol>
      <li>访问 <strong><a href="https://g2.ltfc.net" target="_blank">g2.ltfc.net</a></strong></li>
      <li>搜索或浏览你感兴趣的书画作品，<strong>点击进入高清浏览页面</strong></li>
      <li><strong>复制浏览器地址栏中的完整链接</strong>（格式形如 <code>g2.ltfc.net/view/SUHA/...</code>）</li>
      <li>回到本页面，粘贴链接并点击「解析」</li>
    </ol>
  </div>
</template>

<style scoped>
.how-to-section {
  margin-top: 36px; background: var(--card);
  border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px;
}
.how-to-section h3 { font-size: .95rem; color: var(--accent); margin-bottom: 14px; font-weight: 500; }
.how-to-section ol { color: var(--text2); font-size: .85rem; line-height: 2; padding-left: 20px; }
.how-to-section ol li strong { color: var(--text); }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code { color: var(--accent); background: var(--border); padding: 2px 6px; border-radius: 4px; }
</style>
