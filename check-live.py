#!/usr/bin/env python3
"""Is what is live what is in git?

The repo and the host are two separate things: a push updates GitHub, not the
site. This answers the one question that gap creates — has someone edited and
forgotten to upload — without needing any credentials.

A byte compare would always fail, because the page is rewritten in flight:
Cloudflare obfuscates mailto: links and injects a decoder, and GoDaddy appends
a traffic-monitoring script. Both are stripped before comparing, so what is
left is genuinely our content.

    python3 check-live.py
"""
import re
import sys
import urllib.request
from pathlib import Path

LIVE = "https://threeohfivestudios.com/portfolio/"
LOCAL = Path(__file__).resolve().parent / "index.html"

INJECTED = [
    # Cloudflare Email Address Obfuscation: the rewritten href and its decoder
    (re.compile(r'href="/cdn-cgi/l/email-protection#[0-9a-f]*"'),
     'href="mailto:lova@threeohfivestudios.com"'),
    (re.compile(r'<script data-cfasync="false" src="/cdn-cgi/scripts/[^"]*"></script>'), ''),
    # Cloudflare Web Analytics beacon, appended before </body>
    (re.compile(r'<script type="module" src="https://static\.cloudflareinsights\.com/beacon\.min\.js[^"]*"[^>]*></script>'), ''),
    # GoDaddy's tccl performance monitor, appended before </html>
    (re.compile(r"<script>'undefined'=== typeof _trfq.*?</script>\s*"
                r"<script src='https://img1\.wsimg\.com/traffic-assets/js/tccl\.min\.js'></script>", re.S), ''),
]


def strip(html):
    for pattern, repl in INJECTED:
        html = pattern.sub(repl, html)
    html = html.replace("\r\n", "\n")
    # Removing an injected script leaves the blank line it sat on, which would
    # offset every line after it — so blank lines are dropped on both sides.
    return "\n".join(l for l in (x.rstrip() for x in html.split("\n")) if l)


def main():
    local = strip(LOCAL.read_text(encoding="utf-8"))
    req = urllib.request.Request(LIVE + "?cachebust=checklive",
                                 headers={"User-Agent": "check-live/1.0",
                                          "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as res:
        live = strip(res.read().decode("utf-8"))

    if local == live:
        print(f"in sync — {LIVE} matches index.html ({len(local):,} bytes compared)")
        return 0

    print(f"OUT OF SYNC — {LIVE} does not match index.html")
    print(f"  local {len(local):,} bytes / live {len(live):,} bytes")
    print("  Upload index.html (cPanel File Manager, tick Overwrite), then purge")
    print("  the Cloudflare cache. See DEPLOY.md.")
    for i, (a, b) in enumerate(zip(local.split("\n"), live.split("\n")), 1):
        if a != b:
            print(f"  first difference, line {i}:\n    local: {a.strip()[:110]}\n    live:  {b.strip()[:110]}")
            break
    return 1


if __name__ == "__main__":
    sys.exit(main())
