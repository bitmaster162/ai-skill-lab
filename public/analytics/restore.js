try {
  const frame = document.querySelector('iframe[src="/analytics/preferences.htm"]');
  if (frame && localStorage.getItem('aisl.adult-analytics.v1') === 'allow') frame.loading = 'eager';
} catch {}
