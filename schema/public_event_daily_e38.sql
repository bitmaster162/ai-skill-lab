CREATE TABLE public_event_daily_e38 (
  day TEXT NOT NULL CHECK(day GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'),
  event_name TEXT NOT NULL CHECK(event_name IN (
    'lead_submit_ok',
    'lead_submit_error',
    'cal_click',
    'telegram_click',
    'whatsapp_click',
    'line_click',
    'email_click'
  )),
  page TEXT NOT NULL CHECK(length(page) BETWEEN 1 AND 180 AND substr(page, 1, 1) = '/' AND substr(page, 1, 2) != '//'),
  locale TEXT NOT NULL CHECK(locale IN ('ru', 'en')),
  count INTEGER NOT NULL CHECK(count >= 1),
  PRIMARY KEY (day, event_name, page, locale)
);
