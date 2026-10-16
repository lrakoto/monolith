-- copy every existing aggregate before extending the accepted activity types.
-- apply once before publishing the worker that accepts the artdex scene.
-- keep the previous table as an additional recovery copy.
CREATE TABLE metrics_daily_artdex (
  day TEXT NOT NULL,
  scene TEXT NOT NULL CHECK(scene IN ('temple','redwoods','forest','website','games','artdex')),
  event TEXT NOT NULL CHECK(event IN ('page_view','project_click','project_view','live_click','game_launch','resume_click','contact_click','portfolio_click','asset_view','asset_download','filter_use','asset_save')),
  project TEXT NOT NULL DEFAULT '',
  count INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(day,scene,event,project),
  CHECK(event NOT IN ('asset_view','asset_download','filter_use','asset_save') OR scene='artdex'),
  CHECK(scene<>'artdex' OR (project='' AND event IN ('page_view','asset_view','asset_download','filter_use','asset_save')))
);

INSERT INTO metrics_daily_artdex SELECT * FROM metrics_daily;
ALTER TABLE metrics_daily RENAME TO metrics_daily_pre_artdex;
ALTER TABLE metrics_daily_artdex RENAME TO metrics_daily;
