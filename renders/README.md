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
