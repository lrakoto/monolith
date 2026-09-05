# Working in this repo

One page, no build step. `index.html` is ~320KB and contains the markup, the
CSS and the whole Three.js scene in a single inline `<script>`. `serve.py` is a
static server plus the tuning panel's save endpoint. `assets/three.min.js` is
vendored (r149).

More than one agent works here, one at a time. The tree can move between your
turns — run `git log --oneline -5` before assuming anything, and re-read the
region you are about to change instead of editing from remembered line numbers.

## Verify before you claim it works

```sh
python3 -B -m unittest discover -p 'test_*.py'
```

That is the whole suite: `test_serve.py` covers the tuning save endpoint,
`test_page.py` parses the inline script with `node --check` and asserts the
tuning keys line up across their three homes. It runs in under a second and in
CI on every push. Run it after any edit; a broken `index.html` is otherwise
silent until the preloader hangs.

Prefer anchored, asserted edits (match an exact string, assert it occurs once)
over line-numbered or blind replacement. One bad `sed` on this file is the
whole site.

## Running it

`python3 serve.py [port]` — default `http://127.0.0.1:5180/`. It is often
already running; reload the page rather than restarting the server. Changes to
`index.html` need no build, just a refresh.

URL flags: `?tune=1` opens the tuning panel, `?driver=timer` swaps the frame
loop from rAF to `setTimeout`.

## The tuning panel

Adding a slider means touching **three** places that must agree on the same
key, and nothing warns you if they drift:

1. `const TUNE` — the value, and the decimal style the file writes back
2. `const TUNE_SCHEMA` — label, min, max, step, group (display order; keep a
   group's rows contiguous or the header repeats)
3. the handlers object in `initTuning()` — omit it if the value is read every
   frame; supply one if it has to be pushed at a uniform or rebaked

`test_page.py` asserts all three agree, so a drift fails the suite rather than
producing a slider that reads `undefined`.

**SAVE TO CODE** posts to `serve.py`, which substitutes the literals in place.
It deliberately leaves keys it was not sent alone — an earlier version rebuilt
the block and silently deleted any key a stale browser tab did not know about.
Do not "simplify" it back.

## Browser automation gotcha

The page stops its own frame loop when the tab is hidden
(`if (document.hidden) running = false`), and Chrome throttles background tabs
to ~1fps regardless. Driving it from an automation tool that renders offscreen
gives stale frames and settled-looking screenshots that are nothing of the
kind — check `document.hidden` before trusting anything you measure.

For camera and layout questions you can skip the browser entirely: load
`assets/three.min.js` in Node, rebuild the `CAM` curve, and compute the pose
directly. That is exact and takes no waiting.

## Conventions

Comments here carry the *why* — what was tried, what broke, why a number is
that number. Match that register; do not restate what the code says. Keep the
existing voice (lowercase, unhyphenated, no bullet lists inside code comments).

## Open

`index.html` has social-preview tags but no domain yet, so `og:url` is absent
and the image paths are relative. Grep `SITE-URL` — three lines to change once
the page is deployed.
