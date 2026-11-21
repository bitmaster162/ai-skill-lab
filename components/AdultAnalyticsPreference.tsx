'use client';

import { useEffect, useRef } from 'react';

/** The separate document discards the optional tag when this audience route is left. */
export function AdultAnalyticsPreference({ locale }: { locale: 'ru' | 'en' }) {
  const frame = useRef<HTMLIFrameElement>(null);
  useEffect(() => {
    try {
      if (frame.current && localStorage.getItem('aisl.adult-analytics.v1') === 'allow') {
        frame.current.loading = 'eager';
      }
    } catch { /* Storage restrictions keep the footer preference control lazy. */ }
  }, []);

  return <iframe
    ref={frame}
    src="/analytics/preferences.htm"
    title={locale === 'en' ? 'Optional audience measurement (18+)' : 'Настройки статистики посещений (18+)'}
    width="100%" height="170" frameBorder="0" loading="lazy" referrerPolicy="no-referrer"
  />;
}
