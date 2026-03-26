<template>
  <SplashLoader />
  <WeChatBanner />
  <AppHeader />

  <main>
    <UrlInput v-model="url" :loading="fetching" @submit="onFetch" @auto-submit="onFetch" />
    <DemoLinks @fill="onDemoFill" />
    <ErrorBox :error="error" />
    <EmptyState :visible="!meta && !error" />

    <MetaCard
      v-if="meta"
      :meta="meta"
      :downloading="downloading"
      :is-done="isDone"
      :status-text="statusText"
      :progress="progress"
      @download="onDownload"
    />

    <HowToSection />
    <FaqSection />
  </main>

  <AppFooter />
</template>

<script setup>
import { ref, reactive } from 'vue'
import { extractUrl, fetchMetadata, startDownload, fetchProgress, triggerFileDownload } from './api.js'
import { trackEvent } from './tracker.js'

import SplashLoader from './components/SplashLoader.vue'
import WeChatBanner from './components/WeChatBanner.vue'
import AppHeader from './components/AppHeader.vue'
import UrlInput from './components/UrlInput.vue'
import DemoLinks from './components/DemoLinks.vue'
import ErrorBox from './components/ErrorBox.vue'
import EmptyState from './components/EmptyState.vue'
import MetaCard from './components/MetaCard.vue'
import HowToSection from './components/HowToSection.vue'
import FaqSection from './components/FaqSection.vue'
import AppFooter from './components/AppFooter.vue'

trackEvent('page_view', { path: location.pathname, referer: document.referrer })

const url = ref('')
const fetching = ref(false)
const error = ref('')
const meta = ref(null)
const downloading = ref(false)
const isDone = ref(false)
const statusText = ref('')
const progress = reactive({ status: '', done: 0, total: 0, message: '' })

let currentUrl = ''
let pollStopped = true

function reset() {
  pollStopped = true
  meta.value = null
  isDone.value = false
  statusText.value = ''
  Object.assign(progress, { status: '', done: 0, total: 0, message: '' })
}

async function onFetch() {
  const extracted = extractUrl(url.value)
  if (!extracted) { error.value = '链接格式不对'; return }
  error.value = ''
  fetching.value = true
  reset()
  try {
    currentUrl = extracted
    meta.value = await fetchMetadata(extracted)
    trackEvent('metadata_fetch', { url: extracted })
  } catch (e) {
    error.value = e.message
  } finally {
    fetching.value = false
  }
}

function onDemoFill(demoUrl) {
  url.value = demoUrl
  onFetch()
}

async function onDownload(level) {
  if (!currentUrl) return
  error.value = ''
  downloading.value = true
  statusText.value = ''
  Object.assign(progress, { status: '', done: 0, total: 0, message: '' })

  try {
    const { task_id } = await startDownload(currentUrl, level)
    pollStopped = false
    trackEvent('download_start', { url: currentUrl, level })
    pollTask(task_id)
  } catch (e) {
    error.value = e.message
    downloading.value = false
  }
}

function pollTask(taskId) {
  async function tick() {
    if (pollStopped) return
    try {
      const d = await fetchProgress(taskId)
      if (pollStopped || !d) return
      Object.assign(progress, d)

      if (d.status === 'done') {
        pollStopped = true
        isDone.value = true
        downloading.value = false
        statusText.value = '下载完成 ✓'
        const ext = meta.value?.layout_type === 'PAGE' ? '.zip' : '.jpg'
        triggerFileDownload(taskId, (d.filename || 'artwork') + ext)
        trackEvent('download_done', { url: currentUrl })
        return
      }
      if (d.status === 'error') {
        pollStopped = true
        downloading.value = false
        error.value = d.message
        return
      }
    } catch { /* transient */ }
    if (!pollStopped) setTimeout(tick, 500)
  }
  setTimeout(tick, 500)
}
</script>

<style>
main { width: 100%; max-width: 720px; padding: 32px 20px 80px; }
</style>
