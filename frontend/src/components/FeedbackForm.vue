<template>
  <section class="feedback-section">
    <h2>意见反馈</h2>
    <p class="feedback-sub">遇到问题？有新想法？告诉我们，每条反馈都会认真阅读。</p>

    <form class="feedback-form" @submit.prevent="submit">
      <textarea
        v-model="text"
        placeholder="描述你的问题或建议，越详细越好…"
        rows="4"
        :disabled="state === 'loading' || state === 'done'"
        maxlength="2000"
      />
      <div class="char-count">{{ text.length }} / 2000</div>

      <!-- 拖拽上传区 -->
      <div
        class="drop-zone"
        :class="{ dragover, 'has-preview': previewUrl }"
        @click="triggerFileInput"
        @dragover.prevent="dragover = true"
        @dragleave="dragover = false"
        @drop.prevent="onDrop"
      >
        <template v-if="previewUrl">
          <img :src="previewUrl" class="preview-img" alt="预览" />
          <button class="remove-img" type="button" @click.stop="removeImage">✕</button>
        </template>
        <template v-else>
          <span class="drop-icon">🖼️</span>
          <span class="drop-text">拖拽图片到此处，或 <u>点击选择</u></span>
          <span class="drop-hint">支持 JPG / PNG / GIF · 最大 5 MB</span>
        </template>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display:none"
        @change="onFileChange"
      />

      <div v-if="errorMsg" class="feedback-error">{{ errorMsg }}</div>

      <button
        class="submit-btn"
        type="submit"
        :disabled="!text.trim() || state === 'loading' || state === 'done'"
      >
        <template v-if="state === 'loading'">提交中…</template>
        <template v-else-if="state === 'done'">✓ 已提交，感谢反馈！</template>
        <template v-else>提交反馈</template>
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'

const text = ref('')
const file = ref(null)
const previewUrl = ref('')
const dragover = ref(false)
const state = ref('idle') // idle | loading | done | error
const errorMsg = ref('')
const fileInput = ref(null)

const MAX_SIZE = 5 * 1024 * 1024

function triggerFileInput() {
  if (previewUrl.value) return
  fileInput.value?.click()
}

function setFile(f) {
  if (!f) return
  if (!f.type.startsWith('image/')) { errorMsg.value = '请选择图片文件'; return }
  if (f.size > MAX_SIZE) { errorMsg.value = '图片不能超过 5 MB'; return }
  errorMsg.value = ''
  file.value = f
  previewUrl.value = URL.createObjectURL(f)
}

function onFileChange(e) { setFile(e.target.files[0]) }
function onDrop(e) {
  dragover.value = false
  setFile(e.dataTransfer.files[0])
}
function removeImage() {
  file.value = null
  previewUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

async function submit() {
  if (!text.value.trim()) return
  errorMsg.value = ''
  state.value = 'loading'

  const fd = new FormData()
  fd.append('text', text.value.trim())
  if (file.value) fd.append('image', file.value)

  try {
    const resp = await fetch('/api/feedback', { method: 'POST', body: fd })
    if (!resp.ok) throw new Error((await resp.json()).detail || '提交失败')
    state.value = 'done'
  } catch (e) {
    errorMsg.value = e.message || '网络错误，请稍后重试'
    state.value = 'idle'
  }
}
</script>

<style scoped>
.feedback-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}
.feedback-section h2 {
  font-size: 1.1rem; color: var(--accent); margin-bottom: 6px; font-weight: 500;
}
.feedback-sub {
  font-size: .82rem; color: var(--text2); margin-bottom: 20px;
}
.feedback-form { display: flex; flex-direction: column; gap: 10px; }

textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  font-size: .88rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  font-family: inherit;
  transition: border-color .2s;
}
textarea:focus { border-color: var(--accent); }
textarea::placeholder { color: var(--text2); }
textarea:disabled { opacity: .6; }

.char-count {
  text-align: right; font-size: .72rem; color: var(--text2); margin-top: -6px;
}

.drop-zone {
  position: relative;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all .2s;
  background: var(--card);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  min-height: 100px;
  justify-content: center;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--accent);
  background: rgba(201,169,110,.04);
}
.drop-zone.has-preview {
  padding: 8px;
  border-style: solid;
  border-color: var(--accent-dim);
  cursor: default;
}
.drop-icon { font-size: 1.6rem; }
.drop-text { font-size: .85rem; color: var(--text2); }
.drop-text u { color: var(--accent); }
.drop-hint { font-size: .75rem; color: var(--text2); opacity: .6; }

.preview-img {
  max-width: 100%;
  max-height: 280px;
  border-radius: 8px;
  object-fit: contain;
  display: block;
}
.remove-img {
  position: absolute;
  top: 8px; right: 8px;
  width: 26px; height: 26px;
  border-radius: 50%;
  background: rgba(0,0,0,.55);
  color: #fff;
  border: none;
  cursor: pointer;
  font-size: .8rem;
  display: flex; align-items: center; justify-content: center;
  transition: background .2s;
}
.remove-img:hover { background: var(--danger); }

.feedback-error {
  font-size: .8rem;
  color: var(--danger);
  padding: 6px 10px;
  background: rgba(221,68,68,.08);
  border-radius: 6px;
}

.submit-btn {
  padding: 11px;
  background: var(--accent-dim);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  font-size: .9rem;
  cursor: pointer;
  transition: background .2s;
}
.submit-btn:hover:not(:disabled) { background: var(--accent); }
.submit-btn:disabled { opacity: .5; cursor: default; }
</style>
