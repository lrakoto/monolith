# Cathedral Blender study — agent handoff

Updated 2026-09-10. Read this before continuing the cinematic forest work. This is a local, editable Blender study for Lova's portfolio, not yet a website asset or deployment.

## Where work lives

- Main repository: `/Users/victoriarajaonarivony/Documents/monolith`.
- Active study worktree: `/Volumes/Hitch_07/Blender/Data/monolith-cathedral`, branch `codex/forest-cathedral`. This lives on the removable Hitch_07 drive; see "Drive location and repointing" below before assuming the path resolves.
- Current reviewed baseline: `tools/render_cathedral_foliage.py`, `renders/cathedral-foliage-study.png`, and `renders/cathedral-foliage-study.blend` in the study worktree.
- Current latest pass: `tools/render_cathedral_plinth.py`, `renders/cathedral-plinth-study.png`, and `renders/cathedral-plinth-study.blend`. The chain to it is branches, then value, mass, shore, trunk, plinth; each has its own builder and PNG/blend pair and they are all kept.
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
- `tools/probe_frame_cells.py` — raycasts chosen cells and reports what geometry is behind them
  in world coordinates. Use it before placing anything; see the units lesson below.

The working loop is a quick render at 600px/16 samples through `CATHEDRAL_QUICK=<path>`, which
takes about 24 seconds against 2m45 for the full pass, then the diff map, then a full render only
once the numbers and the image both look right. The reference itself is a browser capture of the
midjourney page, so it carries a few percent of jpeg and display profile error; the gaps that
matter here are much larger than that, but do not chase its last digit.

**rms is a guide, not the verdict.** Two separate passes scored better while visibly getting
worse: a pond that measured correct and read as a flat mint slab, and trunk foliage that scored
8.3 while reading as balls floating off the silhouette. Always look at the render as well.

## Value and structure passes

Error against the reference went from rms 10.1 to 7.9 across five passes, all kept:

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
