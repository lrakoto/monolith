# Where this page lives, and how to take it back

Deployed 2026-09-05 to **https://threeohfivestudios.com/portfolio/**

## The host

`threeohfivestudios.com` is an **addon domain** on the GoDaddy cPanel account
whose main domain is `pixelmix.co` (Deluxe plan) — not a hosting account of its
own, which is why it does not appear under Web Hosting in the GoDaddy products
list. Cloudflare sits in front of it. The WordPress + Elementor site is the
document root; this page is a plain static folder inside it.

```
/public_html/threeohfivestudios.com/            WordPress (Elementor)
/public_html/threeohfivestudios.com/portfolio/  this page
```

Nothing here touches WordPress. Its own `.htaccess` sends unmatched requests to
`index.php` only when the path is not a real file or directory
(`RewriteCond %{REQUEST_FILENAME} !-d`), so a real `/portfolio/` directory is
served straight off disk with no rule of its own.

## Publishing an update

The whole site is `index.html` plus `assets/`. Upload over the top — cPanel
File Manager, tick **Overwrite existing files**. Usually only `index.html`
changes, and it is one 336KB file.

**Purge the Cloudflare cache afterwards** or the old file lingers.

Then confirm it landed:

```sh
python3 check-live.py
```

That fetches the live page and compares it to `index.html`. A byte compare
would always fail — the page is rewritten in flight, so the script strips what
the infrastructure adds before comparing:

| Injected by | What |
|---|---|
| Cloudflare | rewrites `mailto:` to `/cdn-cgi/l/email-protection#…` + a decoder script |
| Cloudflare | Web Analytics beacon before `</body>` |
| GoDaddy | `tccl.min.js` traffic monitor before `</html>` |

Worth knowing that the first one means **the contact mailto needs JavaScript**
to resolve. Cloudflare → Scrape Shield → Email Address Obfuscation turns it off
if you would rather have the plain link.

It is not in CI on purpose: CI must not fail because a host had a bad minute,
and a check that goes red for reasons outside the code gets ignored.

## Automatic deploy

`.github/workflows/deploy.yml` publishes on every push to `main`: it runs the
test suite first, then FTPs the site into
`/public_html/threeohfivestudios.com/portfolio/`.

It needs four repository secrets — **Settings → Secrets and variables →
Actions → New repository secret**. Nobody but you should add these; they are
not something to paste into a chat or a file.

| Secret | Value |
|---|---|
| `FTP_SERVER` | `p3plzcpnl506867.prod.phx3.secureserver.net` — see below, this one is not obvious |
| `FTP_USERNAME` | the FTP account's user |
| `FTP_PASSWORD` | its password |
| `CF_ZONE_ID` | *optional* — Cloudflare zone id, to purge the cache after deploy |
| `CF_API_TOKEN` | *optional* — a Cloudflare token with **Zone → Cache Purge** only |

Without the two Cloudflare secrets the purge step skips and the deploy still
succeeds; the cache just ages out on its own.

**`FTP_SERVER` must be the server's own hostname, not the domain.** Both
`threeohfivestudios.com` and `ftp.threeohfivestudios.com` resolve to Cloudflare
(`104.21.x` / `172.67.x`), and Cloudflare proxies HTTP and HTTPS only — port 21
is not carried, so an FTP client aimed there hangs until it times out. The
error is `connect ETIMEDOUT <cloudflare ip>:21` and it looks like a credentials
problem, which it is not. `ftp.pixelmix.co` does not resolve at all.

The address that works is the cPanel host itself, which is in the URL when you
open cPanel: `p3plzcpnl506867.prod.phx3.secureserver.net` → `107.180.115.245`,
port 21 open. Prefer the hostname over the IP; GoDaddy moves accounts between
servers and the hostname follows.

**The setting to check before the first run is `server-dir`**, because it is
relative to wherever the FTP account lands, and that differs per account on
this host:

| FTP account | Lands at | `server-dir` must be |
|---|---|---|
| `hermes@pixelmix.co` *(in use)* | `/home/cb7kn7l8ecwu/public_html` | `/threeohfivestudios.com/portfolio/` |
| `cb7kn7l8ecwu` (main cPanel) | `/home/cb7kn7l8ecwu` | `/public_html/threeohfivestudios.com/portfolio/` |

The account in use is scoped inside `public_html`, so `public_html` must **not**
appear in the path — with it, the deploy resolves to `public_html/public_html/…`
and fails. If the credentials ever change, check this line against them.

One level too high in the other direction would sync the repo over the
WordPress root. The first deploy is worth watching in the Actions tab rather
than assuming.

The workflow excludes `*.py`, `*.md`, `.github/` and `.git*` — `serve.py` most
of all, which has an endpoint that writes to `index.html`.

Note what this changes about access: anyone who can push to `main` can now
reach the host. That is the trade a push-to-deploy makes.

Never upload `serve.py`, `test_*.py`, `AGENTS.md`, `CLAUDE.md` or `.github/`.
`serve.py` has an endpoint that writes to `index.html`; it is a local dev tool
and has no business on a public host.

## The homepage redirect  ← the thing to undo first

The site root currently **302s to `/portfolio/`**. That is a block in
`/public_html/threeohfivestudios.com/.htaccess`, between the Cloudflare HTTPS
block and `# BEGIN WordPress`:

```apache
# BEGIN Portfolio redirect
... comments ...
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{QUERY_STRING} !(^|&)home=1(&|$)
RewriteRule ^$ /portfolio/ [R=302,L]
</IfModule>
# END Portfolio redirect
```

**To revert:** delete that block, `# BEGIN` through `# END`. Nothing else moves.
A byte-exact copy of the original file is on the server beside it as
`htaccess-backup-2026-09-05.txt` (606 bytes).

Three deliberate choices in it:

- **302, not 301.** A permanent redirect is cached hard by browsers and is
  miserable to take back. This is on trial, so it stays temporary.
- **`^$` matches only the root**, so `/design/`, `/wp-admin/`, the media
  library and `/portfolio/` itself are untouched — and it cannot loop, because
  `/portfolio/` is not an empty path.
- **`?home=1` skips the redirect**, so the WordPress homepage stays reachable
  at `https://threeohfivestudios.com/?home=1` while the redirect is up.

Verified at deploy: `/` 302s; `/portfolio/`, `/design/` and the résumé PDF all
200; `/wp-admin/` still redirects to wp-login; `/?home=1` still serves the
Elementor homepage.

## Coupling worth knowing

The contact chapter's résumé button points at
`/wp-content/uploads/2026/03/Lova_Resume_2026.pdf` — the copy in WordPress's
media library, because that is where it is actually replaced. It is the same
origin, so it needs no CORS and no duplicate. If WordPress ever moves off this
domain, that link goes with it.
