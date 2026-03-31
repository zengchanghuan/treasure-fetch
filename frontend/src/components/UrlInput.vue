<template>
  <div class="input-group">
    <input
      ref="inputEl"
      v-model="inputValue"
      type="text"
      placeholder="粘贴书画作品页面链接…"
      @keydown.enter="$emit('submit')"
      @input="onInput"
    />
    <button class="btn" :disabled="loading" @click="$emit('submit')">
      {{ loading ? '解析中...' : '解析' }}
    </button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { isValidUrl } from '../api.js'

const props = defineProps({ modelValue: String, loading: Boolean })
const emit = defineEmits(['update:modelValue', 'submit', 'auto-submit'])

const inputEl = ref(null)
const inputValue = ref(props.modelValue || '')
let debounce = null

watch(() => props.modelValue, (v) => { inputValue.value = v || '' })

function onInput() {
  emit('update:modelValue', inputValue.value)
  clearTimeout(debounce)
  if (!inputValue.value.trim()) return
  debounce = setTimeout(() => {
    if (isValidUrl(inputValue.value)) emit('auto-submit')
  }, 400)
}

onMounted(() => {
  const params = new URLSearchParams(location.search)
  const prefill = params.get('url')
  if (prefill && isValidUrl(prefill)) {
    inputValue.value = prefill
    emit('update:modelValue', prefill)
    setTimeout(() => emit('auto-submit'), 200)
  }
})

defineExpose({ focus: () => inputEl.value?.focus() })
</script>

<style scoped>
.input-group { display: flex; gap: 10px; }
.input-group input {
  flex: 1; padding: 12px 16px; background: var(--card);
  border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text); font-size: 16px; outline: none;
  transition: all .3s ease; min-height: 44px; -webkit-appearance: none;
}
.input-group input:focus { border-color: var(--accent); box-shadow: 0 0 12px var(--glow); }
.input-group input::placeholder { color: var(--text2); }
@media (max-width: 520px) {
  .input-group { flex-direction: column; }
  .input-group input { font-size: 16px; }
}
</style>
