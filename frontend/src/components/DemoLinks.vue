<template>
  <div class="demo-links">
    <span class="demo-label">没有链接？试试台北故宫示例：</span>
    <button class="demo-btn" :disabled="filling" @click="fill">
      {{ filling ? '✓ 已填入，解析中…' : '《行书詹同松磵亭轴》' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { DEMO_URL } from '../api.js'

const emit = defineEmits(['fill'])
const filling = ref(false)

function fill() {
  filling.value = true
  emit('fill', DEMO_URL)
  setTimeout(() => (filling.value = false), 2500)
}
</script>

<style scoped>
.demo-links {
  margin-top: 12px; display: flex; align-items: center; flex-wrap: wrap;
  gap: 8px; font-size: 0.85rem; color: var(--text2);
}
.demo-label { white-space: nowrap; }
.demo-btn {
  padding: 5px 14px; background: transparent; color: var(--accent);
  border: 1px dashed var(--accent); border-radius: 20px; font-size: .82rem;
  cursor: pointer; transition: all .2s; min-height: 36px;
  -webkit-tap-highlight-color: transparent; touch-action: manipulation;
}
.demo-btn:hover { background: rgba(201,169,110,.12); }
.demo-btn:disabled { opacity: .5; cursor: default; }
</style>
