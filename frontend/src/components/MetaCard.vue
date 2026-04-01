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
      <div v-if="officialUrl" class="official-link-wrap">
        <a :href="officialUrl" class="official-link" target="_blank" rel="noopener">查看馆藏原页面</a>
        <span class="official-hint">如需进一步使用，请以馆方页面说明与规则为准</span>
      </div>

      <label for="levelSelect">选择研究副本尺寸</label>
      <select id="levelSelect" v-model="selectedLevel" class="level-select">
        <option v-for="lv in (meta.levels || [])" :key="lv.level" :value="lv.level">
          {{ formatLevel(lv) }}
        </option>
      </select>

      <div class="download-actions">
        <button class="btn" :disabled="downloading" @click="$emit('download', selectedLevel)">
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
import { ref, computed, watch } from 'vue'
import DownloadProgress from './DownloadProgress.vue'

const props = defineProps({
  meta: Object,
  officialUrl: { type: String, default: '' },
  downloading: Boolean,
  isDone: Boolean,
  statusText: { type: String, default: '' },
  progress: { type: Object, default: () => ({ status: '', done: 0, total: 0, message: '' }) },
})
defineEmits(['download'])

const selectedLevel = ref(null)

watch(() => props.meta, (m) => {
  if (m?.levels?.length) selectedLevel.value = m.levels[m.levels.length - 1].level
}, { immediate: true })

const pixelLabel = computed(() => {
  if (!props.meta) return ''
  const m = props.meta
  return m.layout_type === 'PAGE'
    ? `${m.width} × ${m.height}（最大页，共 ${m.page_count} 页）`
    : `${m.width} × ${m.height}`
})

const downloadBtnText = computed(() => {
  if (props.downloading) return '处理中...'
  if (props.meta?.layout_type === 'PAGE') return `导出研究副本（${props.meta.page_count} 页 ZIP）`
  return '导出研究副本'
})

function formatLevel(lv) {
  const levels = props.meta?.levels || []
  const maxLevel = levels.length ? levels[levels.length - 1].level : lv.level
  const diff = maxLevel - lv.level
  const megapx = Math.round(lv.width * lv.height / 1e6)
  const label = diff === 0 ? '完整尺寸'
    : diff === 1 ? '较高尺寸'
    : diff === 2 ? '标准尺寸'
    : '预览'
  return `${label}  ${lv.width}×${lv.height}${megapx >= 1 ? '（约 ' + megapx + ' 百万像素）' : ''}`
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
.official-link-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}
.official-link {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  justify-content: center;
  padding: 9px 14px;
  background: rgba(201,169,110,.1);
  border: 1px solid rgba(201,169,110,.28);
  border-radius: 8px;
  color: var(--accent);
  text-decoration: none;
  font-size: .84rem;
}
.official-link:hover { text-decoration: underline; }
.official-hint { font-size: .78rem; color: var(--text2); }
.download-section label { display: block; font-size: .85rem; color: var(--text2); margin-bottom: 8px; }
.level-select {
  width: 100%; padding: 10px 14px; background: var(--bg);
  border: 1px solid var(--border); border-radius: 8px;
  color: var(--text); font-size: .9rem; outline: none; appearance: none; cursor: pointer;
}
.download-actions { margin-top: 16px; display: flex; gap: 10px; align-items: center; }
.dl-status { font-size: .85rem; color: var(--text2); }
@media (max-width: 520px) {
  .meta-header { flex-direction: column; align-items: center; text-align: center; }
  .meta-thumb { width: 80px; min-height: 100px; }
}
</style>
