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
