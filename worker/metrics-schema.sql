-- no raw requests, addresses, referrers, or visitor identifiers are stored.
CREATE TABLE IF NOT EXISTS metrics_daily (
  day TEXT NOT NULL,
  scene TEXT NOT NULL CHECK(scene IN ('temple','redwoods','forest','website')),
  event TEXT NOT NULL CHECK(event IN ('page_view','project_click','project_view','live_click','resume_click','contact_click','portfolio_click')),
  project TEXT NOT NULL DEFAULT '',
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day,scene,event,project)
);
CREATE TABLE IF NOT EXISTS metrics_limit (
  id INTEGER PRIMARY KEY CHECK(id=1),
  minute INTEGER NOT NULL,
  count INTEGER NOT NULL
);
