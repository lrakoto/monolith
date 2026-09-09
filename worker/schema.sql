-- One row per signal. Deliberately thin: a kind, whatever name the caller gave
-- for itself, and when. Nothing about who or from where, because the footer is
-- a guestbook and a guestbook that recorded its visitors would be surveillance
-- wearing a nicer word.
CREATE TABLE IF NOT EXISTS signals (
  id    INTEGER PRIMARY KEY AUTOINCREMENT,
  kind  TEXT    NOT NULL CHECK (kind IN ('hello', 'helpful', 'unhelpful')),
  agent TEXT,
  ts    INTEGER NOT NULL
);

-- the tally groups by kind on every read, and the flood cap counts a trailing
-- minute; both are the whole table without these
CREATE INDEX IF NOT EXISTS signals_kind ON signals (kind);
CREATE INDEX IF NOT EXISTS signals_ts   ON signals (ts);

-- The wallet held a little dust before any of this existed, and a footer that
-- announced it as a tip would be claiming something that did not happen. The
-- baseline is the balance at the moment the counter went up; what the page
-- shows is whatever arrived after it.
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
