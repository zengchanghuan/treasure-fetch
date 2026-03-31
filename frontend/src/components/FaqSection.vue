<template>
  <section class="faq-section">
    <h2>常见问题</h2>

    <details class="faq-item">
      <summary>什么是瓦片图 (Deep Zoom Tiles)？</summary>
      <p>瓦片图是一种将超高分辨率图片切割成无数小方块（通常 512×512 像素）的技术，类似地图软件的缩放。博物馆网站使用这种技术让用户流畅地浏览巨幅画作，但无法直接保存完整原图。一轴能自动下载所有碎片并无损拼接还原为完整的高清大图。</p>
      <p class="faq-demo-row">
        没有可用链接？
        <button class="demo-btn" @click="copyDemo">{{ copyText }}</button>
        <span class="faq-demo-hint">复制后粘贴到上方输入框即可体验</span>
      </p>
    </details>

    <details class="faq-item">
      <summary>支持哪些网站和博物馆？</summary>
      <p>目前支持 <a href="https://g2.ltfc.net" target="_blank">g2.ltfc.net</a> 收录的所有书画作品，涵盖台北故宫博物院、大都会艺术博物馆、大英博物馆等数十家文博机构的数字化藏品。</p>
    </details>

    <details class="faq-item">
      <summary>下载的图片是什么格式？分辨率有多高？</summary>
      <p>单幅画作输出为 JPEG 格式（quality=95，近无损）。多页册页会自动打包为 ZIP。分辨率取决于原始数据，部分顶级藏品可达数万×数万像素。你可以在解析后自由选择不同的缩放级别（Level），级别越高，分辨率越大，下载耗时也越长。</p>
    </details>

    <details class="faq-item">
      <summary>下载速度慢怎么办？</summary>
      <p>高分辨率画作可能包含数百甚至上千张图块，下载时间从几十秒到几分钟不等。建议选择适中的分辨率级别，并确保网络连接稳定。下载期间请勿关闭或刷新页面。</p>
    </details>

    <details class="faq-item">
      <summary>下载的画作可以商用吗？</summary>
      <p>本工具仅供个人学习与艺术交流使用。画作的版权归原博物馆或收藏机构所有，商业使用前请获取相关机构的正式授权。</p>
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
