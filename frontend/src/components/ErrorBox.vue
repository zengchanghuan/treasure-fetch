<template>
  <Transition name="fade">
    <div v-if="error" class="error">
      <div class="err-title">⚠️ {{ friendly.title }}</div>
      <div class="err-hint">{{ friendly.hint }}</div>
      <a v-if="friendly.upgrade" href="#pricing" class="upgrade-cta">查看 Pro 套餐 →</a>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'
import { friendlyError } from '../api.js'

const props = defineProps({ error: { type: String, default: '' } })
const friendly = computed(() => friendlyError(props.error))
</script>

<style scoped>
.error {
  margin-top: 16px; padding: 14px 16px;
  background: rgba(221,68,68,.08); border: 1px solid rgba(221,68,68,.25);
  border-radius: 10px; color: var(--danger); font-size: .85rem; line-height: 1.7;
}
.err-title { font-weight: 600; margin-bottom: 4px; }
.err-hint { font-size: .8rem; opacity: .8; margin-top: 6px; }
.upgrade-cta {
  display: inline-block;
  margin-top: 10px;
  padding: 6px 16px;
  background: var(--accent-dim);
  color: #fff;
  border-radius: 20px;
  font-size: .8rem;
  text-decoration: none;
  transition: background .2s;
}
.upgrade-cta:hover { background: var(--accent); }
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
