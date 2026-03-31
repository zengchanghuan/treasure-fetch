<template>
  <div v-if="visible" class="empty-state">
    <div class="empty-icon">🖼️</div>
    <p>
      粘贴书画作品的页面链接，即可一键保存完整高清原图<br>
      <span class="hint">在数字文博平台找到喜欢的作品，复制浏览器地址栏链接粘贴到这里</span>
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
