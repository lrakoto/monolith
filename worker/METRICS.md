# Anonymous activity counts

POST `/api/events` accepts a small JSON object containing `event`, `scene`, and an optional allowlisted `project` slug. It returns no data. Daily aggregate counts live in D1; there is no public reporting endpoint. The guestbook endpoints remain separate.

Install `metrics-schema.sql` before deploying the worker. The portfolio loads `assets/metrics.js`; WordPress loads the same file through `root/mu-plugins/305-metrics.php`. The plugin skips signed-in visits and previews. The script skips localhost, studies, browser automation and DNT/GPC opt-outs. Session storage holds only deduplication flags, not visitor IDs. Data counts once per event/project, site/scene and tab session. Tabs or cleared storage can produce additional counts. Site/scene visits are not unique people. No referrers, raw page URLs, form values or browser details are sent. Hosting infrastructure can still have its own request logs.

`page_view` means the first visible visit to a site or scene in a tab session. Root WordPress pages are grouped as `website`. Other events measure detail-dialog opens and live-project, résumé, email and WordPress-to-portfolio link clicks. These do not prove a completed download, sent email or inquiry. No cross-site funnel is inferred. Reports have no historical data before installation.

The endpoint accepts only same-origin POSTs and fixed event, scene and project values. A shared cap of 240 accepted submissions per minute bounds floods without recording callers. Origin headers and client deduplication are not authentication: synthetic or repeated requests can inflate counts. Treat these as directional activity, not audited conversions.

Read a private report with your existing Cloudflare login:

```sh
python3 tools/metrics_report.py --days 30
```

The HTML report goes under `artifacts/metrics/`, excluded from deployment. Ask Codex to refresh and open it, or open that file locally. Use `wrangler login` if your authorization expires. The report uses direct authenticated D1 queries, not a token embedded in the website.

To stop collection, remove the metrics script tags and the WordPress mu-plugin. Existing daily aggregates remain. No worker route has been broadened beyond `/api/*`.

For a private dashboard with automatic refresh:

```sh
python3 tools/metrics_dashboard.py
```

Open the localhost URL printed by the command. Keep the command running while viewing it. The dashboard refreshes every 60 seconds while visible, pauses in hidden tabs, and stops requesting data when closed. Credentials stay in Wrangler, never in the HTML. Only the loopback interface is served, with a random path, host validation, and no CORS access. Multiple viewing tabs share a 60-second cache. A persisted conservative daily read reservation caps dashboard queries below one million rows per UTC day; reaching that cap pauses updates until the next day. The report remains visible after refresh failures. This uses existing free-tier allowances, adds no subscription, and never upgrades billing. Other account usage still shares Cloudflare's limits.

## Hosted dashboard

The primary report is now WordPress Admin → Dashboard → 305 Metrics, at `/wp-admin/index.php?page=305-metrics`. WordPress requires the `manage_options` capability and an AJAX nonce. A dedicated server-only key authenticates WordPress requests to `/api/metrics-report`. That endpoint rejects unauthenticated reads and has no CORS permission. The secret is held in Worker secrets and an ABSPATH-guarded PHP file, installed from a GitHub Actions secret. No Cloudflare account credentials are stored in WordPress or browser JavaScript.

The hosted view refreshes every 60 seconds while visible and stops polling when closed. WordPress shares a 60-second cache across devices and reserves database reads before fetching, reconciling against returned row usage. A one-million-row daily allowance pauses report queries before using the full free-tier allowance. Guestbook endpoints and public-site routing stay unchanged. The local report remains optional; the laptop is no longer needed for the hosted dashboard or collection.


### September 25 update

Reporting accepts only 7, 30 or 90 days and caches each period separately. The WordPress date selector uses the same allowlist. Its daily one-million-row budget remains unchanged; each fetch now reserves 40,000 rows to cover the largest permitted date range, then reconciles actual usage. All project names are presented as readable labels.

`game_launch` records a Play Beta link click for `pyxel` or `blockshooter`. It does not prove the game loaded or that someone played. Field-log visits use the `games` scene; study pages remain excluded. Previous game links remain `live_click`, because their destination cannot be inferred from the historic aggregates. Apply `metrics-games-migration.sql` once before deploying this version; it copies existing counts into the extended schema.

### Artdex

Artdex uses the same collector and private WordPress dashboard, with its own `artdex` scene. Both the hosted and local reports show a dedicated Artdex section; Artdex visits do not increase the portfolio or WordPress totals.

The accepted Artdex events are `page_view`, `asset_view` (Asset previews), `asset_download` (Download clicks), `filter_use` (Filter uses), and `asset_save` (Asset saves). Each has an empty `project` value. New asset events are rejected for every other scene, and portfolio events other than `page_view` are rejected for Artdex. Existing portfolio and game event rules stay the same.

Artdex counts an activity type once per tab session across the whole catalog, rather than per asset or search. Only the UTC day, fixed scene and event, empty project and aggregate count are stored. Asset IDs or names, tags, search terms, URLs, admin identities, email addresses and form content are not included. The standalone Artdex client excludes its signed-in admin and initial account setup, honors DNT/GPC, and skips local previews and browser automation. A download click measures intent, not a completed transfer or a sale. Collection begins when the integration is installed; no earlier visits are reconstructed.

For an existing database, export a private backup, then apply `metrics-artdex-migration.sql` once **before** publishing the worker. It copies every existing aggregate, retains the previous table as `metrics_daily_pre_artdex`, and keeps `metrics_limit` intact. Run the SQL file as one remote import, not as separate commands; Cloudflare's import operation is atomic ([D1 import behavior](https://blog.cloudflare.com/building-d1-a-global-database/)). The fresh-install `metrics-schema.sql` already includes Artdex and should not be used to migrate an existing table. From `worker/`, using the existing authenticated Cloudflare login:

```sh
wrangler whoami
wrangler d1 info signals
wrangler d1 export signals --remote --output /private/tmp/signals-before-artdex.sql
wrangler d1 execute signals --remote --file metrics-artdex-migration.sql
wrangler d1 execute signals --remote --command "SELECT COUNT(*) AS missing_or_reduced FROM metrics_daily_pre_artdex b LEFT JOIN metrics_daily a ON a.day=b.day AND a.scene=b.scene AND a.event=b.event AND a.project=b.project WHERE a.count IS NULL OR a.count < b.count;"
wrangler deploy
```

Keep the backup private and out of Git. Verify the database account and worker name against `wrangler.toml` first; stop if either migration table already exists, rather than rerunning or deleting it. The verification query must return zero before deploying. New traffic may increase counts, so comparing exact totals after migration is not sufficient. The route remains only `threeohfivestudios.com/api/*`; Artdex's own `/artdex/api/` remains independent. Confirm an opted-out Artdex request returns 204 without creating a count, a malformed request returns 400, and the report still rejects unauthenticated access.

For an application rollback, publish the previous worker and Artdex client versions while retaining the expanded database table. The previous worker remains compatible with it and all newly collected counts survive. Keep `metrics_daily_pre_artdex` and the export until the update is verified. Do not swap the old snapshot over the active table: that would discard activity collected since migration. Any database recovery should preserve the current table first and merge aggregates, using the private export only when necessary.

Publish the dashboard through the existing manual `metrics-wordpress` GitHub Actions workflow from the reviewed commit. It reuses the existing FTP and `METRICS_REPORT_KEY` secrets; no credentials belong in the Artdex client. The report's 7/30/90-day ranges, 60-second cache, visibility-based refresh and daily read budget are unchanged. The local dashboard's conservative reservation now includes the five possible Artdex rows per day.
