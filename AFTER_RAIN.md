# Monolith — After Rain study

Local iteration, 2026-09-22. Branch `codex/monolith-after-rain`, based on
`origin/main` at `177352b`. This separate worktree is
`/Users/victoriarajaonarivony/Documents/monolith/.worktrees/monolith-after-rain`.
The Forest checkout and Sol's external-drive Blender study were not edited.

## Preview

Run `python3 serve.py 5186` here, then open <http://127.0.0.1:5186/>.
The current session already has that server running. No build is needed.
`after-rain-baseline.html` is a local, ignored copy of the starting page; it
uses the same assets. It can be reopened at
<http://127.0.0.1:5186/after-rain-baseline.html> for comparison.
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
