CREATE TABLE IF NOT EXISTS tip_transfers (
  hash TEXT NOT NULL,
  log_index INTEGER NOT NULL,
  block INTEGER NOT NULL,
  timestamp INTEGER NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('in', 'out', 'self')),
  amount TEXT NOT NULL,
  PRIMARY KEY (hash, log_index)
);
CREATE INDEX IF NOT EXISTS tip_transfers_recent ON tip_transfers (block DESC, log_index DESC);
