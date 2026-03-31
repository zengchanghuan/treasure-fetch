<template>
  <header>
    <div class="brand">
      <h1>一 轴</h1>
      <span class="brand-en">Yizhou</span>
    </div>
    <p>高清书画瓦片图 · 一键还原下载</p>
  </header>
</template>

<style scoped>
header {
  width: 100%; padding: 32px 0 16px; text-align: center;
  border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: baseline; justify-content: center; gap: 12px; }
header h1 { font-size: 1.6rem; font-weight: 500; letter-spacing: 6px; color: var(--accent); }
.brand-en { font-size: .8rem; color: var(--accent-dim); letter-spacing: 2px; font-weight: 400; opacity: .8; }
header p { color: var(--text2); font-size: .85rem; margin-top: 6px; }
</style>
