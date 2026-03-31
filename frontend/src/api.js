const URL_RE = /g2\.ltfc\.net\/view\/[A-Za-z]+\/[a-f0-9]{24}/

export const DEMO_URL = 'https://g2.ltfc.net/view/SUHA/647a19401977e748e6a9bfbe'

export function extractUrl(raw) {
  const m = raw.match(URL_RE)
  return m ? 'https://' + m[0] : null
}

export function isValidUrl(raw) {
  return URL_RE.test(raw)
}

export async function fetchMetadata(url) {
  const resp = await fetch('/api/metadata', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!resp.ok) throw new Error((await resp.json()).detail || '请求失败')
  return resp.json()
}

export async function startDownload(url, level) {
  const resp = await fetch('/api/download', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, level }),
  })
  if (!resp.ok) throw new Error((await resp.json()).detail || '启动失败')
  return resp.json()
}

export async function fetchProgress(taskId) {
  const resp = await fetch(`/api/progress/${taskId}`)
  if (!resp.ok) return null
  return resp.json()
}

export async function fetchQuota() {
  const resp = await fetch('/api/quota')
  if (!resp.ok) return null
  return resp.json()
}

export function triggerFileDownload(taskId, filename) {
  const a = document.createElement('a')
  a.href = `/api/result/${taskId}`
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
}

export function friendlyError(raw) {
  if (!raw) return { title: '出了点小问题', hint: '请稍后再试，或刷新页面重新尝试。' }
  if (/无法识别|有效链接|格式/.test(raw))
    return { title: '链接格式不对哦 🤔', hint: '请从 g2.ltfc.net 复制完整的作品页面地址，格式形如 g2.ltfc.net/view/SUHA/…' }
  if (/今日免费下载额度已用完|今日.*额度/.test(raw))
    return { title: '今日免费工具次数已用完', hint: '免费版每日可还原 3 次，明日 0 点自动重置。升级 Pro 可获得每日 30 次额度。', upgrade: true }
  if (/今日高清下载额度已用完|高清.*额度/.test(raw))
    return { title: '高清额度已用完', hint: '高清还原属于 Pro 专属功能，或改选标清分辨率继续使用。', upgrade: true }
  if (/过于频繁|请.*秒后再试/.test(raw))
    return { title: '操作太频繁，稍等片刻 🙏', hint: raw }
  if (/无此资源|404|not found/i.test(raw))
    return { title: '没有找到这件作品 😕', hint: '该作品可能已下架或链接有误，请到原网站确认链接是否仍然有效。' }
  if (/上游|upstream|API|500|server/i.test(raw))
    return { title: '数据源暂时开小差了 😓', hint: '上游服务偶有波动，请稍等 1–2 分钟后重试。若持续出现，欢迎反馈给我们。' }
  if (/网络|network|fetch|connect/i.test(raw))
    return { title: '网络好像断了 🌐', hint: '请检查你的网络连接后重试。' }
  return { title: '出了点小问题', hint: raw }
}
