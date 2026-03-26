export function trackEvent(event, props) {
  try {
    const blob = new Blob(
      [JSON.stringify({ event, properties: props || {} })],
      { type: 'application/json' },
    )
    navigator.sendBeacon('/api/event', blob)
  } catch { /* fire-and-forget */ }
}
