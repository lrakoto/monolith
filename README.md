# Monolith

A single-page WebGL scene: a board-formed concrete slab standing at the head of
a forty-step flight, with one horizontal slot of light cut through it. Rendered
live in Three.js — every piece of geometry and every texture in the scene is
generated in JavaScript at load. There are no model files and no image assets
for the 3D scene at all.

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

The wet-street approach and the tuning-panel pattern are ported from a private
project of my own.

## Licence

MIT — see `LICENSE`, which carries both the original ThreeUI copyright and mine.

Bundled open fonts (embedded as base64 in `assets/fonts.css`) remain under the
SIL Open Font License 1.1; see `FONT-LICENSES.md`. The bundled Three.js runtime
is MIT and retains its upstream SPDX header.

The imagery in `assets/generated/` and `assets/foreground/` is ThreeUI-authored
and MIT licensed. The `assets/generated/` files are still the original Kage
chapter renders and do not match this scene — replacing them is outstanding.
