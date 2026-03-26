<template>
  <Transition name="fade">
    <div v-if="error" class="error">
      <div class="err-title">⚠️ {{ friendly.title }}</div>
      <div class="err-hint">{{ friendly.hint }}</div>
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
.fade-enter-active, .fade-leave-active { transition: opacity .25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
