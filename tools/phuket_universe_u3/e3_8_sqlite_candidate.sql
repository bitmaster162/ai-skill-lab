-- OFFLINE SQLITE DESIGN ONLY. Never execute against Cloudflare D1 without
-- a separate approval, tested D1 migration adapter, snapshot and rollback plan.
-- The old E3.8 event counter allows seven names. This preserves existing rows
-- while extending the CHECK constraint to exactly three Universe click events.
BEGIN TRANSACTION;
CREATE TABLE public_event_daily_e38_next (
  day TEXT NOT NULL CHECK(day GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  event_name TEXT NOT NULL CHECK(event_name IN (
    'lead_submit_ok', 'lead_submit_error',
    'cal_click', 'telegram_click', 'whatsapp_click', 'line_click', 'email_click',
    'universe_click', 'project_click', 'listing_click'
  )),
  page TEXT NOT NULL CHECK(length(page) BETWEEN 1 AND 180 AND substr(page, 1, 1) = '/' AND substr(page, 1, 2) != '//'),
  locale TEXT NOT NULL CHECK(locale IN ('ru', 'en')),
  count INTEGER NOT NULL CHECK(count >= 1),
  PRIMARY KEY(day, event_name, page, locale)
);
INSERT INTO public_event_daily_e38_next (day, event_name, page, locale, count)
SELECT day, event_name, page, locale, count FROM public_event_daily_e38;
DROP TABLE public_event_daily_e38;
ALTER TABLE public_event_daily_e38_next RENAME TO public_event_daily_e38;
COMMIT;
