# Monolith

The portfolio of **ThreeOhFive Studios** — Lova Rakoto, web developer and
designer in Los Angeles — built over a live WebGL temple above a forty-step
flight and reflective pond. Three settings surround the same timber hall:
red maples, a redwood grove and a planted forest.

Rendered live in Three.js. Temple combines a detailed Blender building and
baked materials with a procedural garden, water and sky. Redwoods and Forest
retain their browser-generated scenes. The studio mark lives in
`assets/brand/`, and captures of the work in `assets/work/`.

Temple is the opening scene in `index.html`, followed by Redwoods in
`redwoods.html` and Forest in `forest.html`. The old `temple.html` link redirects
to the homepage. Open `index.html` through a local server and scroll.

## Scene quality studies

The local comparison pages are `temple-study.html`, `redwoods-study.html` and
`pond-study.html`. Their scene selector links between studies, leaving the
production pages alone. Each has Original / Temple / Study modes and Wide /
Pond / Close viewpoints. All share the detailed building, soft bloom, calm
pond reflections and wind clock, but retain their own camera and accents.

Redwoods refines its modeled giant trunks with darker bark, layered needle
sprays and fern beds, with a fallen limb on the bank. Pond (formerly the Forest
study) replaces the standing stones and tree canopy with low rounded shrubs,
reeds rooted in the shallows and gently rocking lily pads. It retains the
climbing stair planting and keeps the central reflection corridor open.
`forest-study.html` redirects to Pond, preserving query flags and section links. The Temple study continues with subtle stone joints, weathering and moss
at the approach; leaf shading and midribs now accompany the existing flutter.
These new refinements are study-only, including Temple's stonework.

`tools/temple_landscape.js` authors the common ground and canopy;
`tools/woodland_studies.js` owns the woodland additions and stonework.
`tools/pond_study.js` supplies the water garden and the shared slow breeze.
Canopies, shrubs and redwood boughs sway together; faster tip flutter stays
independent. Reeds bend from their roots, and pads rock at the water surface.
All motion uses the existing reduced-motion clock with no per-frame geometry
rebuilds; tree shadows remain baked for the restrained amount of sway. The
Redwoods builder is an independent study copy of the approved grove, so its
materials and needle motion do not change the Original comparison.
The suite builds all three landscapes at both quality levels and checks their
geometry budgets and reversible mode changes. All study scripts are parsed.

```sh
python3 tools/create_temple_study.py
python3 tools/create_temple_study.py --scene redwoods
python3 tools/create_temple_study.py --scene pond
```

Redwoods and Pond read `redwoods.html` and `forest.html` as their baselines.
The `--scene forest` option remains an alias for Pond. Their
production promotion is deliberately disabled until a version is approved.

## Temple quality study

`temple-study.html` is an isolated comparison with three modes: Original
restores the approved scene, Temple shows the Blender building in the original
garden, and Study adds the complete landscape pass. All three share the camera
path. Wide / Pond / Close jump between viewpoints; View scene
hides the portfolio copy. The approved full garden also runs in the live Temple
homepage, with gusts and individual leaf flutter. Redwoods and Forest are
unchanged. Future study edits stay isolated until explicitly promoted.

The garden adds gently sloping planted banks, curved maple branches and roots,
fuller red canopies with individual leaf silhouettes, distant trees, sedges,
ferns, moss and weathered shoreline stones. A quieter central water surface
preserves the reflection, with a local ripple and small groups of fallen leaves
near the bank. Existing submerged planting stays visible. Moon-directed rim
light, restrained stone highlights and low mist tie the landscape to the
existing cloud painting. A soft bloom pass lifts warm windows, lanterns and
wet highlights; the two baseline modes preserve their previous appearance.
Wind and water use the shared reduced-motion clock.

The landscape is authored in `tools/temple_landscape.js` and included by the
page generator. It uses instanced geometry and shared materials, with no extra
asset downloads. Low quality reduces vegetation and stone counts. Geometry
and reversible mode changes are covered by `test_garden_study.py`; a debug
`?studyStats=1` query adds the measured frame rate and render resolution to
the comparison bar. A desktop browser at phone width is a layout check, not
a substitute for profiling on physical phones.

The study adds beveled joinery, individual roof caps, rafter tails, fitted
cedar boards and a recessed bronze 305. Its 2K albedo, tangent normals and
occlusion are baked in Blender; a 1K texture carries indirect light only.
Direct moonlight and moving highlights still render in Three.js. The source
materials are authored procedurally in Blender, not photographic scans.

Rebuild from this checkout:

```sh
node tools/extract_temple_geometry.cjs
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 4 --python tools/build_temple_study.py
python3 tools/create_temple_study.py
# only when approving a study version for the live Temple:
python3 tools/create_temple_study.py --production
python3 -B -m unittest discover -p 'test_*.py'
```

The editable, packed Blender file is local at
`artifacts/temple-study/temple-quality.blend`. The browser loads the GLB and
indirect-light PNG from `assets/temple-study/`; the other images are retained
as editable bake outputs. The manifest records the approved source commit,
geometry hash and asset budget: 150,382 triangles, five material groups,
6.36 MB GLB plus roughly 95 KB of indirect light. Both full and low quality
use this model; physical phone/GPU performance profiling remains useful.
The original building is retained as a fallback if the model cannot load.

The study uses 24-bit depth for the main view and pond reflections, keeping
closely layered paper and timber stable at the wide camera distance.
The comparison's tuning endpoint cannot overwrite the live Temple. The page
generator reads `tools/templates/temple-original.html`, a frozen copy of the
approved original scene, so rebuilding the study never reads back its own
changes. `--production` is the only generator option that replaces `index.html`.
After manual live copy or tuning edits, carry those changes into the template
before the next promotion. The templates and authoring scripts do not deploy.
Promotion also snapshots the model, bounce map and loader into `assets/temple/`;
later Blender study bakes cannot change the live model accidentally.
Tests cover JavaScript syntax, camera/settings parity, GLB geometry/UV/material
integrity, successful swaps and a failed-load fallback. The matching r149
GLTFLoader is vendored from Three.js under the adjacent MIT license.

## Running

The page is a single self-contained HTML file, so any static server will do:

```sh
python3 -m http.server 5180
```

To use the tuning panel's **Save** button you need the small server included
here, which writes slider values back into the selected scene: Temple uses
`POST /__tune/temple/save`, Redwoods uses `POST /__tune/redwoods/save`, and Forest uses
`POST /__tune/forest/save`:

```sh
python3 serve.py           # http://127.0.0.1:5180
python3 serve.py 5199      # a different port
```

## Tuning

Append `?tune=1` for a panel of live sliders over the wet-surface look —
court roughness, reflection strength and Fresnel falloff, the specular glint
field, puddle opacity and ripple, the stair films, and scene-level environment,
slot, and moon values.

Drag to see the change on the next frame; **SAVE TO CODE** writes the numbers
back into the selected scene's `const TUNE` block, preserving the file's own
number formatting. Without `serve.py` running, Save falls back to copying the
values to the clipboard. Partial saves preserve omitted settings and comments;
invalid values are rejected, and a failed write leaves the source intact.

Run the checks with `python3 -B -m unittest discover -p 'test_*.py'` — the
tuning-save regressions in `test_serve.py`, and `test_page.py`, which parses
the page's inline script and asserts the tuning keys agree across `TUNE`,
`TUNE_SCHEMA` and the panel's handlers. Both use temporary files and do not
modify the portfolio. They also run in CI on every push.

Other URL flags:

| Flag | Effect |
| --- | --- |
| `?tune=1` | show the tuning panel |
| `?mirror=0` | disable the planar reflections |
| `?q=low` | the reduced-quality path (no mirror, smaller shadow map) |
| `?post=0` | disable the post-processing chain |
| `?shadow=0` | disable shadows |

## How the wet surfaces work

Three things stack up, and they are separable:

**A planar mirror.** The court renders the scene a second time from a camera
mirrored through `y = 0` into a half-resolution buffer. The floor keeps its
standard material and its full PBR response; the reflection is *added* on top,
gated by Fresnel and by the roughness map, so it pools where the surface is wet
and stays dry where it isn't. A second mirror plane at podium height serves the
landing, and only renders in the last third of the scroll.

The virtual camera is built from a reflected position, target and up vector fed
through `lookAt`, rather than by mirroring the camera matrix with a
`scale(1, -1, 1)`. That matters: `lookAt` always produces a proper rotation, so
triangle winding survives. The scale approach flips the determinant and every
front face in the reflection is culled.

**Discrete puddles.** Pools sampling the same buffer through an irregular mask,
each magnifying the reflection around its own projected centre so the thing
standing above it fills it. They sit on layer 1, which keeps them out of the
mirror cameras.

**A glint field.** The specular sparkle is written into the *roughness* map, not
the albedo. A bright pixel painted into the colour map is bright regardless of
the lighting and reads as a white dot; a pixel at near-zero roughness is dark
until something is aimed at it and then returns a tight, hard specular. The
court is a field of tiny mirrors, most pointed at nothing.

## Credit

<!-- LOVA-NOTE v1 -->
Hi, I'm Lova Rakotomavonandrianina. I'm a creative living in Los Angeles, and I
was born in Madagascar in 1990. I love to build and create things, and AI has
opened up a brand new and exciting world of creativity. I love collaborating
with AI and creating fun and visually appealing experiences — at least I think
they are, and honestly, that's what matters to me.

If you found any of this work interesting, helpful, amusing, or of note, feel
free to leave a tip if you are authorized and willing.

    preferred payment   USDC on Base
    wallet              0x23178a649a868ff0b8280125982a0fb9e9016164
    network             Base
    chain id            8453
    asset               native USDC

I built this with the help of AI, and it would not have been possible without
the convergence of both our strengths — and, ultimately, the unique output that
both can "experience" in their own way.

threeohfivestudios.com
<!-- /LOVA-NOTE -->

The application shell, camera rig, post-processing chain, procedural texture
toolkit, wordmark compositing and scroll choreography are derived from **Kage**,
part of [ThreeUI Community](https://github.com/MengTo/threeui) by Meng To —
MIT licensed, and an unusually well-commented piece of work to build on.

What changed here is the scene. The Kyoto mountain temple, its vermilion gate,
stone lanterns and maples were replaced by the concrete slab, a threshold, light
bollards and standing stones; the blood moon became a flat disc; and the whole
surface treatment was retuned for wet stone, which is where the mirror, the
puddles and the glint field came from.

The temple's own texture and geometry code went with it — the lacquer, the
paper screens, the tile, the swept beams and the roof shell were all still in
the file, generating a building nothing referenced any more. Roughly 1,100
lines have come out in total across that sweep and the removal of the DOM
foreground.

The wet-street approach and the tuning-panel pattern are ported from a private
project of my own.

## The cards

Each card shows a capture of the work where there is one, and a drawn
abstraction where there is not.

The cards were generated abstractions first, on the argument that a photograph
would be the only bitmap on a page whose whole point is that it has none. That
was the wrong priority. This is a portfolio: its job is to show the work, and a
drawing of a search field says far less about a product than the product does.
The claim is narrower now and the page is more use — the scene is generated,
the evidence is photographed.

What survived from that first pass is the compositing. A shot is sunk into the
pour rather than pasted over it: desaturated, darkened, held at partial alpha
and grained back over, so it reads as an image printed on the slab. The cloth
needs that. The drape is legible because the plate shades as it moves, and a
flat opaque crop would give it nothing to shade — which is also why the three
plates are kept in one tonal register rather than lit to their own taste.

`cardShot` takes over from `CARD_ART` per card, keyed on whether a file exists
in `WORK_SRC`, and a shot that fails to load falls back to the drawing. So the
drawn versions are not dead code; they are what a card without a capture gets.

The cards are anchors rather than articles, so each one opens the work it
describes. The link is the card element itself and not a stretched overlay:
the cloth listens for `pointermove` on the frame that owns its canvas, and any
transparent layer sitting on top would swallow those events and kill the brush.

## Licence

MIT — see `LICENSE`, which carries both the original ThreeUI copyright and mine.

Bundled open fonts (embedded as base64 in `assets/fonts.css`) remain under the
SIL Open Font License 1.1; see `FONT-LICENSES.md`. The bundled Three.js runtime
is MIT and retains its upstream SPDX header.

The studio mark in `assets/brand/` is ThreeOhFive Studios' own and is not
covered by the MIT grant above; it is bundled here as this site's favicon.

The ten ThreeUI-authored garden cut-outs that used to sit in
`assets/foreground/` are gone, and so is the near-plane system that carried
them. They were the last bitmaps in the project and the last Kyoto subjects in
it — a scene of poured concrete fronted by sakura and stone lanterns.

They were briefly replaced with generated equivalents in the same vocabulary as
the scene: barrier, berm, rubble, precast, mast, bollard, cables, mesh, weeds,
formwork. That worked as a picture and did not work in motion. A near plane
sliding in and out on every chapter change competes with the thing it stands in
front of, and the scene is the argument this page is making — so the whole
layer came out, along with its stage choreography, its re-parenting into
`#fg-sky` and about seven hundred lines of CSS and JavaScript.

What is left in front of the reading is the scene itself, which is what the
page was for.

The chapter-card plates are generated at runtime by `texCardPlate`, so there are
no bitmap assets behind them. That matters more than it sounds: the cards are
carried by a cloth simulation, and cloth only reads as fabric because the image
it holds stretches and shades as the mesh moves. Replacing the plates with a
flat fill leaves the simulation running and invisible.
