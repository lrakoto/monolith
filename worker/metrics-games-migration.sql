-- no raw requests, addresses, referrers, or visitor identifiers are stored.
CREATE TABLE metrics_daily_v2 (
  day TEXT NOT NULL,
  scene TEXT NOT NULL CHECK(scene IN ('temple','redwoods','forest','website','games')),
  event TEXT NOT NULL CHECK(event IN ('page_view','project_click','project_view','live_click','game_launch','resume_click','contact_click','portfolio_click')),
  project TEXT NOT NULL DEFAULT '',
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day,scene,event,project)
);

INSERT INTO metrics_daily_v2 SELECT * FROM metrics_daily;
DROP TABLE metrics_daily;
ALTER TABLE metrics_daily_v2 RENAME TO metrics_daily;
