<template>
  <div v-if="visible" class="empty-state">
    <div class="empty-icon">🖼️</div>
    <p>
      粘贴台北故宫博物院公开馆藏页面链接，即可查看作品资料与研究信息<br>
      <span class="hint">支持作者、年代、尺寸、馆藏与简介等信息整理</span>
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
