<template>
  <section class="pricing-section">
    <h2>工具套餐</h2>
    <p class="pricing-sub">按工具使用次数计费，不卖图片，只卖能力</p>

    <div class="plans">
      <!-- 免费版 -->
      <div class="plan">
        <div class="plan-header">
          <div class="plan-name">免费版</div>
          <div class="plan-price">¥0</div>
          <div class="plan-cycle">永久免费</div>
        </div>
        <ul class="plan-features">
          <li><span class="ok">✓</span> 每日解析 <strong>20</strong> 次</li>
          <li><span class="ok">✓</span> 每日还原 <strong>3</strong> 次</li>
          <li><span class="ok">✓</span> 标清分辨率（适合临帖、参考）</li>
          <li><span class="ok">✓</span> 单幅图片还原</li>
          <li><span class="no">✗</span> 最高清分辨率</li>
          <li><span class="no">✗</span> 批量下载</li>
        </ul>
        <div class="plan-cta plan-cta--free">当前方案</div>
      </div>

      <!-- Pro 版 -->
      <div class="plan plan--pro">
        <div class="plan-badge">推荐</div>
        <div class="plan-header">
          <div class="plan-name">Pro 专业版</div>
          <div class="plan-price">¥29<span class="plan-unit">/月</span></div>
          <div class="plan-cycle">或 ¥199/年（省 ¥149）</div>
        </div>
        <ul class="plan-features">
          <li><span class="ok">✓</span> 每日解析 <strong>无限</strong> 次</li>
          <li><span class="ok">✓</span> 每日还原 <strong>30</strong> 次</li>
          <li><span class="ok">✓</span> 最高清分辨率（原始像素级）</li>
          <li><span class="ok">✓</span> 单幅图片还原</li>
          <li><span class="ok pro-future">✓</span> 批量下载 <span class="coming">开发中</span></li>
          <li><span class="ok">✓</span> 优先处理队列</li>
        </ul>
        <button class="plan-cta plan-cta--pro" @click="joinWaitlist">
          加入候补名单
        </button>
        <p class="plan-note">公测期间免费开放，正式上线前通知</p>
      </div>
    </div>
  </section>
</template>

<script setup>
function joinWaitlist() {
  window.open('mailto:hi@moyun.art?subject=申请加入%20Pro%20候补名单&body=您好，我希望在%20Pro%20版本上线时第一时间获得通知。', '_blank')
}
</script>

<style scoped>
.pricing-section {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--border);
}
.pricing-section h2 {
  font-size: 1.1rem; color: var(--accent);
  margin-bottom: 6px; font-weight: 500; text-align: center;
}
.pricing-sub {
  text-align: center; color: var(--text2);
  font-size: .82rem; margin-bottom: 24px;
}

.plans {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.plan {
  position: relative;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 24px 20px 20px;
}
.plan--pro {
  border-color: var(--accent);
  box-shadow: 0 0 20px rgba(201, 169, 110, 0.12);
}

.plan-badge {
  position: absolute;
  top: -11px; left: 50%;
  transform: translateX(-50%);
  background: var(--accent);
  color: #1a1a1a;
  font-size: .72rem;
  font-weight: 700;
  padding: 2px 14px;
  border-radius: 20px;
  letter-spacing: 1px;
}

.plan-header { text-align: center; margin-bottom: 20px; }
.plan-name { font-size: .88rem; color: var(--text2); margin-bottom: 8px; }
.plan-price {
  font-size: 2rem; font-weight: 700; color: var(--text); line-height: 1;
}
.plan--pro .plan-price { color: var(--accent); }
.plan-unit { font-size: 1rem; font-weight: 400; }
.plan-cycle { font-size: .75rem; color: var(--text2); margin-top: 4px; }

.plan-features {
  list-style: none;
  font-size: .82rem;
  color: var(--text2);
  line-height: 1;
  margin-bottom: 20px;
}
.plan-features li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 0;
  border-bottom: 1px solid var(--border);
}
.plan-features li:last-child { border-bottom: none; }
.plan-features strong { color: var(--text); }
.ok { color: var(--green); font-size: .9rem; }
.pro-future { color: var(--accent-dim); }
.no { color: var(--text2); opacity: .4; }
.coming {
  margin-left: auto;
  font-size: .7rem;
  background: rgba(201,169,110,.15);
  color: var(--accent-dim);
  padding: 1px 7px;
  border-radius: 10px;
}

.plan-cta {
  display: block;
  width: 100%;
  padding: 11px;
  border-radius: 8px;
  font-size: .88rem;
  text-align: center;
  cursor: pointer;
  border: none;
  transition: all .2s;
}
.plan-cta--free {
  background: var(--border);
  color: var(--text2);
  cursor: default;
}
.plan-cta--pro {
  background: var(--accent-dim);
  color: #fff;
}
.plan-cta--pro:hover { background: var(--accent); }
.plan-note {
  text-align: center; font-size: .72rem;
  color: var(--text2); opacity: .6; margin-top: 8px; margin-bottom: 0;
}

@media (max-width: 520px) {
  .plans { grid-template-columns: 1fr; }
}
</style>
