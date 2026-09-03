# Monolith

The portfolio of **ThreeOhFive Studios** — Lova Rakoto, web developer and
designer in Los Angeles — built over a single-page WebGL scene: a board-formed
concrete slab standing at the head of a forty-step flight, with one horizontal
slot of light cut through it.

Rendered live in Three.js. Every piece of geometry and every texture *in the
scene* is generated in JavaScript at load — no model files, no image assets.
The exceptions are deliberate and both live outside the scene: the studio mark
in `assets/brand/`, and captures of the work in `assets/work/`.

Open `index.html` through a local server and scroll.

## Running

The page is a single self-contained HTML file, so any static server will do:

```sh
python3 -m http.server 5180
```

To use the tuning panel's **Save** button you need the small server included
here, which adds one route (`POST /__tune/save`) that writes slider values back
into the source:

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
back into the `const TUNE` block in `index.html`, preserving the file's own
number formatting. Without `serve.py` running, Save falls back to copying the
values to the clipboard.

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
