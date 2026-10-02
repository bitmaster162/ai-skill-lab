CREATE TABLE IF NOT EXISTS route_rate_event_r159 (
  request_id TEXT PRIMARY KEY NOT NULL,
  ip_token TEXT NOT NULL CHECK (length(ip_token) = 64),
  occurred_at INTEGER NOT NULL CHECK (occurred_at > 0)
);
CREATE INDEX IF NOT EXISTS route_rate_event_r159_ip_time_idx
  ON route_rate_event_r159 (ip_token, occurred_at);
CREATE INDEX IF NOT EXISTS route_rate_event_r159_time_idx
  ON route_rate_event_r159 (occurred_at);
