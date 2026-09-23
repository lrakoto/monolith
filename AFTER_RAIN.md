# Monolith — After Rain study

Local iteration, 2026-09-22. Branch `codex/monolith-after-rain`, based on
`origin/main` at `177352b`. This separate worktree is
`/Users/victoriarajaonarivony/Documents/monolith/.worktrees/monolith-after-rain`.
The Forest checkout and Sol's external-drive Blender study were not edited.

## Preview

The current preview is <http://127.0.0.1:5193/>. It serves a local snapshot
from `/private/tmp/monolith-after-rain-preview`, managed by the temporary
macOS job `local.codex.monolith-after-rain-5193`. The earlier command-launched
servers disappeared between task turns, including a detached process.
An independent job cannot read the Documents folder under the current macOS
permissions, so the website files are copied into that temporary directory.
No login item or permanent LaunchAgent was installed.

After editing the page, refresh the snapshot with
`cp index.html temple.html /private/tmp/monolith-after-rain-preview/` and reload.
Copy changed assets there too. This snapshot rejects tuning saves so edits
cannot silently land in the wrong copy. For SAVE TO CODE, run
`python3 serve.py 5186` in this source worktree and use port 5186. Monolith
and Temple have separate save endpoints and update their own source files.
Stop the snapshot server with
`launchctl remove local.codex.monolith-after-rain-5193`.

`after-rain-baseline.html` is a local, ignored copy of the starting page; it
uses the same assets and can be opened on the source server for comparison.
The baseline and screenshots are not included in a clone; the source baseline
is available from commit `177352b`.

## Retained first pass

The main slab is now one continuous beveled extrusion around its opening.
The body keeps its original dimensions, lean and slot location. The emitter
was already deeply recessed, so its depth stays unchanged to preserve the
light from the low stair cameras. Softer brightness across the emitter,
shadowed reveals, smaller steel edges and a thinner beveled coping make
that depth more legible.

A dedicated procedural concrete atlas adds fine timber grain, sparse pores,
formwork marks, faint pour lines and dampness at the base. The facade and
reveals share their texture allocations. The atlas is 1024 by 2048 pixels,
halved in each dimension on the low-quality path. UVs are tied to object
coordinates, and capped to keep the dry coping from wrapping into the damp
foot of the texture. The surface stays intentionally restrained at distance.

The hero camera steps back slightly and looks higher so the coping clears
the navigation at ordinary desktop sizes. The moon is smaller and dimmer;
the directional key now crosses the architecture, with its shadow bounds
expanded to include the slab. Rain is quieter, foreground planting opens
onto more wet ground, and the exposed rocks have a rougher surface.

Featured project images lose two redundant dark overlays while retaining
one label scrim and their existing cloth simulation. A persistent View scene
button hides the portfolio without changing its scroll layout, disables its
hidden controls, and pauses the cloth renders. Escape returns to the page.
The narrow header now fits the menu and an accessible resume icon.

## Validation

- `python3 -B -m unittest discover -p 'test_*.py'`: 24 tests pass.
- `git diff --check`: clean.
- Vendored Three.js r149 geometry check: slab bounds remain
  12.6 by 19.4 by 3.7, 288 vertices, finite UVs and valid material groups.
- Browser review: hero, work and close facade views; AutoDex details still open.
- Layout checks at 1280 by 720, 390 by 844 and 320 by 740.
- Low-quality scene, menu-to-scene transition, Escape/focus return and
  no-WebGL fallback checked. These are browser viewport checks, not a
  physical-device performance benchmark.
- Browser visibility checked before visual review; no headless frame claims.

Local PNGs are in `artifacts/`: hero, facade detail, featured work and mobile.
These are review captures, not website assets. Nothing was deployed.

Further iterations should compare the same views and preserve this pass as
a checkpoint. The optional asymmetric facade setback has not been added.

## Preview connection fix

The single-request development server could wait indefinitely on a browser
connection that had not yet sent an HTTP request, blocking every later page
load. It now uses ThreadingHTTPServer with a 15-second per-connection timeout.
Tuning saves are serialized across the full read/modify/replace transaction
so concurrent partial saves preserve one another. The loopback bind remains.
A regression opens an idle connection first, then verifies a separate page
request succeeds. The corrected server was restarted on port 5186, and the
page was reloaded and visually checked in the in-app browser.

## Pacing and planting follow-up

The 3D experience chapter is 1400vh instead of 1600vh, shortening the scroll
by 12.5% while retaining all seven role stops and the existing dwell rhythm.
The three grass silhouettes have lower peaks and broader shoulders, giving
the foreground more gradual slopes without increasing geometry or draw calls.

The clearing-storm sky is now implemented in Monolith. A spherical painting
contains the cloud opening, sparse stars and a smaller partly veiled moon;
the same texture drives both the visible background and PMREM reflections.
The broad cloud light follows the key-light direction. It is generated once,
in short asynchronous batches so the loader can keep responding. Resizes and
moon tuning debounce a new bake; stale results cannot replace the latest sky.
The high/low paths use 2048 by 1024 and 1024 by 512 textures. No extra per-frame
cloud passes or image downloads were added. Courtyard particles are quieter.

## Temple restoration

`temple.html` restores the original Kage procedural architecture, vermilion
torii, stone lanterns, maple trees, falling leaves, foreground and blood moon.
The recovered source is `public/landing-pages/kage.html` from MengTo/threeui,
commit `326580429881c2abe7893bee53c62cbb31b6ee49`, blob
`9f96c15b52a140e386a40c0178723f17ab7d8a13`, also present locally in the threeui
checkout. The shared MIT license retains Meng To's copyright. No reference
artwork was substituted for the procedural scene, and no new bitmap assets
are needed.

This is the original scene restored into the current portfolio, not an old
copy of the portfolio itself. Work content, games, accessible navigation,
View scene, the shorter seven-role timeline and wet-ground improvements remain.
The original six-waypoint Kage camera cannot drive the current seven chapters,
so the current route stays, with Kage's original hero pose. Original material
colors and warm lighting are retained; the reflected moon is also warm.
The Lova note in README remains unchanged.

The selector links Monolith and Temple locally; Forest retains its existing
published URL. Nothing has been pushed or deployed. `d91a56f` preserves the
previous After Rain scene before this sky/restoration pass.

Validation now covers both pages' script syntax, tuning keys, project cards
and machine-readable content; independent tuning-save destinations; sky seam
continuity, moon-off behavior and stale asynchronous bakes. The suite has 42
passing tests. Desktop and narrow-view browser checks include both scenes,
with screenshot artifacts kept locally under `artifacts/`.
