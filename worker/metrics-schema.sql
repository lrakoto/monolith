-- no raw requests, addresses, referrers, or visitor identifiers are stored.
CREATE TABLE IF NOT EXISTS metrics_daily (
  day TEXT NOT NULL,
  scene TEXT NOT NULL CHECK(scene IN ('temple','redwoods','forest','website','games','artdex')),
  event TEXT NOT NULL CHECK(event IN ('page_view','project_click','project_view','live_click','game_launch','resume_click','contact_click','portfolio_click','asset_view','asset_download','filter_use','asset_save')),
  project TEXT NOT NULL DEFAULT '',
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day,scene,event,project),
  CHECK(event NOT IN ('asset_view','asset_download','filter_use','asset_save') OR scene='artdex'),
  CHECK(scene<>'artdex' OR (project='' AND event IN ('page_view','asset_view','asset_download','filter_use','asset_save')))
);
CREATE TABLE IF NOT EXISTS metrics_limit (
  id INTEGER PRIMARY KEY CHECK(id=1),
  minute INTEGER NOT NULL,
  count INTEGER NOT NULL
);
