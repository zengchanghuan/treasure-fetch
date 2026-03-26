<template>
  <div v-if="visible" class="empty-state">
    <div class="empty-icon">🖼️</div>
    <p>
      粘贴一条 g2.ltfc.net 的书画作品链接，即可解析并下载高清原图<br>
      <span class="hint">链接格式：g2.ltfc.net/view/SUHA/…</span>
    </p>
  </div>
</template>

<script setup>
defineProps({ visible: Boolean })
</script>

<style scoped>
.empty-state {
  margin-top: 32px; text-align: center; color: var(--text2);
  padding: 32px 16px; border: 1px dashed var(--border); border-radius: var(--radius);
}
.empty-icon { font-size: 2.2rem; margin-bottom: 12px; }
.empty-state p { font-size: .88rem; line-height: 1.8; margin: 0; }
.hint { font-size: .8rem; opacity: .65; }
</style>
