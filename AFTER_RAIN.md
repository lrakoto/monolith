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
`cp index.html temple.html forest.html /private/tmp/monolith-after-rain-preview/` and reload.
Copy changed assets there too. This snapshot rejects tuning saves so edits
cannot silently land in the wrong copy. For SAVE TO CODE, run
`python3 serve.py 5186` in this source worktree and use port 5186. Monolith, Temple
and Forest have separate save endpoints and update their own source files.
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


## Temple planting, 305 and the redwood grove

Temple now uses Monolith's lower, broader foreground silhouettes, quiet
winter grass tint and per-layer cursor light response. Its puddle shaders,
positions, wet paving and water values already matched; the lower banks expose
those pools. The second-floor blank plaque now has a recessed timber face,
height-mapped 305 lettering and four separate brass frame bars. It adds no
new light source and leaves the original roof silhouette intact.

Monolith's five standing stones are replaced by a procedural redwood grove.
The trees keep the lateral scatter, with tall tapering trunks, fluted root
flares, broken low limbs, drooping boughs and individual modeled needle sprays.
The nearest branches stay outside the approach. A shared bark atlas carries
vertical fissures and fine fibres; merged wood and instanced foliage keep the
whole grove to two meshes, with 92,180 triangles in high quality and 27,920 in
low quality. Foliage receives light and appears in the reflections; solid wood
casts shadows while fine needles do not add noise to the shadow map.

A narrow band on thin cloud edges now catches cool silver moonlight. Spherical
distance keeps the rim strongest near the moon, with dense cloud interiors
remaining dark. The effect follows moon brightness, and the same sphere drives
the reflected sky. No new texture assets or per-frame cloud work were added.

Validation: the 42-test suite passes, including loopback server checks; real
Three.js geometry checks confirm finite attributes and valid indices in both
grove quality modes. Browser checks cover both desktop scenes and narrow
layouts. Review PNGs are kept under artifacts. The preceding scene checkpoint
is e8832fc; this remains a local study, with no changes to Sol's Blender files.


## Coordinated landscape and material pass

The scene selector now stays within the study: index.html, temple.html and
forest.html. Forest was copied from the main scene-vegetation checkout (page
commit 46afc71), retaining its pond, ferns, broadleaf banks, hanging vines,
stair planting and economical tree batches. The current portfolio UI, games,
shorter role timeline and View scene are carried into it. Its pond-aware
handlers and low-quality reflection safeguards remain, with its own tuning
save endpoint. Main and the published Forest site remain untouched.

All three scenes now share the clearing-storm sky. High quality uses a
4096×2048 background and 16-bit cloud-density field; low quality uses 1024×512.
The broad glow remains baked, with both broad edge terms shaded toward the
moon using the density gradient. An additional HDR pass computes the fine rim
after texture filtering, antialiases it with screen derivatives, and lights
only boundaries whose density falls toward the moon. Two slow waves move the
brightness along that rim. The real planar reflections include the shimmer;
PMREM stays static. Reduced motion freezes the shimmer, redwood needle breeze
and Forest canopy-light drift. Async row batches keep sky generation yielding
to the page, and generation guards still protect against stale resize bakes.

The five near redwoods are roughly 25% larger. Eight simpler background trees
add depth on desktop; the low-quality path retains four of them. The grove
still uses two meshes: merged wood and instanced needle sprays. Its triangle
budget is 115,252 high and 32,328 low. Needle tips bend gently without per-frame
CPU instance updates. The background trees stand at podium level and retain
space around the main building. Forest's existing canopy now casts slowly
drifting dapple through its material shader.

Temple uses local, photographed weathered timber albedo, OpenGL normal and
roughness maps from Poly Haven (CC0; credits in assets/materials/weathered-wood).
A single-board crop serves columns and a stained variant serves the gate;
procedural wood remains a loading fallback. The lit bays gain real timber
returns, roof edges get sparse non-emissive wear, and the existing 305 plaque
stays in place. Lanterns and hall spill are now restrained cream; red moon
lights are replaced by cool moonlight. Maples have taller trunks, spreading
branches and denser rounded leaf clusters. Their breeze also respects reduced
motion. The architecture keeps its original silhouette.

Monolith and Temple boulders use broader irregular erosion, slightly denser
meshes, continuous normals averaged across shared corners, varied mineral
color and matte stone maps. This removes the old triangular facets without
turning them into polished spheres. Forest keeps its planted pond banks.

Validation: 57 tests pass, including three-page syntax/content/tuning checks,
Forest pond behavior with and without reflections, separate save endpoints,
sky continuity, disabled moon, directional edge light and stale bakes. Direct geometry checks cover
both redwood quality modes and shared rock normals. Desktop/narrow browser
review covers all scenes; screenshots remain local review artifacts. This is
still a local study, with no deployment and no Blender changes. 28cd03e preserves
the preceding scene pass.


## Softer sky and engraved studio marks

The cloud treatment returns to 28cd03e, retaining the 4K desktop bake. Only
the extra silver rim is thinner, from density band .18–.56 to .22–.49; the
cloud body and broad glow keep their earlier shading. The later directional
mask and bright filament pass are removed. This also removes their per-frame
sky draw and extra density texture. The async sky safeguards remain.

Redwood trunks are darker with less environment reflection. Both Monolith and
Forest carry a 2.55m-wide, .90m-high 305 just above the slit, shaded as a shallow
cut into the concrete. A front-face mask and view-space height derivatives
retain the underlying concrete; there is no separate plaque. Forest chains its
canopy-light shader and keeps its existing facade mapping.

Temple returns to its original procedural wood and material tints. The growth
rings, knots and splits are finer, and the height relief and normal strengths
are reduced. Red maple foliage returns while keeping the fuller tree geometry.
Shoji paper emits warm interior light with a subtle edge falloff; exterior
lanterns retain their restrained cream light. Photographic wood assets remain
archived but are no longer loaded.

Validation: 56 tests pass after removing the intentionally reverted directional
edge-light assertion. Desktop previews check both engraved facades, Temple's
wood and windows, and all three shared skies. This remains a local study.


## Shared pond and warmer Temple

Monolith and Temple now use Forest's continuous pond, including the sloping
basin, submerged stone bed, clear shallow edges, fine ripples and undistorted
scene reflection. The upper landing pools stay in place. All three share the
same pond construction and tuning behavior. Low quality retains one smaller
reflection updated every other frame; resizing skips the unused landing
reflection target.

Temple's maple foliage is a richer red, with less cool environment wash. The
hall's boards and posts return toward brown through warmer material tints and
a lighter brown albedo that remains visible under moonlight. The restored fine
procedural grain, shallow relief and warm windows remain.

The shared sky keeps the previous cloud shapes and broad backlight. Its extra
silver rim is narrower again (.275–.395 density) and roughly twice as bright,
with the same soft falloff around the moon. A stronger trial read as an outline
on desktop, so the final gain is restrained to 65/73/84.

Validation: 58 tests pass, including the full local server checks and pond
shader behavior with and without reflections on all three pages. Desktop
review covers Monolith's pond and Temple's leaves, timber, water and sky;
Temple also loads without errors in a narrow low-quality viewport and after
rotation. The preview remains on port 5193. This is a local study.
