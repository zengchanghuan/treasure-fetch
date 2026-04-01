<template>
  <section class="faq-section">
    <h2>常见问题</h2>

    <details class="faq-item">
      <summary>一轴现在提供什么服务？</summary>
      <p>当前版本聚焦台北故宫博物院公开馆藏页面，提供作者、年代、尺寸、馆藏与简介等资料整理，并保留研究辅助所需的处理能力。使用前请先阅读并遵守原站的使用规则。</p>
      <p class="faq-demo-row">
        没有可用链接？先试试效果：
        <button class="demo-btn" @click="copyDemo">{{ copyText }}</button>
      </p>
    </details>

    <details class="faq-item">
      <summary>支持哪些博物馆的藏品？</summary>
      <p>当前仅支持台北故宫博物院公开馆藏页面。其他机构来源暂不开放，以保证服务范围、页面口径与实际能力保持一致。</p>
    </details>

    <details class="faq-item">
      <summary>资料页里会展示哪些信息？</summary>
      <p>系统会整理作者、年代、尺寸、馆藏、标签、简介与页面分辨率等信息，方便你先做检索、笔记与研究判断，再决定是否回到馆方页面继续查看。</p>
    </details>

    <details class="faq-item">
      <summary>等待时间有点长，正常吗？</summary>
      <p>正常。部分页面资料较大，系统需要先完成元数据整理与图像处理准备。通常几十秒内会返回结果；若页面尺寸较大或网络波动，等待时间会更长。</p>
    </details>

    <details class="faq-item">
      <summary>这些资料或图像可以商用吗？</summary>
      <p>不能默认视为可商用。请以台北故宫博物院公开页面的使用规则、版权说明与授权要求为准；如涉及出版、商用或再分发，请先自行取得授权。</p>
    </details>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { DEMO_URL } from '../api.js'

const copyText = ref('复制示例链接')

function copyDemo() {
  navigator.clipboard.writeText(DEMO_URL).then(() => {
    copyText.value = '✓ 已复制'
    setTimeout(() => (copyText.value = '复制示例链接'), 2000)
  }).catch(() => {
    copyText.value = '复制失败，请手动复制'
    setTimeout(() => (copyText.value = '复制示例链接'), 2000)
  })
}
</script>

<style scoped>
.faq-section { margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--border); }
.faq-section h2 { font-size: 1.1rem; color: var(--accent); margin-bottom: 20px; font-weight: 500; }
.faq-item { margin-bottom: 20px; }
.faq-item summary {
  cursor: pointer; color: var(--text); font-size: .92rem; font-weight: 500;
  padding: 10px 0; list-style: none; display: flex; align-items: center; gap: 8px;
}
.faq-item summary::before { content: '▸'; color: var(--accent-dim); transition: transform .2s; }
.faq-item[open] summary::before { transform: rotate(90deg); }
.faq-item p { color: var(--text2); font-size: .85rem; line-height: 1.8; padding: 4px 0 8px 20px; }
.faq-item a { color: var(--accent); text-decoration: none; }
.faq-item a:hover { text-decoration: underline; }
.faq-demo-row { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.faq-demo-hint { font-size: .8rem; color: var(--text2); opacity: .7; }
.demo-btn {
  padding: 5px 14px; background: transparent; color: var(--accent);
  border: 1px dashed var(--accent); border-radius: 20px; font-size: .82rem;
  cursor: pointer; transition: all .2s; min-height: 36px;
}
.demo-btn:hover { background: rgba(201,169,110,.12); }
</style>
