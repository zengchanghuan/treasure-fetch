<template>
  <Transition name="slide">
    <div v-if="show" class="wx-banner">
      <span class="wx-icon">💬</span>
      <div class="wx-body">
        <strong>请在系统浏览器中打开，体验更佳</strong>
        微信内置浏览器不支持文件下载，下载功能将无法正常使用。
        <ul class="wx-steps">
          <li>① 点击右上角 <strong>「···」</strong> 菜单</li>
          <li>② 选择 <strong>「在浏览器中打开」</strong></li>
        </ul>
      </div>
      <button class="wx-close" @click="dismiss" aria-label="关闭">✕</button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
const show = ref(false)

onMounted(() => {
  if (/MicroMessenger/i.test(navigator.userAgent)) {
    show.value = true
    document.body.classList.add('has-wechat-banner')
  }
})
onUnmounted(() => document.body.classList.remove('has-wechat-banner'))

function dismiss() {
  show.value = false
  document.body.classList.remove('has-wechat-banner')
}
</script>

<style scoped>
.wx-banner {
  position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
  background: linear-gradient(135deg, #07c160, #059652);
  color: #fff; padding: 12px 16px; display: flex; align-items: flex-start; gap: 10px;
  box-shadow: 0 2px 12px rgba(0,0,0,.3);
}
.wx-icon { font-size: 1.4rem; flex-shrink: 0; margin-top: 2px; }
.wx-body { flex: 1; font-size: .85rem; line-height: 1.6; }
.wx-body strong { font-size: .9rem; display: block; margin-bottom: 3px; }
.wx-steps { margin-top: 6px; font-size: .78rem; opacity: .92; padding-left: 0; list-style: none; }
.wx-steps li { margin-bottom: 2px; }
.wx-close {
  background: rgba(255,255,255,.25); border: none; color: #fff; border-radius: 50%;
  width: 26px; height: 26px; font-size: .9rem; cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; touch-action: manipulation;
}
.wx-close:hover { background: rgba(255,255,255,.4); }
.slide-leave-active { transition: opacity .3s, transform .3s; }
.slide-leave-to { opacity: 0; transform: translateY(-100%); }
</style>
