<template>
  <div class="how-to-section">
    <h3>三步查看作品资料</h3>
    <ol>
      <li>在台北故宫博物院公开馆藏页面找到感兴趣的书画作品，<strong>点击进入作品详情页</strong></li>
      <li><strong>复制浏览器地址栏中的完整链接</strong></li>
      <li>粘贴到上方输入框，<strong>即可查看作者、尺寸、馆藏与作品简介等资料</strong></li>
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
