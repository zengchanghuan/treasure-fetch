<template>
  <div class="subscribe-section">
    <div class="subscribe-inner">
      <div class="subscribe-icon">📬</div>
      <div class="subscribe-copy">
        <strong>订阅功能更新</strong>
        <span>Pro 上线、新功能发布时第一时间通知，不发广告</span>
      </div>
      <form class="subscribe-form" @submit.prevent="submit">
        <input
          v-model="email"
          type="email"
          placeholder="your@email.com"
          :disabled="state !== 'idle'"
          required
        />
        <button type="submit" :disabled="state !== 'idle'">
          {{ btnLabel }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const email = ref('')
const state = ref('idle') // idle | loading | done | error

const btnLabel = computed(() => ({
  idle: '订阅',
  loading: '提交中...',
  done: '✓ 已订阅',
  error: '重试',
}[state.value]))

async function submit() {
  if (!email.value) return
  state.value = 'loading'
  try {
    const resp = await fetch('/api/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    })
    if (!resp.ok) throw new Error()
    state.value = 'done'
    email.value = ''
  } catch {
    state.value = 'error'
    setTimeout(() => (state.value = 'idle'), 3000)
  }
}
</script>

<style scoped>
.subscribe-section {
  margin-top: 32px;
  padding: 20px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.subscribe-inner {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.subscribe-icon { font-size: 1.6rem; flex-shrink: 0; }
.subscribe-copy {
  flex: 1;
  min-width: 160px;
}
.subscribe-copy strong {
  display: block;
  font-size: .9rem;
  color: var(--text);
  margin-bottom: 3px;
}
.subscribe-copy span {
  font-size: .78rem;
  color: var(--text2);
}
.subscribe-form {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}
.subscribe-form input {
  padding: 9px 14px;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: .85rem;
  outline: none;
  width: 200px;
  -webkit-appearance: none;
  transition: border-color .2s;
}
.subscribe-form input:focus { border-color: var(--accent); }
.subscribe-form input::placeholder { color: var(--text2); }
.subscribe-form button {
  padding: 9px 18px;
  background: var(--accent-dim);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: .85rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background .2s;
}
.subscribe-form button:hover:not(:disabled) { background: var(--accent); }
.subscribe-form button:disabled { opacity: .6; cursor: default; }

@media (max-width: 520px) {
  .subscribe-inner { flex-direction: column; align-items: flex-start; }
  .subscribe-form { width: 100%; }
  .subscribe-form input { flex: 1; width: auto; }
}
</style>
