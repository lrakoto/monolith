# Cathedral Blender study — agent handoff

Updated 2026-09-10. Read this before continuing the cinematic forest work. This is a local, editable Blender study for Lova's portfolio, not yet a website asset or deployment.

## Where work lives

- Main repository: `/Users/victoriarajaonarivony/Documents/monolith`.
- Active study worktree: `/private/tmp/monolith-cathedral`, branch `codex/forest-cathedral`.
- Current reviewed baseline: `tools/render_cathedral_foliage.py`, `renders/cathedral-foliage-study.png`, and `renders/cathedral-foliage-study.blend` in the study worktree.
- Latest generated pass (awaiting user review): `tools/render_cathedral_branches.py`, `renders/cathedral-branch-study.png`, and `renders/cathedral-branch-study.blend`. Shared crown templates now include small woody shoots with varied leaf directions. `tools/render_cathedral_branch_detail.py` produces the matching `renders/cathedral-branch-detail.png`.
- Iteration history and rebuild notes: `renders/README.md` in that worktree.
- Source meshes: `assets/cathedral/cathedral-trunks.blend`.

Run `git log --oneline -5` and `git status --short` in the worktree before assuming its state. The study archive was committed and pushed as `f46b7bd` on `origin/codex/forest-cathedral`; GitHub checks passed and all 19 Blender files uploaded through Git LFS. Check current branch status before assuming later work is committed. Do not clean untracked files or assume the main checkout contains the study. The unrelated main-checkout `b/` directory belongs to other work. The worktree also contains earlier website edits and preview configuration; this Blender task is not permission to publish those. The `/private/tmp` path is not durable archival storage; preserve or migrate the full study with explicit scope before cleaning it.

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

From `/private/tmp/monolith-cathedral`:

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
