<template>
  <div v-if="meta" class="card" :class="{ done: isDone }">
    <div class="meta-header">
      <div class="meta-thumb">
        <img :src="meta.thumb_url || ''" alt="缩略图" />
      </div>
      <div class="meta-info">
        <h2>{{ meta.name }}</h2>
        <div class="detail">
          <div>作者：<span>{{ meta.author }}</span></div>
          <div>年代：<span>{{ meta.age_detail || meta.age }}</span></div>
          <div>尺寸：<span>{{ meta.size_cm ? `${meta.size_cm} cm` : '—' }}</span></div>
          <div>收藏：<span>{{ meta.owner || '—' }}</span></div>
          <div>像素：<span>{{ pixelLabel }}</span></div>
        </div>
        <div class="tags">
          <span v-for="t in (meta.tags || [])" :key="t" class="tag">{{ t }}</span>
        </div>
      </div>
    </div>

    <p v-if="meta.desc" class="desc-text">{{ meta.desc }}</p>

    <div class="download-section">
      <label for="levelSelect">选择图片尺寸</label>
      <select id="levelSelect" v-model="selectedLevel" class="level-select">
        <option
          v-for="lv in (meta.levels || [])"
          :key="lv.level"
          :value="lv.level"
          :disabled="isHdLevel(lv.level) && quota && quota.hd_remaining <= 0"
        >
          {{ formatLevel(lv) }}{{ isHdLevel(lv.level) ? '  · Pro' : '' }}
        </option>
      </select>

      <!-- 工具使用额度 -->
      <div v-if="quota" class="quota-bar">
        <div class="quota-item">
          <span class="quota-label">今日还原次数</span>
          <span class="quota-value" :class="{ warn: quota.standard_remaining <= 1 }">
            剩余 {{ quota.standard_remaining }} 次
          </span>
        </div>
        <div class="quota-item quota-hd">
          <span class="quota-label">高清额度 <span class="pro-tag">Pro</span></span>
          <span class="quota-value" :class="{ warn: quota.hd_remaining <= 0 }">
            剩余 {{ quota.hd_remaining }} 次
          </span>
        </div>
      </div>

      <!-- 高清限制提示 -->
      <div v-if="isHdLevel(selectedLevel) && quota && quota.hd_remaining <= 0" class="upgrade-hint">
        高清还原需要 Pro 套餐，或选择较低分辨率继续使用
        <a href="#pricing" class="upgrade-link">查看套餐 →</a>
      </div>

      <div class="download-actions">
        <button class="btn" :disabled="downloading || (isHdLevel(selectedLevel) && quota && quota.hd_remaining <= 0)" @click="$emit('download', selectedLevel)">
          {{ downloadBtnText }}
        </button>
        <span class="dl-status">{{ statusText }}</span>
      </div>
    </div>

    <DownloadProgress
      :status="progress.status"
      :done="progress.done"
      :total="progress.total"
      :message="progress.message"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { fetchQuota as apiFetchQuota } from '../api.js'
import DownloadProgress from './DownloadProgress.vue'

const props = defineProps({
  meta: Object,
  downloading: Boolean,
  isDone: Boolean,
  statusText: { type: String, default: '' },
  progress: { type: Object, default: () => ({ status: '', done: 0, total: 0, message: '' }) },
})
defineEmits(['download'])

const selectedLevel = ref(null)
const quota = ref(null)

watch(() => props.meta, (m) => {
  if (m?.levels?.length) selectedLevel.value = m.levels[m.levels.length - 1].level
  loadQuota()
}, { immediate: true })

const pixelLabel = computed(() => {
  if (!props.meta) return ''
  const m = props.meta
  return m.layout_type === 'PAGE'
    ? `${m.width} × ${m.height}（最大页，共 ${m.page_count} 页）`
    : `${m.width} × ${m.height}`
})

const downloadBtnText = computed(() => {
  if (props.downloading) return '还原中...'
  if (props.meta?.layout_type === 'PAGE') return `还原全部（${props.meta.page_count} 页 ZIP）`
  return '开始还原'
})

function isHdLevel(level) {
  if (!props.meta?.levels?.length) return false
  const maxLevel = props.meta.levels[props.meta.levels.length - 1].level
  return level >= maxLevel - 1
}

function formatLevel(lv) {
  const levels = props.meta?.levels || []
  const maxLevel = levels.length ? levels[levels.length - 1].level : lv.level
  const diff = maxLevel - lv.level
  const megapx = Math.round(lv.width * lv.height / 1e6)
  const label = diff === 0 ? '最高清（原始尺寸）'
    : diff === 1 ? '高清'
    : diff === 2 ? '标清'
    : '预览'
  return `${label}  ${lv.width}×${lv.height}${megapx >= 1 ? '（约 ' + megapx + ' 百万像素）' : ''}`
}

async function loadQuota() {
  try { quota.value = await apiFetchQuota() } catch { /* noop */ }
}
</script>

<style scoped>
.card {
  margin-top: 24px; background: var(--card);
  border: 1px solid var(--border); border-radius: var(--radius); padding: 24px;
}
.card.done { border-color: var(--green); }
.meta-header { display: flex; gap: 20px; margin-bottom: 20px; }
.meta-thumb {
  width: 120px; min-height: 160px; border-radius: 8px;
  overflow: hidden; background: var(--border); flex-shrink: 0;
}
.meta-thumb img { width: 100%; height: auto; display: block; }
.meta-info h2 { font-size: 1.2rem; font-weight: 500; color: var(--accent); margin-bottom: 8px; }
.detail { font-size: .85rem; color: var(--text2); line-height: 1.7; }
.tags { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
.tag { padding: 2px 10px; background: var(--border); border-radius: 20px; font-size: .75rem; color: var(--text2); }
.desc-text {
  margin-top: 12px; font-size: .82rem; color: var(--text2); line-height: 1.8;
  border-top: 1px solid var(--border); padding-top: 12px;
}
.download-section { margin-top: 20px; }
.download-section label { display: block; font-size: .85rem; color: var(--text2); margin-bottom: 8px; }
.level-select {
  width: 100%; padding: 10px 14px; background: var(--bg);
  border: 1px solid var(--border); border-radius: 8px;
  color: var(--text); font-size: .9rem; outline: none; appearance: none; cursor: pointer;
}
.quota-bar {
  display: flex; gap: 12px; margin: 10px 0 6px;
  padding: 10px 14px;
  background: rgba(255,255,255,.03);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.quota-item { display: flex; flex-direction: column; gap: 3px; flex: 1; }
.quota-hd { border-left: 1px solid var(--border); padding-left: 12px; }
.quota-label { font-size: .72rem; color: var(--text2); display: flex; align-items: center; gap: 5px; }
.quota-value { font-size: .82rem; color: var(--text); font-weight: 500; }
.quota-value.warn { color: var(--danger); }
.pro-tag {
  font-size: .65rem; background: rgba(201,169,110,.2);
  color: var(--accent); padding: 1px 5px; border-radius: 4px;
  font-weight: 600; letter-spacing: .5px;
}
.upgrade-hint {
  font-size: .78rem; color: var(--text2);
  background: rgba(201,169,110,.06);
  border: 1px solid rgba(201,169,110,.2);
  border-radius: 8px; padding: 8px 12px; margin: 6px 0;
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.upgrade-link {
  color: var(--accent); text-decoration: none; white-space: nowrap; font-size: .78rem;
}
.upgrade-link:hover { text-decoration: underline; }
.download-actions { margin-top: 16px; display: flex; gap: 10px; align-items: center; }
.dl-status { font-size: .85rem; color: var(--text2); }
@media (max-width: 520px) {
  .meta-header { flex-direction: column; align-items: center; text-align: center; }
  .meta-thumb { width: 80px; min-height: 100px; }
}
</style>
