<template>
  <section class="faq-section">
    <h2>常见问题</h2>

    <details class="faq-item">
      <summary>为什么博物馆网站上的画作无法直接保存？</summary>
      <p>大多数博物馆数字平台只允许在线"放大浏览"，故意屏蔽了右键保存和截图工具，以保护版权和服务器带宽。一轴通过技术手段将在线浏览的画面还原成完整原图，让你能真正把它保存到本地。</p>
      <p class="faq-demo-row">
        没有可用链接？先试试效果：
        <button class="demo-btn" @click="copyDemo">{{ copyText }}</button>
      </p>
    </details>

    <details class="faq-item">
      <summary>支持哪些博物馆的藏品？</summary>
      <p>目前支持多个数字文博平台收录的书画作品，包括台北故宫博物院、大都会艺术博物馆、大英博物馆、故宫博物院等数十家机构的数字化藏品，总量超过数万件。</p>
    </details>

    <details class="faq-item">
      <summary>保存下来的图片质量怎么样？</summary>
      <p>输出为高质量 JPEG（接近无损）。分辨率由原始数字化采集决定，顶级藏品可达数万×数万像素，足以打印成超大幅临摹参考图，细节远超任何截图方式。多页册页作品会自动打包为 ZIP 文件。</p>
    </details>

    <details class="faq-item">
      <summary>等待时间有点长，正常吗？</summary>
      <p>正常。原图尺寸极大，一轴需要在后台分批获取并合并所有图像片段。通常几十秒到几分钟不等，画作尺寸越大、选择的分辨率越高，等待时间越长。等待期间请保持页面开着，完成后会自动弹出下载。</p>
    </details>

    <details class="faq-item">
      <summary>保存下来的画作可以商用吗？</summary>
      <p>本工具仅供个人学习、临摹练习与艺术研究使用。画作版权归原博物馆及收藏机构所有，商业使用前请自行获取授权。</p>
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
