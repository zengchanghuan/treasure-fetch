<template>
  <Transition name="fade">
    <div v-if="visible" class="loader">
      <div class="loader-title">一 轴</div>
      <div class="loader-dots"><span /><span /><span /></div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
const visible = ref(true)
onMounted(() => setTimeout(() => (visible.value = false), 600))
</script>

<style scoped>
.loader {
  position: fixed; inset: 0; background: var(--bg);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20px;
  z-index: 9999;
}
.loader-title {
  font-size: 1.4rem; letter-spacing: 6px; color: var(--accent);
  font-weight: 400; animation: pulse 2s ease-in-out infinite;
}
.loader-dots { display: flex; gap: 8px; }
.loader-dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--accent-dim);
  animation: bounce 1.2s ease-in-out infinite;
}
.loader-dots span:nth-child(2) { animation-delay: .2s; }
.loader-dots span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: .4; }
  40% { transform: translateY(-8px); opacity: 1; }
}
@keyframes pulse { 0%, 100% { opacity: .7; } 50% { opacity: 1; } }
.fade-leave-active { transition: opacity .4s ease; }
.fade-leave-to { opacity: 0; }
</style>
