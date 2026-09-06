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
