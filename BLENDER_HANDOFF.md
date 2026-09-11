# Cathedral Blender study — agent handoff

Updated 2026-09-10. Read this before continuing the cinematic forest work. This is a local, editable Blender study for Lova's portfolio, not yet a website asset or deployment.

## Where work lives

- Main repository: `/Users/victoriarajaonarivony/Documents/monolith`.
- Active study worktree: `/Volumes/Hitch_07/Blender/Data/monolith-cathedral`, branch `codex/forest-cathedral`. This lives on the removable Hitch_07 drive; see "Drive location and repointing" below before assuming the path resolves.
- Current reviewed baseline: `tools/render_cathedral_foliage.py`, `renders/cathedral-foliage-study.png`, and `renders/cathedral-foliage-study.blend` in the study worktree.
- Current latest pass: `tools/render_cathedral_spill.py`, `renders/cathedral-spill-study.png`, and `renders/cathedral-spill-study.blend`. The chain to it is branches, then value, mass, shore, trunk, plinth, foreground, crowns, separation, tone, highlights, rebalance, edge, litbanks, emergent, pads, wall, sunside, gradient, gaps, cling, columns, lamps, layers, softkey, vines, spill; each has its own builder and PNG/blend pair and they are all kept.
- Earlier branch pass: `tools/render_cathedral_branches.py` with `renders/cathedral-branch-study.png`. `tools/render_cathedral_branch_detail.py` produces the matching close-up.
- Iteration history and rebuild notes: `renders/README.md` in that worktree.
- Source meshes: `assets/cathedral/cathedral-trunks.blend`.

Run `git log --oneline -5` and `git status --short` in the worktree before assuming its state. The study archive was committed and pushed as `f46b7bd` on `origin/codex/forest-cathedral`; GitHub checks passed and all 19 Blender files uploaded through Git LFS. Check current branch status before assuming later work is committed. Do not clean untracked files or assume the main checkout contains the study. The unrelated main-checkout `b/` directory belongs to other work. The worktree also contains earlier website edits and preview configuration; this Blender task is not permission to publish those. The study was moved off `/private/tmp` to the external drive on 2026-09-10 because that path is not durable archival storage.

## Drive location and repointing

The study lives on the removable `Hitch_07` drive. Git's bookkeeping for the
worktree does not: `.git/worktrees/monolith-cathedral` stays in the main
repository on the internal drive, and only the checkout is on the external
drive. So the registration survives an unmount; it is the path that can move.

Before doing anything, confirm the drive is actually mounted:

```sh
ls -d /Volumes/Hitch_07/Blender/Data/monolith-cathedral
```

If that fails, the drive is unplugged or asleep. Stop and ask rather than
recreating the study somewhere else — the renders and `.blend` files exist only
here and on `origin/codex/forest-cathedral`.

macOS usually remounts this volume at the same `/Volumes/Hitch_07`. If a stale
mount is present it can instead appear as `/Volumes/Hitch_07 1`, which makes the
recorded path wrong without anything reporting an error. When the path differs,
repoint git from the main repository:

```sh
cd /Users/victoriarajaonarivony/Documents/monolith
git worktree unlock "/Volumes/Hitch_07/Blender/Data/monolith-cathedral"
git worktree repair "<actual mounted path>/Blender/Data/monolith-cathedral"
git worktree lock --reason "on the Hitch_07 external drive" "<actual mounted path>/Blender/Data/monolith-cathedral"
```

Then update the paths in this file so the next agent reads the truth.

Two settings exist because of the drive and should not be undone:

- The worktree is **locked**. `git worktree prune` would otherwise deregister it
  whenever the drive is unmounted, because the path does not resolve. Unlock
  only to move it, and lock it again afterwards.
- `core.fileMode` is `false` for this worktree only, set through
  `extensions.worktreeConfig` in `.git/config.worktree`. The drive is exFAT and
  mounts `noowners`, so every file reads as `rwx` and git otherwise reports all
  173 tracked files as modified with no content change. The main checkout keeps
  `core.fileMode=true`; do not set this repository-wide.

`git worktree move` cannot move a worktree onto this drive — it uses `rename()`
and fails with "Cross-device link". Copy with `rsync -a`, run
`git worktree repair` against the new path, then delete the source once
`rsync -rcn` reports no differences.

exFAT is case-insensitive, like the internal volume, so that changes nothing
here. Symlinks do work on this mount; `CLAUDE.md -> AGENTS.md` survived the move
intact. Renders write to the drive normally.

## What the user is asking for

A faithful cinematic recreation with immense scale. The exact reference is:
https://www.midjourney.com/jobs/1d1707f0-f59c-4585-9c60-3d25c745643c?index=2

The target is index 2, not the whole four-image grid. The built-in browser has successfully displayed it anonymously when ordinary web fetching failed. Inspect the actual image rather than relying on its prompt.

The reference has two gigantic tree trunks rising out of a dense, much smaller forest; a distant pale forked monument; a large 305 inscription; enormous stairs; and a small green pond at the bottom. The user explicitly approved simplifying foliage until camera, proportions, and depth are right. They accept longer renders. Do not add thousands of detailed leaves merely to make a composition problem look more finished.

Latest accepted direction: farther camera, two main trunks, uneven forest banks burying their bases, planting overlapping stair margins, subdued background forest, and selective canopy lighting. Keep current camera/architecture as the comparison baseline for the next pass unless the user reopens those decisions. Earlier user requests did reopen them; do not treat old approvals as permanent constraints.

## User preference: continual visual check-ins

Lova explicitly prefers short, continual check-ins with visual evidence. Work in focused passes, explain what the next pass is testing, inspect the actual result, and send a render PNG/JPG, screenshot, or browser preview as appropriate. These updates give both user and agent shared context and support efficient decisions. Preserve prior versions for comparison and incorporate feedback before broadening a pass. Keep this workflow when another agent takes over; do not replace visual updates with text-only claims or silently bundle several major changes into one result. For this offline Blender work, show the actual render and link its editable `.blend`.

## How the work is produced

Python scripts build the entire editable scene in Blender and render with Cycles. These are real 3D renders, not generated image edits. Blender runs as a separate background process; the user's open Blender window does not automatically update. Deliver both PNG and `.blend` links. Do not claim the visible Blender UI was used.

From `/Volumes/Hitch_07/Blender/Data/monolith-cathedral`:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 8 --python tools/render_cathedral_branches.py
```

Blender 5.2.1 LTS is installed. CPU rendering works; Metal previously stalled while waiting for kernels. Sandboxed Blender previously crashed before executing the script, so background render commands have needed the normal `require_escalated` execution path. Do not bypass approval review or kill the user's GUI Blender. Poll the exact process/session started for this task, using waits of at most 30–60 seconds and concise progress updates.

The current branch study uses 1200 × 1200, 64 Cycles samples, denoising, AgX, and 8 CPU threads; its full render took about 2m40s, and the separate close-up about 1m18s. Earlier simple studies used 1000px/48 samples, and earlier detailed 1600px renders took several minutes. More samples improve noise, not proportions or modeling.

Create a separately named builder/PNG/blend for each new user-visible pass. Preserve earlier accepted studies. Edit with exact asserted anchors, inspect the resulting render, and only then describe what improved. Temporary patch scripts are not authoritative; the `tools/render_cathedral_*.py` files are.

## Coordinates and current framing

Blender uses Z up; the camera looks along positive Y. Builders lay out geometry in working units, then multiply object locations/scales by 3 and light energy by 9. Do not blindly repeat that transform when reopening a saved blend. Uniformly enlarging the scene and camera preserves the image; perceived scale depends on relative proportions, perspective, and depth cues.

Final camera: `(0, -720, 108)`, 35.518mm lens, upward tilt 0.226 radians. Tower facade is about 1710 metres away horizontally in the final scene, with a 900-metre silhouette above a 450-metre ascent. These are intentional fantasy dimensions. Stairs have 150 steps and taper from about 174 to 141 metres wide. Reference framing checks target tower top near 8%, tower base near 53%, and stair foot near 89% from the image top. The builder asserts these before saving/rendering. Matching these landmarks does not by itself mean the whole image matches the reference.

## Lessons and remaining limitations

- Continuous leaf-covered cliff walls lost the hierarchy of two giant trunks and much smaller trees. The present uneven banks support that hierarchy.
- Uniform canopy templates and smooth ramps look like miniature landscaping. Vary connected crown silhouettes and grouped stands before adding individual leaves.
- Exposed flared roots read as columns standing on top of the forest. Bury bases with varied terrain/canopy masses.
- Thin distant trunks against bright gaps look like poles. Keep distant stands broad, irregular, subdued, and merged by depth haze. Random floating crown blobs across the entire background were rejected during visual checks.
- Area fills previously produced sharp atmospheric cutoffs. Broad soft point lights avoided that issue. Hiding an area emitter from the camera or changing `volume_factor` did not fix those Cycles cutoffs.
- A small atmosphere box caused a horizontal boundary across the sky. The current box extends beyond the visible framing; density increases beyond the monument through a Generated-Y Map Range.
- The world uses a darker camera-visible background while retaining brighter environment illumination. This prevents bright gaps from outlining every distant shape.
- Terrain noise tapering to zero at the pond removed flat shallow patches. Keep the pond small in frame.
- The architecture study replaces the earlier flat 305 treatment with a real Boolean recess; a dark text surface sits inside the recess to retain legibility. The entrance is also cut into the monument. Ray checks verify actual mesh depth independently of overlays. Apply booleans before beveling and delete only the cutters created by the current operation. This remains a composition study, not a finished realism render.
- Current near foliage includes real leaf and small branch geometry over seven supporting crown families; distant crowns remain simple. Rounded supporting forms are still visible. Inspect the latest branch study and its close-up before the next refinement; this is not yet finished realistic foliage.

## Measuring against the reference

Judging "closer to the reference" by eye alone was costing passes, so there are now four small
tools. They run under blender because it has numpy and can read PNGs without any extra install.

- `tools/compare_diff_map.py` — the important one. Splits both images into a twelve by twelve
  grid and prints the per cell difference plus an rms, so the answer is *where* we are wrong
  rather than just whether we are bright. It found in one run what five rounds of scalar tuning
  had missed, and it immediately contradicted a scalar reading that said the pond was fine.
- `tools/compare_value_stats.py` — histogram shape: mean, percentiles, contrast, region bands.
  Useful once you know where to look. On its own it hides local error by averaging it away.
- `tools/compare_crop.py` — magnified crop of one region for texture comparison.
- `tools/compare_histogram.py` — how the luminance is distributed band by band. The other two miss
  shape entirely. This is what showed that half the reference sits in a narrow 30 to 40 band while
  ours spreads across 30 to 50, and that our tower holds three times its share above 100.
- `tools/probe_frame_cells.py` — raycasts chosen cells and reports what geometry is behind them
  in world coordinates. Use it before placing anything; see the units lesson below.

The reference itself is committed at `reference/midjourney-index2.png`; see the README beside
it for provenance. The tools take it as their first argument and do nothing without it.

The working loop is a quick render at 600px/16 samples through `CATHEDRAL_QUICK=<path>`, which
takes about 24 seconds against 2m45 for the full pass, then the diff map, then a full render only
once the numbers and the image both look right. The reference itself is a browser capture of the
midjourney page, so it carries a few percent of jpeg and display profile error; the gaps that
matter here are much larger than that, but do not chase its last digit.

**Quick renders lie about small differences.** At 600px/16 or 1200px/16 the noise is worth roughly
a tenth of rms and a couple of points of any percentile, which is the same size as the gains being
chased at this stage. Two whole passes were built and discarded on differences that turned out not
to exist at 64 samples. Confirm anything under about 0.2 rms with a full render before believing it.

**Things tried against the reference and discarded**, so they are not tried again:
- Thinning the bank in front of the plinth to let the wall through. It made that cell darker, not
  lighter: what stands behind the foliage there is not the wall. Four attempts on that one cell now,
  from three directions, all failed.
- Brightening the near left bank to match the reference's bright bottom left. Improved its own cell
  and spilled into four neighbours; rms 5.0 to 5.4.
- Shifting the lighting budget back toward fill with an exposure trim, to tighten the midtone band.
  Promising at 16 samples and identical to the existing setup at 64. The fill, key and exposure
  triple is already at a local optimum.

**rms is a guide, not the verdict.** Two separate passes scored better while visibly getting
worse: a pond that measured correct and read as a flat mint slab, and trunk foliage that scored
8.3 while reading as balls floating off the silhouette. Always look at the render as well.

## Value and structure passes

Error against the reference went from rms 10.1 to 5.0 across twenty five passes, with contrast from
50.7 through a low of 30.5 back to 49.5 against the reference's 46.1, all kept. Some trade a
little rms for a large visual gain, so these numbers are not a clean ranking; read them with the
contrast figures beside them:

- **value** — first attempt at the dark reference look, by lowering the fill lights. Wrong: it
  made the frame dimmer and flatter without making it darker, and cost the foliage its modelling.
  Only the brighter pond survived. Kept for comparison; do not build on it.
- **mass** — the one that worked. The upper frame was bright because the haze was *scattering the
  key light*, not because of geometry, the backdrop or the world background; all three of those
  together moved almost nothing. Dropping the volume scattering albedo from .46 to .24 moved more
  than everything else combined, and keeps extinction so depth separation survives.
- **shore** — the water was far too bright, the lily pads too few, small and dark, and the
  shoreline stands missing. The reference's brightest foreground is crowded pale pads near camera.
- **trunk** — bark darkened and given fine vertical vine streaking, and the silhouette broken by
  about 620 small clinging clumps per trunk.
- **plinth** — a broad flanking wall and cornice either side of the tower, about four times its
  width, with planting lapping over both ends. Built as two segments rather than one wall so it
  cannot reach into the entrance recess cut between y 329 and 341.
- **foreground** — the near field carries the lighter shoreline material instead of the ordinary
  dark canopy tone, the way distance already picks the hazier one at the far end. The reference is
  also not symmetric here, so the right bank takes a brighter tone again than the left, and the
  bottom left corner gets an explicit cluster of large pads because a uniform scatter never covers
  one corner densely enough. This was the single largest gain after the haze albedo.
- **crowns** — the blob problem, and the diagnosis had been wrong: the reference crowns are rounded
  masses too, so their outline was never it. What they have is granularity at about five percent of
  a crown where ours sat near two, which is one pixel in frame and averages into a smooth shell.
  Leaves roughly tripled in size, plus a second finer noise octave on the lobes.
- **spill** — two cells had been running ten over for several passes, and raycasting them landed
  within a few units of where the `near bank opening` fill sits. That light was placed for the near
  bank and had been lighting the middle distance the whole time; moving it lower and nearer the
  camera and trimming it fixes both. The shoreline growth was also reaching into the bottom right
  pond cell, which the reference keeps bright, so it starts further out.
  Pulling the fill back then left the brightest bank tier standing fifteen over against darker
  surroundings, so fewer crowns take it. Worth expecting: trimming a fill changes what every tier
  above it is measured against.
- **vines** — the trunks were speckled with clumps where the reference drapes them in continuous
  hanging curtains. Clumps give a ragged silhouette but never the vertical run, so the vines are
  real geometry: thin tapered strands hung off the sampled trunk profile, drifting as they fall,
  with small leaves down their length. Density and leaf size decide whether this reads as a curtain
  or as beads on a string, the same distinction as the trunk clumps and the corner pads.
- **softkey** — with p95 on the reference and p5 five under, all of the excess contrast was shadow
  depth. Everything tried for that floor earlier failed for a specific reason worth recording: haze
  lifts the darks and veils the highlights equally, raising dark albedo lifts the midtones instead,
  and more bounces change nothing because those areas are not light starved. The sun's angular size
  is the lever that works: a wide disc softens the terminator and opens what sits just inside it,
  which is where the darkest twentieth lives. At 24 degrees p95 holds and at 42 contrast lands, so
  30 is where both come closest. Far wider than a real sun, which is fair here: this key stands in
  for light coming down through a forest canopy, a broad source.
- **layers** — the banks stopped at y 345 and the distant silhouettes began at 480, so nothing
  occupied the depth either side of the monument and the forest jumped straight from planting to
  backdrop. The reference reads deep there because its forest recedes continuously with haze
  between the layers. Filling that gap improves rms and p95 together and puts trees in front of the
  plinth wall at varying depths, which is what the reference shows at the monument base.
- **lamps** — the stairs had never been looked at closely. Twenty four lamps a side with a hood
  about three pixels wide read as a dotted line; the reference has nine or so, each a clear warm bar
  on a post. Scaled up they are still modest fittings against a staircase 174 metres wide.
  The treads also vanished into a smooth ramp above the lower third, where the reference keeps its
  step lines all the way up. What reads at that distance is the darker riser under each nosing, so
  the faces turned toward camera darken by normal and the line survives the pixel averaging. That
  darkening is what brings the ascent down in value now, so the level trim doing that job came back
  off; stacking both took the stair to flat black.
- **columns** — raising the whole bark range to get the vertical streaks reading again had lifted
  the trunks off near black, which is where the reference keeps them. Contrast for a feature like
  that belongs in the ramp span, not the level: narrowing the span gives the streaks without
  brightening the column. The shoreline growth also gets leaves, since bare shells sitting on open
  water read as rocks while the same shapes with foliage read as growth.
- **cling** — the trunk foliage had been placed at the trunk's nominal radius, which is its radius
  at the base. The trunk tapers, so at height those clumps sat outside the actual surface and read
  as a string of beads hanging in the air beside it, which the trunk pass never caught because it
  was judged on the map rather than on a crop. Sampling the mesh's real radial profile per height
  band and hanging them on that fixes it. Giving the sunward ones a lit tone is also reverted: fine
  on the trunk face, wrong at the silhouette, where it made the beads glow against the sky.
- **gaps** — cell averages were matching to about four levels while the median still ran four
  high, so the darks missing were inside the cells rather than across them. Wider stand heights and
  a thinner understory help a little, and the tower comes down while the lit canopy comes up, which
  moves pixels between bands rather than shifting the frame. The residual is tonal shape rather
  than placement: we hold five percent more pixels below 30 and eighteen percent more in 40 to 50,
  where the reference concentrates in 30 to 40. Some of that is a path traced render against a
  generated image, and chasing it with a global tone curve would soften the render rather than
  match it. Worth knowing before spending renders on it.
- **gradient** — the reference's right bank reads 36 up the slope and 50 to 63 at the waterline;
  ours did the reverse, because the key lights tops. So the stand at the water takes more of the
  brightest tier and the emergent rule stops lighting crowns high on the right. Worth knowing: the
  brightest tier overshot contrast to 51.6 at first and had to come back halfway, since a lit stand
  should be foliage in sun rather than the second brightest thing in the frame after the tower.
  Also tried and reverted: removing the right near field's brighter leaf tier now the key is
  correct. It is still earning its place, and dropping it cost six points of p95.
- **sunside** — the map had been lopsided for several passes, the right running five to fourteen
  over at every height while the left ran under, and no amount of per crown material tiering moved
  it. The cause was the key's azimuth. At -26 degrees the lit face of each bank is the one turned
  toward the clearing, which for the right bank is the face we see and for the left bank is the
  face we do not, so the render was bright on the right and dark on the left by construction.
  Flipping the azimuth put the lit faces where the reference has them and took the worst cell from
  -16 to +11 in one change. Check the key direction before tiering materials to compensate for it.
- **wall** — the plinth was a clean untextured slab where the reference's is coursed. For banding
  the lateral stretch has to be small and the vertical one large: at 2.6 the bands came out finer
  than the surface grain and read as noise, at 7.5 they read as courses.
  Widening the wall was tried for the worst remaining cell and reverted. That cell is dark because
  bank foliage stands in front of the wall rather than beside it, so more width never reaches it
  and only lifted cells further out that were already right.
- **pads** — the corner cluster measured right and looked wrong: at that size the pads overlapped
  into one green sheet, where the reference's corner is just as bright but is plainly separate pads
  with dark water between them. More and smaller gets both, and they are a pale sage rather than
  the saturated lime they had drifted to. A cell can be the right brightness and the wrong picture.
- **emergent** — lit tone had only ever been given to the near field, but a forest catches light on
  whatever stands proud of its neighbours at any distance, and the reference's middle distance
  canopy is bright. Crowns riding high on their trunks are that emergent layer, which the
  separation pass had already made identifiable. The threshold matters: at twelve units above
  terrain it catches most of the bank and lifts the whole right side over, at nineteen it catches
  the few that should be lit.
  The bottom right corner was open water catching the lit bank's reflection; in the reference it is
  dark shoreline growth reaching in toward camera, which is now modelled. Watch where new geometry
  lands in the near/far material rules: the first attempt put that growth in crown_specs, where the
  near field rule gave it the brightest materials in the scene, the exact opposite of the intent.
- **litbanks** — the reference lights its right bank and near field hard while keeping the left
  dark, and crowds its bottom left corner with pads until it is the brightest cell in the frame at
  78. Matching all three brings contrast onto the reference exactly. Two things learned here: the
  lit stands were bare crown shells with no leaf geometry, so they read as smooth blobs sitting in
  granular foliage, which looked far worse than the colour did; and a pad cluster has to be sized
  to the cells it should cover, since at the bottom of frame the pond is only about 86 working
  units half width and a wider scatter spills into cells the reference keeps dark.
- **edge** — the worst cell in the map for several passes was the left edge at mid height, and the
  reference has a tree canopy there in full sun, pale and close to yellow green against near black.
  Nothing in the scene was that bright. Adding it took that cell from -18 to -4. The backdrop also
  gains a vertical gradient, since the map wanted it both darker at the top and lighter behind the
  middle distance, and the trunks widen with height because they had been tapering away below the
  top of frame and leaving sky in the corners where the reference has solid trunk.
- **rebalance** — a directional key changes what every surface receives, so several needed
  resetting after it: the treads take it face on and ran twelve over, while the backdrop and the
  middle distance canopy had been leaning on the fill that went away. The water and the pads were
  trimmed too at first and that was reverted: they are two of the few bright surfaces left, so
  flattening a couple of bottom row cells with them costs p95 across the whole frame.
- **highlights** — at a matching mean our p95 sat at 60 against the reference's 78: the same
  average spread over far fewer bright pixels, which is missing local contrast rather than wrong
  exposure. Every light here was a broad soft point, which lights every face of a crown about
  equally, so nothing had a lit side. A sun supplies that, and the lighting budget then shifts
  from fill to key: fill sets the median, the key sets the tail. Contrast goes 32 to 40 against
  the reference 46, and rms still improves. Note a sun's energy is irradiance, so the scene's
  times nine scaling does not apply to it.
- **tone** — the trunks came down again, the last surfaces the map had running bright. The tower
  was left alone: its cells read high because it covers more of them than the reference's tower
  does, not because its surface is brighter. Measured directly, our tower surface is already
  brighter than the reference's, and darkening it dropped p95 from 77 to 62.
- **separation** — every crown had sat directly on the terrain, making the bank one shell at one
  height. Crowns now ride trunks of differing height, which is what produces the gaps that read as
  separate trees. That opened the bank onto bare ground, so an understory fills underneath and the
  moss is darker: an opening between trees has to read as shadow, not as a lit surface.

## Lessons from those passes

- Exposure cannot fix this. Matching the reference mean by lowering exposure collapses the
  highlights with it: at -0.5 stops the mean was right and p95 fell from 78 to 61. The reference
  is dark *and* contrasty, which is a question of how much of the frame is mass, not of exposure.
- There is no local light in this scene. Every point light here is broad by construction, and
  three separate attempts to brighten one corner spilled across the whole frame and made things
  worse. Regional corrections belong in a **material**, which cannot spill. The lit shoreline
  stands carry their own lighter material and that is also what the reference shows.
- A light near the water mirrors into the pond and produces a hot spot; this is recorded twice now.
- Builders lay out in working units and multiply locations by three at the end. Positions worked
  out from the final frame therefore land three times too far out, silently doing nothing. Use
  `tools/probe_frame_cells.py` to get real coordinates instead of deriving them.
- Texture frequency has to be judged at full resolution. Noise pushed above the pixel rate averages
  to a flat surface, so a trunk can come out completely featureless; at the 600px preview fifty
  streaks read coarse and a hundred read as nothing, while at 1200 fifty is about right.
- Prefer Generated texture coordinates over Object where a feature count matters. Object
  coordinates carry the source mesh's own units, so the multiplier is guesswork.
- Check p95 and contrast, not just rms. The difference map averages each cell, so it cannot see
  local contrast at all and will happily reward a flatter picture: darkening the tower improved
  rms while dropping p95 from 77 to 62. The shore pass lost twenty points of p95 unnoticed for
  four passes because only the cell averages were being watched.
- When a detail layer grows, it takes over the tone of whatever it covers. Tripling the leaf size
  darkened every crown, because the leaf tones had been set back when a leaf was a single pixel and
  the shell underneath was what you saw. Near and far leaves now carry separate tones, and the near
  ones sit in the same range as the sunlit shell they cover rather than four times darker than it.
- `CATHEDRAL_QUICK_RES` keeps the quick loop at full width for texture work. Value questions can be
  answered at 600px in 24 seconds; frequency questions cannot be answered there at all.
- Free floating crown blobs were rejected once before and were re-created twice here: once as
  overhanging canopy in mid sky, once as trunk foliage. Both times the fix was the same, small and
  dense reads as a fringe, large and sparse reads as balls. Mass that reaches a frame edge or hugs
  a surface works; mass hanging in open air does not.

## Verification and delivery

After any edit, run the required repository suite in the affected checkout:

```sh
python3 -B -m unittest discover -p 'test_*.py'
git diff --check
```

Latest result: 24 tests run, one skipped. Those tests validate the website/tuning code, not Blender visual fidelity. Separately check Blender exits successfully, the framing assertions pass, and inspect the PNG with an image-viewing tool. Show the final PNG inline using its absolute path and link the editable `.blend`. Offline iteration does not itself deploy the website. The user requested a repository commit and push after the branch study. The Cathedral preview workflow is manual so archive pushes do not publish the earlier browser experiment.

Keep Lova's authorship block in the existing repository locations exactly as written. This handoff adds workflow notes, not a replacement authorship statement.

## Agreed next passes

The user approved the proposed sequence: forest mass refinement, architectural refinement (recessed 305, entrance, restrained stair variation), atmospheric refinement, then selective foliage realism. The stands study was reviewed positively. The architecture study was reviewed positively. The atmospheric/backdrop and first foliage passes were also reviewed positively. The latest delivered visual is the branch study. Start there; do not restart an earlier atmospheric pass. A useful next refinement is reducing the remaining rounded support shapes, guided by a fresh comparison with the reference and the user’s feedback. Keep the camera and proportions steady unless new feedback reopens them.

## Latest reference comparison

The exact index-2 reference was reopened for the backdrop pass. Its distant forest is much quieter than the modeled bands in our previous renders. Increasing haze alone did not adequately remove that pattern. The 28 distant stems are now hidden (retained for comparison); a remote procedural emissive surface with subtle elongated noise serves as the distant forest in this composition study. Be explicit about this approach: the main scene is modeled, while the far background is a procedural backdrop. Camera pose and lens remain fixed; far clipping increases to include the background. The first new near-bank light made a strong lower-right water reflection, so it was raised and reduced in radius before the final comparison.

## First selective foliage pass

Seven shared leaf meshes each contain 11,000 small cupped leaves sampled by triangle area from their corresponding crown mesh. These are instanced on crowns with working Y < 365 and |X| < 265, preserving the underlying planting/camera. Distant crowns remain simple. Each leaf uses one of four muted greens; the supporting core gets fine material bump. A dedicated RNG prevents template changes from moving the rest of the scene. The first full render took about 2m36s on CPU, at 1200px/64 samples. Surface detail is more visible on the nearer banks, but the rounded support shapes still read; do not call this finished realistic foliage. Inspect the detail crop before the next iteration.

The initial builder failed because a scalar named `area` shadowed the light helper. It was renamed `triangle_area`, and leaf winding was corrected before the successful render. Blender returned process exit 0 even for that Python exception, so inspect logs for exceptions and confirm a new image was actually saved.

## Branch cluster refinement

The branch study retains the accepted camera, architecture, planting positions, and backdrop. Each crown family now combines 7,500 surface leaves with up to 550 small branching shoots (downward-facing samples are skipped), each carrying 12 varied leaves. Thin tapered woody stems share the foliage mesh and use the bark material. Separate random generators keep the rest of the scene stable. The full 1200px/64-sample render completed in about 2m40s on CPU. The change is subtle at full-frame scale; inspect the matching close-up before assessing whether the rounded supporting masses need a larger structural change.

## Repository archive and Blender files

The accumulated work was committed and pushed to `codex/forest-cathedral` as `f46b7bd`; the GitHub checks workflow completed successfully. All `.blend` files use Git LFS; install Git LFS and run `git lfs pull` after cloning if they appear as pointer files. PNGs, scene builders, and handoff notes are ordinary Git files. Prior passes are preserved. The Cathedral preview workflow is manual and excludes `renders/`, tools, and the handoff from uploads. An archive push is not a production deployment. The main checkout contains a mirrored copy of these agent notes for discoverability.
