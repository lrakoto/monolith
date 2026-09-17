# Cathedral offline render

This is the first complete Blender rendering study, separate from the interactive website scene. Nothing in this folder is wired into the live site.

- `cathedral-still.png`: square reference composition, 1000 × 1000, Cycles, 64 samples with denoising.
- `cathedral-cinematic.blend`: editable geometry, materials, lighting, atmosphere, and reference camera. No external image textures are required.
- `../tools/render_cathedral.py`: reproducible scene builder. It loads the source meshes from `../assets/cathedral/cathedral-trunks.blend`.

Rebuild from the checkout root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 8 --python tools/render_cathedral.py
```

The builder uses CPU rendering because the current host stalled waiting for Metal kernels. The image establishes composition and lighting; an animated camera and browser playback have not been implemented.

## Scale study

`cathedral-scale-study.png` and `cathedral-scale-study.blend` preserve the next composition separately. Rebuild with `tools/render_cathedral_scale.py` using the command above.

The monument is 2.2 times the previous size and sits 275 scene units from the camera instead of 155. The stair approach grows from 96 to 210 units, with narrower treads and a smaller doorway and inscription. Camera height drops from 3 to 1.15 units; the lens widens from 40 to 34 mm. Additional forest layers extend into the distance. This is a scale and composition study, before the detailed realism pass.

## Reference proportions pass

`cathedral-proportions.png` and `cathedral-proportions.blend` are a separate camera/composition pass. Rebuild with `tools/render_cathedral_proportions.py`.

The reference was rechecked directly. Its monument base sits near 53% of image height and the stair foot near 89%; the revised camera targets those landmarks. The camera is at (0, -92, 10), aimed at (0, 228, 111), with a 34 mm lens. The monument base rises to 100 units; its silhouette is 191 units tall. The approach uses 150 steps, each 0.667 units tall and 1.4 deep, across a width of 28 tapering to 24. The inscription is enlarged to fit the facade, and overlapping forest crowns replace the dominant foreground trunks. This remains a composition study; surface realism and animation are later work.

## Forest realism pass

`cathedral-forest.png` and `cathedral-forest.blend` retain the approved camera, stair dimensions, and monument silhouette. Rebuild using `tools/render_cathedral_forest.py`.

The smooth canopy placeholders are replaced by shared meshes of branching stems and individual leaves. Dense planting follows both banks; layered crowns partially conceal the more distant trunks. Soft foreground daylight separates the banks and pond from the misty background. The inscription is recessed into the monument and the stone has faint vertical mineral variation. This remains an offline still, with no website integration or animation.

## Forest-covered landforms

`cathedral-landforms.png` and `cathedral-landforms.blend` replace the exposed trunk stands with asymmetric hills and steep banks. Rebuild using `tools/render_cathedral_landforms.py`.

Four unequal ridge profiles shape the valley, with erosion noise, moss on gentler surfaces, occasional exposed rock on steep faces, and foliage positioned against the actual terrain elevation. The camera, monument and stairs remain fixed. This is a silhouette and landscape study; it does not change the website.

## Landscape-scale canopy and distance

`cathedral-landscape-scale.png` and `cathedral-landscape-scale.blend` retain the established framing and primary terrain silhouettes. Rebuild using `tools/render_cathedral_landscape_scale.py`.

Small, full tree crowns replace the large individual plant patches; sampling density increases on steeper slopes. Finer terrain and concrete grain support the scale. Three separate distant ridges extend behind the monument into a larger atmospheric volume. The camera clipping distance is extended to include them; camera position, lens, monument and stairs are unchanged. All earlier studies remain available.

The final landscape-scale still is rendered at 1600 × 1600 with 96 Cycles samples and denoising. The canopy crowns overlap densely; the experimental continuous lower-canopy mesh remains editable but is hidden from the final render.

## Ridge, lighting, and pond refinement

`cathedral-ridges.png` and `cathedral-ridges.blend` add offset shoulders, eroded pockets, spatially varying canopy stands, a planted pond edge, cooler haze, and selective canopy lighting. The main architecture and camera remain fixed. Rebuild using `tools/render_cathedral_ridges.py`; append `-- --draft` for the separate 1000px draft output. The normal render is 1600px with 96 samples.

## Distant camera and two giant trunks

`cathedral-distance-study.png` and `cathedral-distance-study.blend` reset the composition with two enormous trunks and simple clustered canopy volumes. Rebuild with `tools/render_cathedral_distance.py`. Individual leaves and the continuous cliff walls are omitted while judging scale.

The camera is at (0, -720, 108), with a 35.518 mm lens and an upward tilt of 0.226 radians. The tower facade is about 1,710 metres away horizontally, with a 900 metre silhouette above a 450 metre stair ascent. Stair width tapers from 174 to 141 metres. Ordinary crown widths are roughly 30–72 metres, dwarfed by both monument and trunks. This is deliberately a fantasy scale. The builder verifies projected tower top, tower base, and stair foot against the reference at 8%, 53%, and 89% from the image top.

This is a 1000px, 48 sample Cycles composition study, with simplified materials and foliage. Earlier detailed renders remain intact; the website is unchanged by this pass.

## Forest depth composition study

`cathedral-depth-study.png` and `cathedral-depth-study.blend` continue the simplified study with the same camera, tower, and stair geometry. Rebuild with `tools/render_cathedral_depth.py`.

Four offset bank shoulders and varied crown heights replace the even forest ramp. The two main trunks are partially buried and have gentle bends and uneven ribs. Selected planting groups overlap the stair margins. Broader background trunks and simple crowns extend the forest behind the monument; depth-dependent haze and muted background materials merge those silhouettes into receding layers. The atmosphere extends beyond the visible framing to avoid a hard boundary across the sky.

The foliage remains simple clustered meshes, with no individual leaves. The render is 1000px at 48 Cycles samples. Projection checks preserve the previous top/base/foot framing; the prior distance study is retained separately. No website integration or deployment is included.

## Trunk silhouettes and shoreline

`cathedral-silhouette-study.png` and `cathedral-silhouette-study.blend` continue the simplified composition. Rebuild with `tools/render_cathedral_silhouettes.py`.

The two principal trunks have more irregular ribs and contours. Background stems now bend and vary in width independently, breaking up their parallel outlines. Terrain noise tapers away at the pond, removing shallow isolated patches; smaller shoreline planting groups soften the banks. Water reflections are rougher, the pond receives slightly more light, and lily pads are a little larger. Camera, tower, stairs, and the broad forest layout retain the depth study proportions.

This remains a 1000px, 48 sample Cycles study with simple crown geometry. Earlier renders remain available separately. The builder checks the projected tower top, tower base, and stair foot before saving and rendering.

## Lighting hierarchy study

`cathedral-light-study.png` and `cathedral-light-study.blend` preserve the silhouette study geometry and camera while separating the scene through lighting. Rebuild with `tools/render_cathedral_light.py`.

The monument receives a stronger soft light. Three broad point sources suggest openings above the left canopy, right canopy, and stair approach, revealing selected crown tops and tread edges. The left canopy light is slightly warmer than the right. The existing forest atmosphere and shaded giant trunks retain the surrounding depth. These sources use soft point lights to avoid the sharp volumetric cutoffs seen with area fills in earlier studies.

This is still a simplified 1000px, 48 sample composition render. No individual foliage detail or website changes are included. Camera projection checks retain the previous framing.

## Asymmetric canopy families

`cathedral-canopy-study.png` and `cathedral-canopy-study.blend` replace the repeated radial crown with seven asymmetric families of simple connected lobes. Rebuild with `tools/render_cathedral_canopy.py`.

Each family varies the spread, height, and size of its lobes around a lower connecting mass. A separate random generator creates the templates so the existing planting positions, architecture, lighting, and camera remain stable. Family selection is deterministic from world placement. Distant variants retain the subdued forest material. This is still simple crown geometry, without individual leaves.

The render remains 1000px at 48 Cycles samples. See `../BLENDER_HANDOFF.md` for the full agent workflow and lessons from earlier passes.

## Connected forest stands

`cathedral-stands-study.png` and `cathedral-stands-study.blend` break up the broad smooth banks with five smaller shoulders, two shallow gullies, and modest terrain irregularity. Rebuild with `tools/render_cathedral_stands.py`.

Additional groups of smaller crowns connect exposed gaps around the visible banks and roots. A separate random generator preserves the earlier planting samples while adding these groups. The seven canopy families, camera, architecture, lighting, and atmosphere remain the prior study baseline. Terrain changes affect ground-following planting and trunk base elevations.

The simplified render remains 1000px at 48 Cycles samples. Camera framing assertions pass. Agent handoff notes in both checkouts identify this as the latest generated pass and record the agreed sequence for the following architectural and atmospheric work.

## Architectural depth

`cathedral-architecture-study.png` and `cathedral-architecture-study.blend` retain the stands study composition while adding actual Boolean recesses to the 305 and entrance. Rebuild with `tools/render_cathedral_architecture.py`.

The inscription has approximately 3.2 working units of depth, with its dark text surface moved inside the cut. The doorway is carved about 11 units into the facade, with a back wall and recessed warm light. Cuts are applied before a shared edge bevel. Ray checks on the monument mesh independently confirm the inscription and doorway recesses. The steps retain their dimensions and receive modest basalt color/roughness variation and slightly softer edges.

`tools/render_cathedral_architecture_detail.py` opens the saved blend and renders a separate high resolution camera crop to `cathedral-architecture-detail.png`, without saving over the full scene or moving its camera. The full render remains 1000px, 48 samples; the detail uses a cropped 3600px frame, 64 samples.

The handoff now explicitly records Lova's preference for continual visual check-ins, including actual PNG/JPG renders, screenshots, or browser previews suited to the work.

## Cooler atmospheric depth

`cathedral-atmosphere-study.png` and `cathedral-atmosphere-study.blend` retain the architectural pass geometry, camera, and lights. Rebuild with `tools/render_cathedral_atmosphere.py`.

The foreground medium is slightly clearer; extinction rises more strongly beyond the monument. A cool blue-gray volume color, low-frequency density variation, and faint emission restricted to the distant medium reduce contrast in the forest gaps. The camera-visible world background is also slightly cooler. The emission is an artistic approximation of distant ambient illumination, not an additional modeled sky opening.

The render remains 1000px at 48 Cycles samples. Geometry ray checks for the recessed inscription/entrance and camera framing assertions run before rendering. The previous architectural study and close-up remain preserved for comparison.

## Quiet reference backdrop

`cathedral-backdrop-study.png` and `cathedral-backdrop-study.blend` follow a fresh visual comparison with the exact Midjourney index-2 reference. Rebuild with `tools/render_cathedral_backdrop.py`.

The 28 large distant stems created graphic bands that stronger fog alone did not resolve. They remain editable but are hidden from rendering in this pass. A remote procedural forest backdrop uses subtle elongated noise and blue-green values, seen through the existing volume. It is an editable background surface for this composition study; the two principal trunks, terrain, canopy, monument, and stairs remain modeled geometry.

The middle canopy fills are reduced, and a soft opening near the pond adds a selective foreground highlight. Camera pose and lens remain fixed; far clipping is extended to include the remote backdrop. Geometry and framing checks remain active. The output is 1000px at 48 Cycles samples.

## Fine surface foliage

`cathedral-foliage-study.png` and `cathedral-foliage-study.blend` add actual small, cupped leaf meshes over the seven approved crown families. Rebuild with `tools/render_cathedral_foliage.py`.

Each family has a shared surface mesh containing 11,000 leaves with four muted green tones. Leaves are sampled by triangle area across the supporting crown surface and instanced on nearer banks (working Y < 365 and |X| < 265). The supporting crown material gets a finer bump texture. Distant crowns remain simple. A separate leaf random generator preserves the established planting, geometry, and camera. Leaf face orientation is outward, and each leaf keeps one material across its facets.

The full render uses 1200px, 64 Cycles samples, and denoising. `tools/render_cathedral_foliage_detail.py` renders a separate crop of the nearer left bank from a 3600px frame; it does not move the camera or save over the full blend. The underlying shapes and procedural remote backdrop remain editable.

A builder naming collision initially shadowed the `area()` light helper with a triangle-area scalar and was corrected to `triangle_area` before a completed render. The repository tests do not catch Blender runtime errors; verify the actual render output as well as the geometry/framing assertions.

## Branch clusters

`cathedral-branch-study.png` and `cathedral-branch-study.blend` replace part of the surface-leaf layer with small outward branching shoots. Rebuild with `tools/render_cathedral_branches.py`.

Each family retains 7,500 surface leaves and adds up to 550 tapered woody shoots with 12 leaves each, skipping downward-facing samples. Leaf directions vary around each shoot, extending the canopy edges without moving the established planting. Shared meshes retain the four leaf tones and add the bark material for stems. Camera, architecture, lights, and backdrop are preserved.

The 1200px/64-sample full render took about 2m40s on CPU. `tools/render_cathedral_branch_detail.py` renders the matching close-up from the same camera without overwriting the saved blend.


## Focused branch-spray test — 2026-09-11

`cathedral-sprays-study.png` and `.blend` are an isolated experiment based on Lace, not its
replacement. `../tools/render_cathedral_study.py -- --variant sprays` runs under Blender and
replaces only 34 right shoreline crowns. Camera, architecture, lighting and other planting remain
from the saved Lace scene. The `baseline` variant reloads Lace unchanged; `sprays-flat` preserves
the first, overly flat branch distribution. `--quick` renders 16 samples without saving a blend.

`cathedral-sprays-comparison.png` shows reference / Lace / Sprays from left to right, made by
`../tools/compare_sprays.py`. The full 1200px/64-sample render took 2m47s. The result opens the
crowns but is too sparse and horizontally layered; whole-frame cell RMS worsened from 5.019 to
5.250. Keep Lace as baseline while reviewing this test. See BLENDER_HANDOFF.md for the next hypothesis.


## Fuller shoreline crown — local outputs, 2026-09-11

`cathedral-hero-crown-study.png` and `.blend` are deliberately ignored and remain on Hitch_07.
Rebuild through Blender with `tools/render_cathedral_study.py -- --variant hero-crown`. The new
`tools/cathedral_crown.py` builds one fuller specimen with eleven branch systems and hanging
growth; camera and lighting are unchanged. It replaces the same 34 shoreline stands and lowers
98 overlapping clumps to keep ground cover without hiding the crown edge. Use `--retain-understory`
to keep the original foreground. Comparison: `tools/compare_sprays.py -- --variant hero-crown`.
No render or Blender output from this pass should be staged or pushed.


## Irregular canopy — local outputs, 2026-09-11

The `hero-canopy` variant builds on the fuller crown with a broader, uneven outline and grouped
leaf values. `cathedral-hero-canopy-study.png` / `.blend` stay local. Compare with the previous
crown using `tools/compare_sprays.py -- --variant hero-canopy --baseline hero-crown`. Render: 1200px,
64 samples, 2m40s. Cell RMS 4.937 versus 4.995 before; leaves still need less uniform size/crispness.
Historical `cathedral-canopy-study.*` is a different archived pass, restored and verified after
an initial naming collision. The runner now rejects tracked output paths; `--output-name` permits
rebuilding historical profiles under new local filenames.


## Leaf shape / surface test — local outputs, 2026-09-14

`hero-leafcraft` preserves the hero-canopy branch geometry and placement, using varied tapered
leaf outlines, size/proportion variation, smooth leaf shading and roughness 0.62. The PNG and
Blender outputs stay local as `cathedral-hero-leafcraft-study.*`. Compare with
`tools/compare_sprays.py -- --variant hero-leafcraft --baseline hero-canopy` through Blender.
Full render: 1200px, 64 samples, 2m59s. RMS 4.943 versus 4.937 previously, effectively unchanged.
The visual difference is subtle and face count increases from 138,592 to 267,664; assess that
tradeoff before wider use. Source and handoff changes are uncommitted pending review.


## Grouped leaf sprays — local outputs, 2026-09-14

Run the `hero-sprig` variant for the same leaves gathered into three growth sprays per twig.
`cathedral-hero-sprig-study.*` and its comparison remain local. Camera, woody geometry and scene
placement are verified unchanged; no extra geometry was added. Render: 1200px/64 samples, 2m53s.
RMS 4.974 versus leafcraft 4.943. The visual difference is subtle, with no clear win; retain
leafcraft for now and consider upper stair tread readability next. Compare through Blender with
`tools/compare_sprays.py -- --variant hero-sprig --baseline hero-leafcraft`.


## Upper stair edge definition — local outputs, 2026-09-14

`stair-edges` uses the hero-leafcraft crown and retains the original staircase dimensions.
Broader worn-edge bevels are introduced gradually above step 32. Outputs are local-only
`cathedral-stair-edges-study.*`; comparison uses `tools/compare_sprays.py -- --variant stair-edges
--baseline hero-leafcraft` through Blender, with a stair crop rather than foliage.
Render: 1200px/64 samples, 3m03s; RMS 4.836 versus 4.943. Upper steps now read visibly farther
up the flight. All original step meshes, crown branches, scene transforms and camera were
verified unchanged. Future wear/shadow variation should retain the new definition.


## Stair weathering — local outputs, 2026-09-14

`stair-weathered` adds continuous damp-stone variation and small bevel-width differences to the
recovered stair edges. Camera and step meshes remain fixed. The first trial dimmed the edges too
much; its PNG is retained as `cathedral-stair-weathered-initial.png`. Final body factors are
0.85–1.12, edge factors 0.65–1.40; final output is `cathedral-stair-weathered-study.*`.
Render: 1200px/64 samples, 2m59s; RMS 4.838 versus stair-edges 4.836, with nearly identical mean
brightness. It retains step definition with subtle variation. Compare through Blender using
`tools/compare_sprays.py -- --variant stair-weathered --baseline stair-edges`. These outputs
stay local; only the earlier checkpoint was pushed.


## Monument limestone — local outputs, 2026-09-14

`monument-stone` inherits stair-weathered and copies only the monument material. It adds subtle
mottling and vertical weathering at the scale visible from the fixed camera. First trial was too
blotchy; retained locally as `cathedral-monument-stone-initial.png`. Final render and editable
scene are `cathedral-monument-stone-study.*`; compare using `tools/compare_sprays.py -- --variant
monument-stone --baseline stair-weathered` through Blender. Render: 1200px/64 samples, 3m00s.
RMS 4.840 versus 4.838 previously. The 305 inset/edge shading is a potential next focus.
Monument topology, original stair meshes, crown branches and scene transforms were verified
unchanged. Checkpoint bdf68c0/faefb05 was committed locally, not pushed; this new pass is uncommitted.


## Limestone 305 inset — local outputs, 2026-09-14

`inscription-stone` retains the carved geometry and replaces the dark basalt inset material
with the monument limestone. Local output: `cathedral-inscription-stone-study.*`. Compare via
`tools/compare_sprays.py -- --variant inscription-stone --baseline monument-stone` through Blender.
The lettering now has a lighter interior with shadowed recess edges. Text geometry/placement and
the scene geometry are verified unchanged. Render: 1200px/64 samples, 3m02s; RMS 4.824 versus
4.840 before. This pass remains uncommitted; no new renders or Blender files were uploaded.


## Entrance depth and warmth — local outputs, 2026-09-14

`entrance-depth` inherits inscription-stone, darkens the rear panel, redirects the existing warm
light to the floor, reduces/moves the luminous fixture, and adds two small warm details inside.
The back panel now sits ahead of the boolean back face; a ray test confirmed its visibility.
Local outputs: `cathedral-entrance-depth-study.*`; initial panel-placement trial retained as
`cathedral-entrance-depth-initial.png`. Compare via `tools/compare_sprays.py -- --variant entrance-depth
--baseline inscription-stone` through Blender. Final render 1200px/64 samples, 3m03s; RMS 4.872
versus 4.824 previously. The opening reads deeper, but exterior warm spill remains subdued.
Scene geometry outside the scoped entrance changes is verified unchanged. Keep this local for
review and assess the full composition before further doorway tweaks.

### Left bank massing — 2026-09-15

`render_cathedral_study.py -- --variant left-bank-masses` retains entrance-depth and adds broad private shade groups on the left bank. Initial base-anchored compression exposed smooth terrain and was rejected; its local outputs are named `cathedral-left-bank-compression-rejected.*`. The corrected pass retains the original planted volume. PNG/blend stay local and ignored. Compare full composition with `compare_sprays.py -- --variant left-bank-masses --baseline entrance-depth`. Camera, architecture, terrain, giant trunks and right bank are preserved.

### Coordinated left bank contour — 2026-09-15

`render_cathedral_study.py -- --variant left-bank-contour --resolution 700 --samples 16` makes a saved composition preview with terrain and planting translated together, exposing more of the fixed giant left trunk. Local PNG/blend and full-frame comparison remain ignored. Camera, monument, stairs and right bank are preserved. Use `compare_sprays.py -- --variant left-bank-contour --baseline left-bank-masses`; review shape at this resolution, not fine foliage.

### Left bank contour full quality — 2026-09-15

The approved contour composition is preserved at 1200px/64 samples in local `cathedral-left-bank-contour-full.png` and `.blend`. Rebuild with `render_cathedral_study.py -- --variant left-bank-contour --resolution 1200 --samples 64 --output-name cathedral-left-bank-contour-full`. Compare using `compare_sprays.py -- --variant left-bank-contour --baseline left-bank-masses --render-name cathedral-left-bank-contour-full`; the 700px preview remains separate.

### Right bank contour preview — 2026-09-15

`render_cathedral_study.py -- --variant right-bank-contour --resolution 700 --samples 16` keeps the accepted left contour and lowers a shallower part of the far right bank with its planting. Outer taper preserves cover over the giant trunk base; initial outer-edge exposure was rejected and saved locally as `cathedral-right-bank-outer-edge-rejected.*`. Compare with `compare_sprays.py -- --variant right-bank-contour --baseline-name cathedral-left-bank-contour-full`. All render outputs remain ignored/local.

### Canopy grouping shape test — 2026-09-15

`render_cathedral_study.py -- --variant canopy-groups --resolution 700 --samples 16` widens 1,684 crown/leaf pairs into overlapping groups while preserving heights, terrain, architecture and the shoreline hero tree. Compare against `cathedral-right-bank-contour-study` using `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-right-bank-contour-study`. All images/blends remain local and ignored.

### Lower camera / water proximity — 2026-09-15

`render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --resolution 700 --samples 16 --output-name cathedral-water-camera-study` lowers camera z108 to72 without changing lens, tilt or geometry. The new camera flag requires a separate output name. Compare using `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-canopy-groups-study --render-name cathedral-water-camera-study`. PNG/blend remain local/ignored; this is a composition preview.

### Farther camera / longer lens — 2026-09-15

`render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-waterline .89 --resolution 700 --samples 16 --output-name cathedral-compressed-camera-study` tests 25% more camera-to-monument distance and focal length, retaining the lower viewpoint and solving pitch for less foreground water. Local PNG/blend remain ignored. Compare against `cathedral-water-camera-study` using the comparison tool --baseline-name and --render-name options.

### Camera framing refinement — 2026-09-16

`render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-lens 47 --camera-waterline .89 --resolution 700 --samples 16 --output-name cathedral-camera-framing-study` retains camera position/geometry, brings the tower top to8% and keeps stair foot at89%. Local PNG/blend plus comparison remain ignored. Stair/monument proportions still differ from reference.

### Connected ascent and lighting passes — 2026-09-16

Camera stays at z72/y-1147.5, lens47, waterline.89. New --ascent-lift70 extends all150 risers to landing520 while preserving monument summit1350, with terrain/planting and entrance assemblies moved consistently. Candidate `cathedral-ascent-proportion-study`. --canopy-shadows adds two shadow-only canopy flags (`cathedral-canopy-shadow-study`); --entrance-wash tests a soft warm entrance facade light (`cathedral-warm-ascent-study`). Use the two new helper modules `cathedral_ascent.py` and `cathedral_forest_light.py` through the maintained runner. All candidate PNG/blends remain local and ignored.

Final full-quality candidate: `cathedral-ascent-lighting-full`,1200px/64samples, adds --ascent-lift70 --canopy-shadows --entrance-wash --entrance-wash-power27000 --entrance-wash-size75 to the lens47 camera recipe. Keep the initial9000W/size30 warm preview as a diagnostic comparison; it produced a small hotspot. Use spaced CLI flags as shown in BLENDER_HANDOFF.md.

### Pond reflection study — 2026-09-17

After verifying the remounted full-quality scene, `--pond-roughness .18` tests clearer surface reflections over the ascent-lighting recipe, with all other water properties unchanged. Local candidate `cathedral-pond-reflection-study`,700px/16samples. Previous water roughness remains.30 by default; do not replace the full-quality baseline before visual review.

Pond roughness.18 was reviewed but not promoted: stronger amber lamp streaks distract without resolving shoreline texture. Keep the softer.30 water in `cathedral-ascent-lighting-full` as the working candidate. All experiment outputs are preserved locally.

### Foreground shoreline — 2026-09-17

`--shore-colonies` adds953 floating leaves in six broad foreground groups, preserving250 old pads hidden (`cathedral-shore-colonies-study`,700/16). `--shore-gathered` tightens the groups asymmetrically into926 leaves and adds one downward left foreground area light (`cathedral-shore-gathered-full`,1200/64). Both extend the ascent-lighting-full recipe, preserve camera/architecture/water roughness, and keep all PNG/blend outputs local and ignored. See handoff for review decision.

Review: reject the added foreground light in gathered-full (broad pale water reflection). Retain the tighter planting using `--shore-gathered --shore-no-light`; corrected `cathedral-shore-natural-study` rendered900px/32samples and passed visual/scene review. Existing camera, geometry, lights and water settings are preserved. Full1200/64 rerender of the correction remains available for a later checkpoint.

### Hillside foliage detail — 2026-09-17

The maintained runner accepts `--canopy-detail support|fine|broken|dense` via `cathedral_canopy_detail.py`, added to the shoreline-natural recipe. `cathedral-canopy-support-study` completed700/16 with subtle material-only changes; `cathedral-canopy-fine-study` saved a blend but its dense render was terminated(exit137,noPNG). `cathedral-canopy-fine-light-study` completed700/16 but exposes too much rounded support. The third `cathedral-canopy-broken-study` restores leaf area, removes support specular and warps upper shell/leaf geometry together at900/32. See handoff for the final review decision. Avoid concurrent Blender scene validation while rendering heavier foliage. All new render artifacts stay local/ignored.

Final canopy review: broken completed900/32 in5m59s and passed isolation checks. Less rounded outline but overly angular ridges; keep diagnostic only. Working scene remains cathedral-shore-natural-study. Final triptych is cathedral-canopy-broken-study-comparison.png. Next experiment should target a few visible crowns with actual branch/leaf geometry before extending across the forest.

### Targeted branching crowns — 2026-09-17

Checkpoint35623e7 and mirrored handoff77af69f were pushed before these passes; no renders were pushed. `--branch-patch left` replaces12 camera-visible paired crowns, `both` replaces48 across two hillside patches, reusing the natural shoreline crown mesh and retaining original transforms/material slots. Built over shoreline-natural, without rejected canopy-detail flags. Left preview700/16; both900/32 completed7m38s and passed isolation validation. Comparison supports optional normalized top-down `--crop .24 .38 .43 .63`. Third detail render uses the same both scene with `--resolution 2400 --samples 64 --render-crop .24 .38 .43 .63`, saving a cropped view rather than moving the camera. All outputs remain ignored/local. See handoff for final review.

Final review: retain cathedral-branch-patch-both as the current900/32 working candidate. The456x600 high-resolution crop cathedral-branch-patch-detail completed7m26s and shows fine overlapping branch foliage beside the old rounded crowns; scene isolation checks passed. Detail blend has render border enabled, so use both-patch blend for full images. Branch-patch source and notes are included in the requested pause checkpoint after35623e7; artifacts stay on Hitch_07. Resume from the both-patch scene.
