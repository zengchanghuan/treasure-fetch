<template>
  <div v-if="status" class="progress-bar">
    <div class="progress-track">
      <div class="progress-fill" :class="{ 'done-fill': status === 'done' }" :style="{ width: pct + '%' }" />
    </div>
    <div class="progress-text">
      <span>{{ label }}</span>
      <span>{{ pct }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  status: String,
  done: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  message: { type: String, default: '' },
})

const pct = computed(() => {
  if (props.status === 'done') return 100
  if (props.status === 'stitching') return 96
  if (!props.total) return 0
  return Math.min(Math.round((props.done / props.total) * 100), 95)
})

const label = computed(() => {
  if (props.status === 'downloading') return `下载中 ${props.done}/${props.total} (请耐心等待，勿关闭页面)`
  if (props.status === 'stitching') return '图块下载完成，正在合成最终高清大图...'
  if (props.status === 'done') return props.message || '完成'
  return '准备中...'
})
</script>

<style scoped>
.progress-bar { margin-top: 20px; }
.progress-track { width: 100%; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }
.progress-fill {
  height: 100%; width: 0%;
  background: linear-gradient(90deg, var(--accent-dim), var(--accent));
  border-radius: 3px; transition: width .3s ease;
}
.progress-fill.done-fill { background: var(--green); }
.progress-text {
  font-size: .8rem; color: var(--text2); margin-top: 6px;
  display: flex; justify-content: space-between;
}
</style>
