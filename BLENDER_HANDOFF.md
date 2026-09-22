# Cathedral Blender study — agent handoff

Updated 2026-09-22. Read this before continuing the cinematic forest work. This is a local, editable Blender study for Lova's portfolio, not yet a website asset or deployment.

## Concurrent work — 2026-09-17

Lova reports another agent will now make edits and has been told about this Blender work. Keep this task in the external-drive study; do not edit or deploy the WebGL site. Re-read Git state and shared handoff notes before writing, and merge any new notes rather than overwriting them. Renders remain local and ignored. The next check is a matching high-resolution crop of the79-thicket unthinned and lighter scenes.

## Matching high-resolution thinning check — 2026-09-17

Checkpoint committed as study `ebd73f5` and main handoff `d6a4153`; not pushed in this round. The subsequent detail comparison uses the79-thicket transitions and light scenes, both at2400px/64samples with top-down crop(.22,.55,.39,.73). Outputs are `cathedral-thinning-full-detail.png` (6m40s), `cathedral-thinning-light-detail.png` (5m10s), and `cathedral-thinning-detail-comparison.png` (full left, light right). Both are407x432 pixels. The lighter version retains fine branching and overlapping canopy structure in this crop, with slightly more air between leaves; retain it for continued distant foliage work. This is one local timing pair, not a controlled benchmark or proof about every region. All original blends remain intact.

Repeat saved-scene detail checks with `tools/render_cathedral_saved_detail.py --source STEM --output NEW_STEM --crop .22 .55 .39 .73 --resolution 2400 --samples 64` after Blender's `--python ... --` arguments. It refuses existing outputs and does not save over the source blend. Run one Blender process at a time. The left-edge continuation below has finished and passed isolation checks.

## Left-edge continuation — 2026-09-17

`--thicket-fill left-edge` preserves both previous fill patches and adds eight paired crowns around normalized(.20,.54). An initial request for sixteen eligible crowns failed before rendering because this bounded area contains only eight; the selection was narrowed instead of expanding its footprint. `cathedral-canopy-thicket-left-edge-study.png` and `.blend` completed at900px/32samples in10m22s. It has87 thickets and104 earlier branch replacements; thinning affects191 objects with the same718113 unique-template faces. Rebuild with the light-study recipe, changing only `--thicket-fill both` to `--thicket-fill left-edge` and using a fresh output name.

Full image and matching(.12,.46,.33,.65) crop show a subtle reduction in conspicuous rounded clumps at the left trunk/forest transition; retain as the next working scene. The reference still has much finer, more continuous forest texture, so this is incremental. Isolation validation passed: only eight original cores hidden and their paired leaf meshes replaced; all79 previous thickets,104 branch targets, camera, object transforms, landforms, lights and material assignments unchanged. No render jobs remain. This batch completed two matching detail renders and one full-frame refinement. Required tests pass24 with one skip; changed Blender scripts parse and diff checks pass. New work after checkpoint ebd73f5/d6a4153 is uncommitted, with no push or deployment. All render media remain local/ignored. Continue within the study and re-read shared notes before writing while the other agent works.

## Other-agent update reviewed — 2026-09-17

Fetched origin and reviewed `1fd7695` on `origin/colophon-and-funding-terms`. It adds COLOPHON.md, funding.json and .github/FUNDING.yml, and updates attribution text in AGENTS.md and README.md. It does not touch Blender tools, renders or this handoff. It remains on its separate remote branch; no merge, cherry-pick or deployment performed. The active main and study branches remain d6a4153 and ebd73f5 with our subsequent uncommitted Blender work.

## Right-edge continuation — 2026-09-17

`--thicket-fill edges` preserves the87 previous thickets and adds eight paired crowns around normalized(.79,.57). `cathedral-canopy-thicket-edges-study.png` and `.blend` completed at900px/32samples in16m23s. It has95 thickets and104 earlier branch replacements; thinning affects199 objects with unchanged718113 unique-template faces. Rebuild with the left-edge recipe, changing only `--thicket-fill left-edge` to `--thicket-fill edges`, with a fresh output name.

Full image and matching(.69,.48,.88,.68) reference/baseline/candidate crop show a subtle reduction in prominent rounded clumps without an obvious new bare-ground opening. Retain as the next working candidate, but this remains incremental: the reference forest texture is still considerably finer and more continuous. Isolation validation passed for only eight hidden original cores and replacement paired meshes; all87 prior thickets,104 branch targets, transforms, camera, landforms, lights and material assignments remain unchanged. Tests pass24 with one skip; changed scripts parse and diff checks pass. Blender completed normally; no render remains active. The host showed roughly15.9GB system-wide swap usage during the slow run, which may contribute to timing; do not attribute all swap to Blender. All media local/ignored, new source and notes remain uncommitted. No merge of the other agent's attribution branch, push or deployment performed.

## PR merge and checkpoint status — 2026-09-18

At Lova's request, reviewed PR1 (colophon-and-funding-terms): both checks passed, mergeability CLEAN/MERGEABLE, five attribution/support files only. Merged the exact reviewed head1fd7695 into main as d0d930fc17a1a2017c6aa624478a3547b976e1ec; GitHub confirmed MERGED at2026-09-18T17:43:29Z. The manifest contact remains TODO@threeohfivestudios.com; this was disclosed as a follow-up, not silently changed. Local scene-vegetation and forest-cathedral checkouts were not merged with main. No Blender file overlap.

The previous foliage work was committed and pushed as study f720403 and mirrored handoff c385bbb, including earlier checkpoints ebd73f5/d6a4153. Historical sections above describing that work as uncommitted or the PR as unmerged are superseded by this entry. New inner-bank scenes are saved but rendering is blocked by repeated exit137 interruptions; see the memory-limit entry below.

## Inner-bank experiment and memory limit — 2026-09-18

New `--thicket-fill inner` adds16 paired crowns each around(.37,.64) and(.63,.55), preserving all95 previous thickets for127 total. The900px/32sample build saved `cathedral-canopy-thicket-inner-study.blend`, but rendering exited137 without a PNG. A retry from that blend with compact BVH,128px tiles and two CPU threads saved `cathedral-canopy-thicket-inner-compact-study.blend` and also exited137 without a PNG. Treat both as unreviewed experiments, not accepted renders. Memory pressure is suspected, not proven solely by exit code; system-wide swap was about13.4GB during retry. Inspection found574 meshes,2898527 vertices,2362428 polygons, no meshes with zero users,18247 objects with578 hidden. Purging unused meshes was therefore not a meaningful remedy.

New optional `--compact-memory` sets compact CPU BVH,128px tiles and disables persistent render data. Blender documents compact BVH as lower RAM/slower rendering; auto tiling was already enabled and its toggle is deprecated. Do not claim a measured memory saving from these runs. A smaller `--thicket-fill inner-left` adds only eight crowns around(.37,.64), for103 total. Its compact-memory/two-thread render also exited137 without a PNG. All three saved blend files remain local. No render is running, and edges-study remains the accepted baseline. Further render retries are paused until host resource conditions improve or the scene memory cost can be reduced meaningfully. Do not silently promote an unrendered scene.


The saved inner-left scene passed isolation validation: only eight additional original cores hidden and paired leaf meshes replaced; all95 prior thickets,104 branch targets, object transforms, camera, landforms, lights and material assignments preserved. This is structural validation, not visual approval. Changed Blender scripts parse, required tests pass24 with one skip, and diff checks pass. New source/notes are uncommitted. PR1 merge and post-merge checks succeeded; no new render media or Blender source was pushed in this round.

## Successful post-restart retry — 2026-09-18

Hitch_07 remounted at the expected path; source and saved scenes accessible, Git state unchanged. Retried the saved103-thicket inner-left scene with two threads using render_cathedral_saved_detail.py, full-frame crop0 0 1 1, resolution900, samples32, output cathedral-canopy-thicket-inner-left-restart. Completed normally in9m34s. It inherits compact BVH,128px tiles and no persistent render data from the saved blend. No new blend was saved: the editable source is cathedral-canopy-thicket-inner-left-study.blend; the successful PNG has the restart suffix. All outputs remain local/ignored.

Matching reference/edges/restart crop(.28,.55,.45,.74) shows fewer conspicuous rounded clumps beside the left stair edge and no obvious new bare-ground gap. Retain the103-thicket version as the next working candidate; the larger127-thicket experiments remain unreviewed. Prior structural isolation validation already passed for these exact saved scene objects. This success supersedes the render blocker for the smaller scene, but does not prove memory issues solved: system-wide swap reached about11.3GB during this run. No render remains active. Required tests pass24 with one skip and diff checks pass. Source/notes since f720403/c385bbb remain uncommitted. No push or deployment in this round.

## Inner-bank continuation batch — 2026-09-18

User approved the103-thicket post-restart image and requested several further passes. New --thicket-fill inner-banks preserves103 targets and adds eight paired crowns around(.63,.55), for111 total. Cathedral-canopy-thicket-inner-banks-preview.png/.blend completed700px/16samples in6m00s. Crop(.54,.45,.73,.65) and full review retained openness without an obvious bare-ground gap. Since this preview is lower resolution than the900px baseline, do not infer fine-texture quality from that first comparison alone.

New --thicket-fill inner-rise preserves111 and adds eight pairs around(.36,.51), for119 total. Cathedral-canopy-thicket-inner-rise-study.png/.blend completed900px/32samples in9m33s. Full image and matching(.27,.42,.73,.67) reference/103-baseline/119-candidate crop show subtle reduction of rounded clumps beside the stairs; retain both additions as the working candidate. No obvious new ground exposure. The reference still has a finer and more continuous forest texture; this is incremental. Both scenes use two CPU threads and --compact-memory; generated leaf thinning affects215 and223 objects respectively with the same718113 unique-template faces. Larger127-target inner experiment remains unreviewed.

Rebuild from the inner-left recipe with --thicket-fill inner-banks or inner-rise, --compact-memory, the listed resolution/sample count, and a fresh output name. New tools/check_cathedral_thicket_step.py makes the earlier temporary isolation check repeatable: pass --baseline STEM --candidate STEM --counts OLD NEW after Blender's Python argument separator. Both103-to111 and111-to119 checks passed, allowing only new cores hidden and paired leaf mesh assignments; prior targets, transforms, camera optics, lights and material assignments preserved. This check does not hash mesh contents or shader graphs and complements visual review. The2400px/64sample right-inner crop(.56,.46,.72,.65), cathedral-canopy-thicket-inner-rise-detail.png, completed in5m40s (384x456 pixels). Fine leaves and branching hold up; older rounded foliage remains visible around the replacements. Retain the119-thicket scene. Detail rendering did not save a new blend or alter the source. Source and notes remain uncommitted, all media local/ignored.


This batch completed three renders: the111-target preview,119-target full study and high-resolution detail. No render remains active. Tests pass24 with one skip, changed Blender scripts parse and diff checks pass. All new media remain ignored. Next useful visual target is the remaining larger upper-bank clumps; inspect their actual objects before selection, since some are unpaired plinth planting rather than paired canopy. Preserve the approved open irregular structure and keep prior scenes intact. No commit, push or deployment in this batch.

## Fitted upper planting continuation — 2026-09-18

Final-camera ray probes of the119-thicket scene identified visible unpaired plinth planting020/038 on the left and063/054 on the right among the larger upper clumps. New --thicket-upper-plinth left/both selects those exact still-visible objects after the prior thicket selection, fits the existing small-crown mesh into their original local bounds and uses the corresponding left/right foliage palette. Original cores are hidden, transforms copied. Use with the established --thicket-fill inner-rise --thicket-plinth --thicket-fitted --thicket-right recipe, not as a standalone composition assumption.

Cathedral-canopy-upper-planting-left-preview.png/.blend completed700px/16samples in6m49s,121 targets. Cathedral-canopy-upper-planting-study.png/.blend completed900px/32samples in10m13s,123 targets. Both use two threads, compact-memory and leaf thinning. Left and both share the same807592 generated unique-template faces after thinning (1174648 before); thinning affects225/227 objects. Existing119 thickets and104 branching targets preserved.

Validation now supports unpaired fitted replacements: allows only selected core hiding plus the exact new replacement objects, verifies copied transforms and fitted bounds, retains prior-object/material/camera/light checks. Initial exact matrix assertion failed; measured max difference3.814697265625e-6 from Blender matrix decomposition, with exact local bounding extents. Only new replacement transform comparisons use absolute tolerance1e-5; existing-object transform comparisons remain exact. Both119-to121 and121-to123 checks passed. The full matching(.25,.35,.75,.51) crop shows a restrained reduction in solid upper clumps while keeping bank outline controlled; this is not a wholesale silhouette change. The2400px/64sample crop(.29,.36,.41,.50), cathedral-canopy-upper-planting-detail.png (288x336), completed normally in5m51s. Fine foliage holds its detail without obvious stretching; upper planting has more natural openings. Retain the123-target full scene, while recognizing this is a local change rather than a major silhouette revision. No new blend was saved for the detail crop. Source/notes uncommitted, media local/ignored.


This upper-planting batch completed three renders without interruptions. No render remains active. Required tests pass24 with one skip and diff checks pass. All new render media remain local/ignored, source and handoff changes uncommitted. No push or deployment.

## Full-quality and foreground exploration — 2026-09-18

User asked to continue autonomously until a meaningful review choice. Earlier notes warn that the reference also has rounded crowns, and surface granularity matters; avoid indiscriminately removing all rounded mass. Rendering the accepted upper-planting scene at1200px/64samples, two threads, inherited compact settings, as cathedral-canopy-upper-planting-full.png. Source remains upper-planting-study.blend. This quality-only render completed normally in20m39s. Full image reviewed: finer branching is clearer, while older rounded clumps remain. Retain it as the best full-quality image of the accepted123-target scene; no geometry or composition change and no new blend saved.

Prepared optional tools/cathedral_shore_shoots.py and --shore-shoots in the maintained runner. It adds one mesh,54 low curved blades in six edge patches, three new green materials; no new lights or changes to water settings, camera or existing planting. Foreground open center preserved by design. This remains an unaccepted experiment. The render wrapper /tmp/render_shore_shoots.py loads upper-planting-study.blend, verifies all preexisting object transforms/visibility/data names/material assignments and light energies/colors unchanged, adds shoots, saves a new cathedral-shore-shoots-study.blend and renders900px/32samples. The wrapper has now passed its isolation check: only the new972-vertex/432-face mesh added;748 vertices project into frame. Its900px/32sample render completed in10m00s. Full/crop review found the sparse plants read as isolated, arranged spikes; do not promote that version. Keep one Blender process at a time. All outputs local/ignored. Current optional code passes required tests24 with one skip and diff checks. No commit/push/deployment.

## Foreground tuft refinement for user review — 2026-09-18

The first shore-shoots-study is preserved but unpromoted. New optional --shore-shoot-style gathered (with --shore-shoots) keeps the original sparse recipe reproducible and instead creates112 shorter, more leaning blades in four irregular edge patches, with a1.6 base-color multiplier. Central channel remains open. New source helper signature add_shore_shoots(scene,gathered=False). /tmp/render_shore_shoots_gathered.py loads the accepted upper-planting-study source; it passed isolation for only one added2016-vertex/896-face mesh,1631 vertices projected in frame, all existing object descriptors and lights unchanged. Saved cathedral-shore-shoots-gathered-study.blend and its900px/32sample PNG completed normally in11m38s. Full image and matching foreground crop(0,.84,.3,1) reviewed: lower irregular tufts read more naturally than the sparse spikes, with open center preserved. Leave as a candidate for user review before extending foreground growth; accepted upper-planting scene remains unchanged. No new light or pond material change. All media local/ignored; no commit/push/deployment.


Three renders completed in this batch: quality-only1200px baseline20m39s, rejected sparse foreground10m00s, revised low tufts11m38s. No render remains active. User-facing review choice is restrained foreground vegetation versus the cleaner water edge; no additional forest-structure approval is needed. Preserve the open irregular forest preference. Tests pass24 with one skip, all modified/new Python sources parse and diff checks pass. New source and notes uncommitted; media local/ignored.

## Cloud benchmark prepared — 2026-09-18

User authorized trying the proposed cloud benchmark. Prepared renders/cathedral-cloud-benchmark-1200-64.blend from accepted upper-planting-study, preserving scene appearance with1200px/64samples/CPU/full-frame border matching upper-planting-full.png (local20m39s). Frame range restricted to1; relative output path; Blender5.2.1 LTS, Cycles, denoising on, AgX, lookNone, exposure0.1. Packed dependency audit reports no external files. Package76480034bytes, SHA25680add1e0863bf07d360668d59bfb298fbc8808eeef39d14dd4f5fa2d526a2413. Local manifest renders/cathedral-cloud-benchmark-manifest.json records settings; do not commit benchmark media or manifest. Source scene unchanged. No cloud upload, account creation, payment or render has occurred. RenderStreet login page opened for user sign-in; exact5.2.1 availability and job estimate remain unverified. Obtain a spending cap before paid submission. Foreground gathered tufts remain an unaccepted candidate. Resume at authenticated dashboard, verify compatibility and estimate, then compare returned image and total cost/time with local baseline.

## First cloud benchmark completed — 2026-09-20

User created RenderStreet account, chose on-demand and explicitly approved a $5 monitored budget for one benchmark. Uploaded the prepared76MB scene and saved job2856370 at https://my.render.st/job/2856370. RenderStreet defaulted to GPU, Blender5.2 (exact patch not exposed), Cycles,1200x1200,64samples,noise threshold0.01,one still frame. Launched after spending approval. Finished100%, elapsed2m53s, billed1m57s, finalprice$0.15; accountbalance$24.85 from$25.00. Interim estimates/balance fluctuated; use finalprice. About7.2x local20m39s elapsed, one uncontrolled CPU-local/GPU-cloud comparison, excluding prior upload. No subscription or extra credit purchase. Output listed1.75M PNG. Browser download attempts have not yet yielded a verified local artifact; visual parity remains unverified. Do not claim cloud image matches until inspected. No more paid jobs authorized by this single benchmark approval. Source geometry unchanged, foreground choice still pending. All previous local-media exclusions remain.

## Cloud workflow and cohesion candidate — 2026-09-20

User authorized continuing RenderStreet on-demand against existing credit, with agreed pause at$5 remaining; no top-ups or subscriptions. Benchmark finalbalance$24.85. User manually downloaded benchmark archive successfully after automated downloads in both browsers hit ERR_BLOCKED_BY_CLIENT. The cause is not isolated; automation involvement is suspected, not proven. Extracted benchmark PNG to /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2856370/cathedralcloudbenchmark120064_00001.png. Full image comparison showed close visual match to local1200px baseline, no obvious missing assets, framing or color shifts; no pixel-exact claim. Cloud downloads live outside Git at /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/<job-id>/.

New tools/prepare_cathedral_cohesion.py loads accepted upper-planting-study and saves renders/cathedral-forest-cohesion-cloud-v1.blend. Material-only experiment:129 canopy/leaf materials receive shared world-position noise(scale0.006,detail2,roughness0.6), grayscale multiply ramp0.68 at0.25 to1.06 at0.75. Existing color input preserved. Broad continuous variation aims to connect adjacent crowns; this does not change round geometry. Exact object transform/visibility/data-name snapshot unchanged. Camera/monument/lighting not edited.1200px/64samples,oneframe,GPU,self-contained dependencies. Source preserved, candidate unreviewed. Required tests24 pass with one skip.

Chrome automated upload failed with fileChooser.setFiles Not allowed; user given official extension file-URL-access guidance. In-app upload succeeded. Submitted on-demand GPU job2856378 at https://my.render.st/job/2856378, Blender5.2/Cycles. Finished100% in1m59s elapsed,1m41s billed, listedprice$0.13; displayed accountbalance$24.73 (rounding differs from subtracting displayed job prices). Output1.74M PNG awaits manual download and visual review. Review this single variable before a lighting pass. Manual Chrome download may still be needed. No commit/push/deployment.

## Automated FTPS retrieval verified — 2026-09-20

User completed one-time macOS Keychain setup for service monolith-renderstreet-ftps, account lova@threeohfivestudios.com. tools/download_renderstreet.py retrieves that credential privately through security, connects to official us3.render.st:51225 using verified explicit TLS and protected data channel, lists /output-renders and retrieves one job folder. --list authenticated successfully; --job 2856378 downloaded the full1200x1200 PNG to /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2856378/cathedralforestcohesioncloudv1_00001.png. Byte-count verification and SHA256 manifest saved beside it. Full image opens successfully. Browser download bottleneck is resolved through this supported alternate transport; original browser block cause remains unknown. No additional render charge. For subsequent completed jobs run python3 tools/download_renderstreet.py --job JOB_ID from study, with required external-drive/network permission. Existing files are refused rather than overwritten. Password is never printed or stored in source. Do not run Keychain lookup separately with output exposed. Outputs remain outside Git. Cohesion candidate is downloaded but no final keep/reject decision yet; inspect matching baseline before continuing lighting. No render running.

## Independent finishing batch — 2026-09-20

User requested several further passes. Reviewed full cloud cohesion image against benchmark and reference: restrained tonal integration, remaining rounded geometry unresolved; use cohesion as comparison base, without claiming major realism gain. New tools/prepare_cathedral_finish_passes.py loads this same base independently for three candidates. Edge-light scales open sky0.85,near bank opening1.65,left canopy opening1.25,stone light1.12. Stone-grain multiplies weathered monumental limestone with world-position noise stretched(.028,.028,.018),mapped0.72–1.15. Pond-ripple adds secondary world-position noise stretch(.055,.30,.055),bumpstrength0.22,distance0.18 layered over previous normal; preserves roughness0.30. All preserve object transforms, visibility and mesh assignments exactly; no camera/layout changes. All are1200px/64samples,GPU,singleframe,self-contained blends. Checks24 pass,one skip; no existing render overwritten.

Submitted jobs2856380(edge-light),2856382(stone-grain),2856384(pond-ripple), on-demandGPU$4.49/hour. All finished and downloaded through verified FTPS. Edge-light2856380:2m55s elapsed,1m47s billed,$0.13. Stone-grain2856382:2m12s elapsed,1m13s billed,$0.09. Pond-ripple2856384:1m53s elapsed,1m11s billed,$0.09. Listed batchtotal$0.31; displayed finalbalance$24.43 (rounded values differ from subtraction). No render remains running. Starting balance$24.73. Download each after completion via tools/download_renderstreet.py --job ID; compare full-resolution outputs before retaining/combining. No paid top-ups/subscriptions, pause before$5 balance. New outputs local/ignored; source uncommitted. No push/deployment.

## Finishing batch visual review — 2026-09-20

All three1200px PNGs downloaded and opened successfully from /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/{2856380,2856382,2856384}/. Each has byte-count/SHA256 download manifest. Compared full images and matched crops against cohesion2856378. Stone-grain is the most useful modest improvement: less uniform vertical mineral streaking, same silhouette. Retain cathedral-stone-grain-cloud-v1.blend as next working candidate, not explicit user approval. Lighting variant subtly brightens right foreground but does not sufficiently change depth; leave unpromoted. Pond normal change barely reads at this scale; leave unpromoted and preserve accepted0.30roughness. Do not combine rejected/marginal variants automatically. Next work should make a larger deliberate lighting/depth change or resolve older rounded forest geometry rather than keep accumulating tiny invisible changes. Camera and open irregular structure remain locked.

Diagnostic compare-lighting.png,compare-stone.png,compare-water.png outside Git show baseline left/candidate right; initial float-buffer comparison export brightened both sides and was regenerated using byte buffers. Judge color using original renders. Full-image mean absolute RGB changes vs cohesion approximately0.00364,0.000425,0.000091 respectively, in Blender image pixel values; these quantify subtlety, not aesthetic quality. No new cloud charges beyond three jobs. New builder and earlier sources/notes remain uncommitted; no push/deployment. Automatic FTPS retrieval removed manual download bottleneck for this whole batch.

## Depth and atmosphere diagnostics — 2026-09-20

User requested autonomous continuation until a meaningful visual choice. New tools/prepare_cathedral_depth.py builds two independent variants from stone-grain-cloud-v1: canopy key energy x1.8,open sky x0.55,pond opening x0.65,near bank opening x2.4,stone light x1.2,world lighting Background strength x0.55. Camera-visible Background.001 stays unchanged. Directional-depth preserves every object descriptor; atmospheric-depth additionally adds a finite distant volume at(0,1250,900),dimensions(3400,1700,2400),density0.00012. Existing geometry/camera unchanged. Both1200px/64samples,singleframe,packed,GPU. Completed RenderStreet jobs2856386(directional)2m59s elapsed,1m53s billed,$0.14;2856390(atmospheric)1m25s elapsed,1m18s billed,$0.10. Full PNGs retrieved automatically with manifests to cloud-renders/renderstreet/<ID>/ and visually reviewed. Directional lighting change remains modest; added volume softens the upper scene without enough useful separation. Leave both unpromoted pending the controlled comparison below. Settled balance$24.18 from$24.42 at batch start.

Inspection confirms saved light/world energy changes persisted and no animation actions override them. Existing material distance haze already contains a spatial density gradient and a linked emission gradient; do not assume the scene has no volume. Its atmosphere object spans(18000,9900,15000) at(0,3750,6000). Density is driven by generated Y/noise/height, not the unlinked default socket value. Map Range.003 maps the depth signal from0.0006–0.0027 to emission0–0.00021. This may flatten depth; diagnosis is an inference until the next controlled render. No compositor node group is assigned.

New tools/prepare_cathedral_haze_balance.py loads directional-depth, inserts x0.25 on the existing haze Emission Strength connection, leaves density and all object descriptors unchanged, and saves cathedral-haze-balance-cloud-v1.blend. Submitted job2856394 with the same1200px/64samples/singleframe settings; finished in1m43s elapsed,1m12s billed,$0.09. Full PNG downloaded through FTPS and reviewed. Reducing emission produces only a subtle change; it does not establish haze emission as the main cause of the flat appearance. Source files preserve earlier scenes and refuse output overwrite. Leave all three depth variants unpromoted; stone-grain remains the working candidate. Three-job batch cost$0.33; final displayed balance$24.09. No render remains active. The next useful choice is geometry/art direction: more irregular foliage overlap along the straight stair edges and less exposed rear-wall cornice, retaining camera, monument and open forest character. Pause for user preference before changing that established architectural/vegetation balance. Do not keep spending on barely visible lighting variants. Required tests pass24 with one skip in both worktrees; diff checks pass. All media stay ignored/outside Git. No commit,push or deployment in this round.

## Approved overgrown direction — 2026-09-20

User chose more overgrown stairs and rear wall, preserving camera, monument scale and an open central ascent. tools/prepare_cathedral_overgrowth.py loads stone-grain-cloud-v1, normalizes copies of four fitted thicket meshes, and adds21 irregular stair-edge clusters plus7 wall crowns. Stair placements follow measured150-tread bounds, alternating unequal gaps with seed30591. Existing object transforms/visibility/data names asserted unchanged; lighting/materials/camera untouched. Saved cathedral-overgrown-cloud-v1.blend. Job2856396 completed1200px/64samples in1m43s elapsed,1m12s billed,$0.09. Full PNG downloaded by FTPS. Stair edges are visibly interrupted while center stays readable; wall crowns look too wispy/perched, so first version not final.

Tools/prepare_cathedral_overgrowth_connected.py changes only7 new wall crowns: Z-25,Y-15,scaleZ x1.65,X x1.22,Y x1.15. Saved cathedral-overgrown-connected-cloud-v1.blend; job2856402 finished1m22s elapsed,1m12s billed,$0.09. Full image shows better connection but bare branches still too conspicuous against pale stone. A saved-scene comparison passed: exactly seven wall transforms changed, camera optics/matrix and all lights and other object descriptors preserved. Initial comparison held live matrix row references across file loads and failed; flattening to detached scalar tuples fixed the validator. No scene correction was needed.

Tools/prepare_cathedral_overgrowth_backing.py loads connected variant and adds7 lower foliage masses from the original four plinth planting meshes under the branch silhouettes. Each follows its wall crown with offset(0,-10,-22),scale multipliers(.93,1,.85). Saved cathedral-overgrown-backed-cloud-v1.blend; job2856404 finished2m02s elapsed,1m12s billed,$0.09. Downloaded and reviewed: REJECTED because original hidden plinth core meshes read as smooth pebble-like lobes. Do not promote backed-cloud-v1. Corrective tools/prepare_cathedral_overgrowth_leafy.py instead loads connected-cloud-v1 and uses normalized detailed fuller right shoreline crown geometry for the seven backings at the same locations/scales. Job2856406 completed2m53s elapsed,1m51s billed,$0.14; full PNG automatically downloaded and reviewed. Retain cathedral-overgrown-leafy-cloud-v1.blend as the next working candidate: detailed leaf backings remove the smooth blobs, soften the cornice, and connect to the upper planting; staggered stair growth breaks the edges while central ascent remains open. Some straight trim remains visible, and upper new foliage is brighter than surrounding crowns; this is a restrained overgrowth step, not a completed reference match. All four renders cost$0.41 total. Latest image: /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2856406/cathedralovergrownleafycloudv1_00001.png. No render remains active. Required tests pass24 with one skip in both worktrees; diff checks pass. New source/notes remain uncommitted. Saved-scene isolation passed: exactly seven objects added, all prior object descriptors, camera and lights unchanged. All three are isolated saved scenes,1200px/64samples,singleframe,GPU,packed,output overwrite refused. Latest settled balance before third job$23.91. All media remain ignored or in external cloud-renders/renderstreet/<ID>/ with FTPS manifests. No commit,push or website deployment.

## Overgrowth integration and remote forest — 2026-09-20

User requested continued autonomous passes. tools/prepare_cathedral_overgrowth_finish.py builds wall-tones and stair-patina independently from retained overgrown-leafy-cloud-v1. Both copy materials only on the7 wall foliage backings and multiply existing base color by(.58,.69,.63), preserving existing shader input links. Stair-patina additionally copies tread materials and applies patchy world-space dark green multiplication(.40,.62,.33), masked to absoluteX57–82 with maximum0.85 and noise scale0.065/detail3. All150 tread meshes/transforms and all scene object descriptors remain unchanged; center stays outside the stain mask. Both1200px/64samples,GPU,singleframe,packed. Jobs2856412(wall tones) and2856414(stair patina) completed and downloaded via FTPS. Wall tones:2m54s elapsed,1m53s billed,$0.14. Stair patina:1m56s elapsed,1m49s billed,$0.14. Full images reviewed: retain wall-tones as next working candidate because new upper foliage integrates better; leave stair-patina unpromoted because staining barely reads at this distance. Balance$23.40 after the two jobs. Start balance$23.68. New source/notes uncommitted; media remain local/ignored.

Inspection found28 old distant forest trunk objects intentionally hidden in the historical builders; a remote forest atmosphere backdrop replaced them. tools/prepare_cathedral_remote_stems.py prepares a separate comparison from wall-tones, unhiding existing stems01,05,11,23,24,27 and multiplying their X/Y scale by0.28, retaining their original height and position behind the monument. This keeps them subordinate to the two framing trunks. Saved cathedral-overgrown-remote-stems-cloud-v1.blend; job2856418 finished1m59s elapsed,1m12s billed,$0.09. Full PNG downloaded and reviewed: faint stems add slight depth, remain a comparison candidate. Settled balance$23.31. New tools/prepare_cathedral_remote_depth.py loads remote-stems and moves those same six stems Y-650, scales X/Y x1.5 (total0.42 of original width), retaining height. Saved remote-depth-cloud-v1; job2856422 completed2m51s elapsed,1m54s billed,$0.14. Full PNG downloaded and reviewed: stronger but still subdued vertical stems add depth behind the monument without changing its silhouette. Prefer this over the faint version, but pause for user choice on the more enclosed backdrop before further background development. Current retained material baseline remains wall-tones; remote-depth is the recommended visual candidate awaiting that choice. Quieter comparison is job2856418. All four renders this round cost$0.51; final displayed balance$23.17. No render remains active. Isolation confirms only the six background stems changed between distant variants. Tests24 pass with one skip in both worktrees, diff checks pass; source and notes remain uncommitted, all media outside Git/ignored. Latest candidate PNG: /Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2856422/cathedralovergrownremotedepthcloudv1_00001.png. Main composition remains fixed. Saved-scene isolation confirms exactly those six stems changed, with all other object descriptors, materials, camera and lights preserved. Do not promote unseen variants. Tests24 pass with one skip, diff checks pass.

## Rear ridge, stair diagnostic, and overhead canopy — 2026-09-22

Resumed from the recommended remote-depth scene after Lova asked to continue. `tools/prepare_cathedral_ridge.py` adds twelve detailed crown instances behind the rear wall; job 2857388 ($0.09) finished, but the change barely read through the existing haze. Inspection corrected an initial mistaken explanation that the backdrop plane was hiding them: the backdrop is farther away at world Y4350. `tools/prepare_cathedral_ridge_visible.py` moves only those twelve new crowns to Y1170–1320, raises and slightly enlarges them, and uses their original leaf materials. Job 2857394 ($0.09) produces a visible uneven rear forest line while keeping the central monument clear. Retain `renders/cathedral-overgrown-ridge-visible-cloud-v1.blend` as the new forest baseline. Its full PNG is `/Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2857394/cathedralovergrownridgevisiblecloudv1_00001.png`; preserve the quieter earlier candidates.

The stair-bevel material has only a narrow visible footprint. `tools/prepare_cathedral_stair_readability.py` instead copies basalt materials for the broad front and top faces of all 150 treads, without moving the stairs, camera, lights, or other objects. Job 2857402 ($0.14) shows only a tiny full-frame difference. Leave this material experiment unpromoted and avoid more small stair-surface changes unless the stair design itself is revisited.

The reference has dark foliage framing the upper corners. The saved scene already has 234 overhead canopy objects, but most project outside the current frame. `tools/prepare_cathedral_overhead_canopy.py` places six detailed crowns in front of the colossal trunks, with an open central corridor. Job 2857406 ($0.13) looked like six isolated floating trees with exposed stems; reject that first version. `tools/prepare_cathedral_overhead_canopy_connected.py` moves those six closer to the outer edges, widens and overlaps them, darkens the leaves, and uses a transparent object material only for their bark/stem slot. Job 2857410 ($0.13) gives a much more coherent dark canopy edge without covering the 305. Retain `renders/cathedral-overgrown-overhead-connected-cloud-v1.blend` as the current working visual candidate, not a final approved design. Full PNG: `/Volumes/Hitch_07/Blender/Data/cloud-renders/renderstreet/2857410/cathedralovergrownoverheadconnectedcloudv1_00001.png`. The reference still has richer fine forest texture and less uniform darkness around the large trunks, so further work should target those broad differences rather than repeat tiny material changes.

All five comparisons used packed Blender 5.2/Cycles scenes, RenderStreet On Demand GPU, one 1200x1200 PNG frame at 64 samples. All finished and were retrieved by the existing FTPS tool to Hitch; total listed job cost $0.58. The settled account balance is $22.59, well above the agreed $5 pause threshold. No render job remains active. The study builders preserve prior scene files and refuse output overwrite. Required tests pass 24 with one skip; source files parse and Git diff checks pass. Render PNGs and packed blends stay on Hitch and out of Git. Continue to show Lova actual full images for meaningful visual decisions. Source and notes from this round were pushed in study checkpoint `a7dac2b` and mirrored to the main checkout as `f51d12f`; the website remains untouched.

## Where work lives

- Main repository: `/Users/victoriarajaonarivony/Documents/monolith`.
- Active study worktree: `/Volumes/Hitch_07/Blender/Data/monolith-cathedral`, branch `codex/forest-cathedral`. This lives on the removable Hitch_07 drive; see "Drive location and repointing" below before assuming the path resolves.
- Historical foliage baseline: `tools/render_cathedral_foliage.py`, `renders/cathedral-foliage-study.png`, and `renders/cathedral-foliage-study.blend` in the study worktree.
- Historical Lace source scene: `tools/render_cathedral_lace.py`, `renders/cathedral-lace-study.png`, and `renders/cathedral-lace-study.blend`. The chain to it is branches, then value, mass, shore, trunk, plinth, foreground, crowns, separation, tone, highlights, rebalance, edge, litbanks, emergent, pads, wall, sunside, gradient, gaps, cling, columns, lamps, layers, softkey, vines, spill, taper, scale, shade, lace; each has its own builder and PNG/blend pair and they are all kept.
- Earlier1200px full-quality baseline: `renders/cathedral-ascent-lighting-full.png` and `.blend`, built by `tools/render_cathedral_study.py` with the camera, ascent and lighting flags documented below. Latest working candidate: `cathedral-canopy-upper-planting-study.png` and `.blend` (900px/32samples), retaining the asymmetric landforms,104 earlier branching crowns and123 thicket replacements, with distant leaf thinning and compact-memory settings. Inner-rise-study with119 replacements remains the prior comparison. The previous user-approved comparison is inner-left-restart.png, from inner-left-study.blend with103 thickets. Edges-study remains the previous accepted comparison. The87-thicket left-edge-study remains intact. The79-thicket light-study remains the prior comparison. Unthinned transitions-study and earlier47-thicket banks-study remain intact. Latest explicit user-approved comparison: `cathedral-canopy-thicket-fitted-study.png` and `.blend` with20 thickets. The user explicitly chose the more open, irregular structure, including the small wall opening. Covered-study is retained as the prior comparison. Banks-lean remains the unchanged foliage comparison baseline. Original full-template banks-study remains intact. Wider136-crown extended-lean-study is an unpromoted experiment. Earlier upper/both-patch scenes remain intact. High-resolution crop: `cathedral-branch-patch-detail.png` and `.blend`; that blend has render border enabled. Reflection experiment `cathedral-pond-reflection-study.*` was not retained. These new outputs stay local/ignored.
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

**The default is to check in, and it has not changed.** A later session ran long autonomous
stretches, twenty five passes without asking, and committed and pushed throughout. That was granted
explicitly and for that session only: Lova said to keep going without checking in and that they
would look in after a few hours. Do not read the size of that run, or the commit history it
produced, as standing permission. Ask, as below, unless told otherwise in your own session.

Lova explicitly prefers short, continual check-ins with visual evidence. Work in focused passes, explain what the next pass is testing, inspect the actual result, and send a render PNG/JPG, screenshot, or browser preview as appropriate. These updates give both user and agent shared context and support efficient decisions. Preserve prior versions for comparison and incorporate feedback before broadening a pass. Keep this workflow when another agent takes over; do not replace visual updates with text-only claims or silently bundle several major changes into one result. For this offline Blender work, show the actual render and link its editable `.blend`.

## Render storage policy — 2026-09-11

Lova questioned uploading every render. New generated PNG/JPG and Blender study outputs stay
local on Hitch_07; push source, configuration and notes only. `.gitignore` now excludes new
outputs under `renders/`. Existing tracked artifacts remain tracked and in Git history; do not
rewrite history or delete the archive without explicit direction. Stage exact source/note paths,
since ignore rules do not protect changes to already tracked outputs. The initial Sprays archive
was already pushed in `76758fd` before this correction (four PNGs and one Blender file).

## Transition patch continuation — 2026-09-17

User requested the next several passes. Added --thicket-fill right|both after all prior selection: right adds16 paired visible crowns around(.69,.64); both retains them and adds16 around(.31,.54). All47 previous thicket targets are retained. Cathedral-canopy-thicket-fill-right-preview completed700px/16samples in9m26s with63 targets; preview shows retained coverage around the foreground hero. Isolation passed:16 paired changes only, all47 prior thickets and104 earlier branch targets, transforms, landforms, camera, lighting and materials preserved. Cathedral-canopy-thicket-transitions-study completed900px/32samples in22m17s with79 targets. Matching full image/crop retain openness and reduce rounded transition patches; no obvious bare ground. Isolation passed for32 additions only, preserving all47 prior thickets and104 earlier branch targets, transforms/landforms/camera/lights/materials. Rendering was unusually slow: this host reports8GB RAM, system-wide swap usage about15GB during the job, and Blender remained active. Those observations suggest memory pressure but are not a controlled performance diagnosis. Replaced the planned detail crop with the memory experiment below. All media remain local/ignored; source/notes uncommitted.

## Distant leaf memory reduction — 2026-09-17

New tools/cathedral_leaf_thinning.py, opt-in --canopy-leaf-thinning, processes only the generated distant folded-leaf/thicket/fitted-thicket meshes. Removes every third four-triangle leaf fan, retaining all branches and all other leaf coordinates. Compacts unused vertices, preserves materials/smoothing/generated texture bounds and object overrides, then frees the unused generated source meshes in the new scene only. Archived blend files stay intact. The full-detail shoreline hero is excluded.183 objects share the affected meshes; unique-template face total falls1044665 to718113 (31.3%);81638 leaves removed across unique templates, not per-instance count.

Cathedral-canopy-thicket-light-study loaded transitions-study, applied this helper and rendered identical900px/32samples in9m07s versus the preceding22m17s. This is one pair of runs with system load uncontrolled, not a guaranteed speedup or memory benchmark. Full image and matching crop look very close at900px; retain light-study as the next working candidate, with heavier transitions-study preserved. Geometry digest verification proves all retained face coordinates/material indices/smoothing exactly match the expected source subset, all branches retained, original generated texture bounds, all transforms/material slots/camera/lights and foreground hero unchanged. Fine high-resolution leaf-thinning fidelity has not yet been checked; before judging final export quality, compare a high-resolution crop against the unthinned scene. Three successful renders completed this turn: lower-right preview,79-target transitions, and lighter scene. No render remains running. Required24 tests passed, one skipped. No commit/push or website deployment performed.

Rebuild light-study with the prior banks-study recipe plus --thicket-fill both --canopy-leaf-thinning, a unique output name,900px/32samples. No root extension or tiered experiment. Thinning is opt-in and all previous recipes keep their original geometry.

## Approved open structure: right-side continuation — 2026-09-17

User explicitly chose the open irregular fitted thickets and requested autonomous continuation. New --thicket-right preserves the20 accepted left replacements and adds12 paired plus3 unpaired visible right-bank crowns, selected around(.65,.44). Initial8-unpaired expectation failed because only3 were visible in the bounded region; no image was produced in that failed build. Updated to the actual3 rather than widening indiscriminately. Right replacements borrow tones from their own nearby paired crowns; original left tone selection remains unchanged. New total35 thicket targets, plus104 earlier branch targets. Cathedral-canopy-thicket-right-preview completed700px/16samples in6m24s. Visual review shows a blended right patch without an isolated-looking tree; isolation passed for15 additions only. Added --thicket-lower selecting12 paired crowns around(.30,.64), preserving all35 previous thicket targets. Cathedral-canopy-thicket-banks-study completed900px/32samples in10m24s;47 total thicket targets. Full image and matching lower-left crop reviewed: retains approved openness, finer replacement structure, no obvious bare-ground exposure. Isolation passed against fitted-study:27 additions only, original20 thickets and104 earlier branching crowns, all transforms/landforms/camera/architecture/lights/unrelated materials preserved. Retain banks-study as the next working candidate. Fitted-study remains the prior user-approved comparison. High-resolution cathedral-canopy-thicket-banks-detail rendered the same scene at2400px/64samples through normalized top-down crop(.22,.55,.39,.73), producing407x432 pixels in6m06s. Close-up confirms fine branches and interlocking smaller crowns; much full-preview softness is lost detail, although old rounded crowns remain around the patch. Detail blend has border/crop enabled; use banks-study blend for full renders. No render remains running. New renders local/ignored; source/notes uncommitted since e73e3bc.

## Smaller interlocking crown patch — 2026-09-17

User accepted covered-study landforms and requested autonomous continuation. Added tools/cathedral_thicket.py and --canopy-thicket. After landform placement, rays around(.35,.44) select12 visible paired old crowns, excluding hidden/previously replaced cores. Each receives a shared mesh comprising seven smaller, differently oriented branching crowns inside roughly the old envelope. New shoot_density=.12 on build_crown reduces per-tree shoot and trailing-branch counts; its default1.0 reproduces the original full mesh exactly (verified coordinates/connectivity against saved full scene, plus full/lean attachment hashes). Combined thicket mesh168826 vertices/129983 faces versus172764/134784 for the current lean hero template; finer structural scale without increasing per-replacement mesh size.

Cathedral-canopy-thicket-preview completed700px/16samples in5m33s. Preview has a finer edge with no obvious bare ground, but evaluate equal quality before promotion. Scene isolation passed: only12 new replacements; original104 targets, all transforms, landforms, camera, architecture, lights and unrelated material slots preserved. Cathedral-canopy-thicket-study completed900px/32samples in9m21s; isolation checks passed and matching crop shows only a small difference. The12 targets are smaller paired crowns, while prominent rounded silhouettes include separate plinth planting objects. Added --thicket-plinth to retain those12 and select8 visible unpaired planting objects in the same patch. New objects borrow nearby foliage materials and preserve original transforms; originals remain hidden. Cathedral-canopy-thicket-plinth-study completed900px/32samples in9m20s. Isolation passed, but matching crop shows excess wall exposure because the replacement envelope is smaller. Do not promote this unfitted version. Added --thicket-fitted to fit each of those8 meshes to its original local bounding dimensions while preserving their transforms; cathedral-canopy-thicket-fitted-study completed900px/32samples in8m17s. Validation confirms only8 replacement meshes fitted, with local bounds matching originals within.0001; all other assignments/transforms/materials/camera/lights unchanged. Full image and matching reference/covered/fitted crop reviewed: fine structure is more irregular but still opens a small gap near the wall. Matching outer bounds does not preserve dense silhouette coverage. The user subsequently explicitly chose to keep the more open, irregular structure. Promote fitted-study as the approved baseline; the small wall opening is accepted, not a defect to fill automatically. Preserve this preference when extending foliage elsewhere. Covered-study remains the previous comparison. Four renders completed (preview, paired12, added8plinth, fitted8); no render remains running. No root extension or tiered/extended experiments in this recipe. Outputs local/ignored; source/notes uncommitted since e73e3bc.

## Stronger asymmetric landforms and right-base correction — 2026-09-17

User requested autonomous continuation. Added --canopy-landform-strength (default1) and --canopy-landform-both. Both uses separate oblique right-bank ridges and valley farther back, keeping shore/stair margins. Strength1.45 preview cathedral-canopy-landform-both-preview rendered700px/16samples in4m05s; initial preview looked covered. Matching900px/32sample cathedral-canopy-landform-both-study completed6m15s and revealed a straight exposed edge at the right colossal trunk base. REJECT that version despite its improved image-grid RMS. Isolation checks passed for5207 vertical plant translations and2004 terrain vertices; camera/architecture/materials/lights unchanged. Visual evidence, not the metric, caught the defect.

Correction clamps right-bank displacement at zero, shaping a valley between raised ridges without lowering existing trunk coverage. Left retains strength1.45. Candidate cathedral-canopy-landform-covered-study completed900px/32samples in6m49s;1745 terrain vertices and4475 plants moved. Full image and matching right crop inspected, scene isolation passed, and all moved right-bank plants remain at or above their original height. Retain covered-study as the working candidate: stronger left contour and asymmetric raised right ridges with prior base coverage restored. Rounded crown texture remains unresolved. No render remains running. The original left-only landform and banks-lean baselines remain intact. New source and notes are uncommitted; no media uploaded.

## Optional lower right trunk extension: do not promote — 2026-09-17

A short straight-looking transition remained near the right trunk after coverage restoration. Initial visual diagnosis was a finite source trunk base. Tested --canopy-root-extension via tools/cathedral_root_extension.py: copy colossal trunk1 mesh, freeze its original generated texture bounds, extend only the bottom120-world-unit band downward up to180 units.96 vertices changed. Cathedral-canopy-rooted-study rendered900px/32samples in7m48s. Verification proves upper vertices exactly unchanged, original texture bounds, all transforms/materials/camera/lights preserved. However the image difference is very small. Surface probes at x=.86/.92/.98 and y=.50/.515/.53/.545 hit trunk above and foliage below, with foliage at all sampled .53/.545 positions. This does not establish a remaining open geometry gap; do not claim the extension definitively fixes the visual edge. Keep the extension as an optional experiment, not the new baseline. Current retained scene is covered-study. Further refinement should address the still-rounded crown silhouettes and transitions, not automatically deepen right-bank cuts or extend trunks again. All outputs local/ignored and notes/source uncommitted since e73e3bc. Four renders completed this turn (preview, both study, covered study, optional root study); no render is running.

## Connected left canopy landform — 2026-09-17

User approved the broader connected-hillside direction. New helper tools/cathedral_canopy_landform.py and opt-in --canopy-landform displace the terrain and vegetation together over a softly bounded left-bank region. Two oblique ridges and a shallow saddle replace a uniform shoulder, retaining shore/stair margins. Starts from accepted104-crown banks-lean baseline, without the unpromoted tiered/extended experiments. Camera, stairs, monument and lighting stay fixed. Build reports1203 terrain vertices and3195 plant objects moved vertically. Candidate cathedral-canopy-landform-left completed900px/32samples in8m49s. Full image and matching reference/baseline/landform crop inspected: modest improvement to the uneven sweep around the left trunk, with no obvious bare terrain or trunk-base gap. Rounded individual crown texture still remains; do not describe this as solved realism. Retain as the first landform candidate; banks-lean remains the comparison baseline. Isolation verification passed:3195 plant objects moved vertically only, copied terrain changed, all other transforms/data/material slots, camera, architecture and lights preserved. No render is still running. Next pass can strengthen selected ridge/valley separation or integrate crown silhouettes, but avoid assuming a numerical image-score change proves visual fidelity. No media enters Git. Latest changes are not committed; previous pushed checkpoint remains e73e3bc /43caf22.

## Pushed checkpoint and tiered crown trial — 2026-09-17

At the user request, committed and pushed source/notes as e73e3bc on codex/forest-cathedral and mirrored handoff43caf22 on scene-vegetation. This also pushed the earlier local92c2a3b/b9a69aa checkpoints. No new media staged or uploaded. Other untracked main-checkout b/ untouched.

Continued with opt-in `--branch-tiered` for banks-extended only. It retains all104 accepted crowns and changes the32 experimental crowns: individual branch groups flatten vertically to.62, widen1.06, narrow depth.94, and receive staggered heights. Leaf counts stay unchanged. `cathedral-branch-tiered-crop` rendered900px/32samples with top-down crop(.20,.34,.80,.70) in8m31s. Camera/lighting are unchanged. Isolation verification passed for all transforms/material slots/lights, the104 retained crowns and all unrelated scene data. Matching comparison cathedral-branch-tiered-comparison.png shows only a small improvement; the broader canopy still reads as rounded masses. Do not promote this experiment. The retained baseline remains cathedral-branch-banks-lean-study. Tiered crop blend has border/crop enabled; no render remains running.

A visual direction check is warranted before broadening changes: recommend shaping the hillside canopy as larger connected irregular masses, with deliberate gaps and lit ridges, rather than continuing small individual-crown refinements. Camera, monument and stairs should remain stable during that work. The tiered source changes and these notes remain uncommitted after the pushed checkpoint. All render outputs stay local/ignored. Required24 tests passed, one skipped.

## Lighter distant branching geometry — 2026-09-17

User explicitly authorized continued autonomous local work until a meaningful check-in is needed. Cloud rendering was discussed but deferred; no uploads, accounts or purchases. The drive remains mounted at the recorded path.

New opt-in `--branch-detail lean` keeps all32268 leaf placements and branch paths but uses four-point folded leaf rims and triangular branch sections for the distant replacement mesh. The shoreline hero retains full detail. Default full geometry was verified exactly against the prior saved mesh (vertex coordinates and face connectivity). Full/lean attachment hashes and leaf counts match. Triangles fall from277184 to140496 per shared template; vertices309452 to172764. `cathedral-branch-banks-lean-study` rendered900px/32samples in8m38s versus14m52s for the prior full-template run. This is an observed pair of runs, not a controlled hardware benchmark. Full image and equal-quality left crop look very close; retain lean for further distant-canopy trials. Scene validation confirms only104 leaf meshes changed: every transform, material slot, camera, light, support visibility and shoreline hero preserved. Fine high-resolution leaf silhouette fidelity remains untested.

New `--branch-patch banks-extended` preserves those104 targets and adds16 each around(.35,.55) and(.64,.46). Candidate `cathedral-branch-extended-lean-study` completed900px/32samples in10m29s. Isolation checks passed: original104 targets retained,32 additions only; camera, transforms, lights and unrelated data unchanged. Full image and comparison crop inspected. Upper-right expansion looks darker and softer at preview size. A2400px/64sample crop with bounds(.57,.38,.73,.53), saved as cathedral-branch-extended-right-detail.png/.blend, completed4m54s and confirms fine branching geometry but a dense dark crown mass. Do not promote the wider expansion yet; retain104-crown banks-lean-study as the working baseline and the136-crown version as an experiment. The next useful pass should vary crown shape and canopy separation rather than blindly expand the same template. Detail blend has render border/crop enabled. No render remains running. All outputs stay local/ignored, source is uncommitted. Required24 tests passed, one skipped.

## Bank patch continuation after local commit — 2026-09-17

User requested commit and a few more passes. Upper-edge source/notes committed as92c2a3b, main handoff b9a69aa. These commits were not pushed because this request asked for a commit only. Render files stayed local/ignored. Subsequent experiments below are uncommitted until the next checkpoint.

New `--branch-patch bank-left|banks` modes retain the previous72 targets, then select16 more visible crowns around normalized top-down(.24,.63), with banks adding16 around(.76,.64). Camera, terrain, architecture and shoreline hero are retained. Left candidate cathedral-branch-bank-left completed700px/16samples in6m33s;88 targets built. Validation preserves the original72, all transforms, camera and lights, with16 additional targets only. Preview shows no obvious ground gaps; defer fine-texture judgment until equal-quality rendering. Second candidate cathedral-branch-banks-preview completed700px/16samples in7m28s with104 targets. Validation confirms all original72 targets/transforms/camera/lights and unrelated data preserved, with32 additions only. Equal-preview-quality right crop compared against bank-left shows a less rounded, darker branch patch without an obvious ground gap. Third candidate cathedral-branch-banks-study completed900px/32samples in14m52s. Full equal-quality comparison against upper was visually reviewed: retain both bank patches as the new working candidate, with finer branching texture and no obvious exposed ground; improvement is local and much of the old rounded foliage remains. Final scene validation preserves all original72 targets, every existing transform, camera, lighting and unrelated scene data;32 added targets only. Both preview crop comparisons and the final full comparison are local/ignored. No render is still running. Rendering is now expensive enough that the next wider expansion should first test a lighter distant branch template against the current image quality, rather than multiplying the full shoreline hero mesh across the whole forest. The user considered running a WebGL agent concurrently, then explicitly put that work on hold. Continue only the Blender study unless told otherwise. If website work resumes, use separate worktrees; BLENDER_HANDOFF.md is the only mirrored main-checkout file.

## Return from break: upper-edge foliage continuation — 2026-09-17

Hitch_07 is mounted at the original path. The study checkout was clean at6192f8b and main handoff at3f4cd99. Saved full/crop images opened and cathedral-branch-patch-both.blend loaded18225 objects with48 retained targets. No worktree repair was needed.

The upper silhouette probe revealed two selection issues: viewport raycasts hit camera-invisible forest shadow flags, and some smooth upper-left shapes are plinth planting objects with no separate leaf layer. New opt-in `--branch-patch upper` preserves the exact earlier48 targets, then adds12 targets around(.30,.40) and12 around(.72,.43). Upper selection steps past camera-invisible/hidden objects and accepts plinth planting. Unpaired planting receives a new branch replacement object at the exact original transform, with leaf tones borrowed from the nearest selected paired crown; its old support remains archived but hidden. Newly created names are recorded in scene['branch_patch_added']. Old left/both modes retain their original selection behavior.

Candidate cathedral-branch-patch-upper uses the same shoreline-natural recipe and camera/ascent/lighting flags, with --branch-patch upper --resolution900 --samples32 (use spaced flags).72 targets built successfully. Render completed10m30s at900px/32samples. Equal-quality left close-up comparison shows fewer smooth bulbous silhouettes and finer irregular upper edges; retain upper as the working candidate. Validation confirms the original48 targets and all existing object transforms, camera and lights unchanged; only24 new targets differ, with11 new branch replacement leaf objects for unpaired plinth planting. The new objects reproduce original transforms within0.000007 matrix-element error after Blender decomposition; an initial bitwise-equality check was corrected to a measured0.0001 tolerance. All other existing data/material/visibility matches the both-patch baseline. Comparison file: cathedral-branch-patch-upper-comparison-crop.png. No render remains running. Fine-detail consistency across the rest of the hillside remains unfinished; expand in small visible patches rather than reverting to whole-forest shell warps. All render files remain local/ignored. No new commit/push requested after the pause checkpoint.

## Targeted branch crown patches — 2026-09-17

User requested commit/push, then several more passes. Source and notes checkpoint pushed successfully as35623e7 on codex/forest-cathedral; matching main handoff77af69f on scene-vegetation. Only seven source/note files entered the study commit, no new render assets. The user requested a commit/push and a break after these passes. The subsequent branch-patch source and notes are included in the pause checkpoint (see latest git log). Resume from cathedral-branch-patch-both, with the detail crop available for inspection; no render job remains in flight. Render assets stay local on Hitch_07.

New `tools/cathedral_branch_patch.py`, used by `--branch-patch left|both`, reuses `build_crown(...layered=True,natural=True)` from the successful shoreline hero. Raycasts through the final camera select frontmost paired crown/leaf objects around normalized top-down image anchors(.33,.48) and(.67,.53). Left selects12; both selects24 per side. The selected original support meshes are hidden; their existing leaf objects receive the branching crown mesh with original per-object material slots and transforms preserved. All surrounding vegetation, terrain and architecture remain unchanged. Selected names are stored in scene['branch_patch_targets'] for validation. This is built over shoreline-natural, without the rejected --canopy-detail experiments.

First `cathedral-branch-patch-left` rendered700px/16samples and passed isolation validation for12 crowns. Low-sample close-up is too soft for a final leaf-detail judgment, so compare at equal quality before promotion. `tools/compare_sprays.py` now supports `--crop X0 Y0 X1 Y1` with normalized top-down coordinates and writes a separate -comparison-crop PNG. Left inspection crop: .24 .38 .43 .63. Second candidate `cathedral-branch-patch-both` completed900px/32samples in7m38s. Validation passed for48 target crowns only, preserving every object transform, existing light and non-target object data/material/visibility. Equal-quality full comparison shows a subtle, more continuous local canopy texture without obvious exposed ground. Third pass `cathedral-branch-patch-detail` renders the same scene at2400px/64samples through `--render-crop .24 .38 .43 .63`, producing a456x600 crop without moving the camera; completed7m26s and passed the same scene validation. Close-up clearly shows finer leaf edges/overlapping branches beside still-smooth unmodified upper crowns. Retain both-patch as the new working candidate; older shoreline-natural remains intact. Next expansion should target remaining visible smooth crown silhouettes, keep ray-selected patches bounded, and verify transitions rather than replacing the whole forest blindly. The detail blend has border/crop enabled: use the full both-patch blend for normal renders, or rebuild without --render-crop. Never treat the cropped image as a full-scene preview. All new outputs remain local/ignored.

## Hillside canopy detail experiments — 2026-09-17

User authorized several more autonomous passes. New helper `tools/cathedral_canopy_detail.py` adds opt-in `--canopy-detail support|fine|broken|dense` to the maintained runner, over the shoreline-natural recipe. `support` changes only3461 paired hillside crown support materials (base color multiplier.38,roughness1), preserving transforms, leaves, ground and existing light/camera settings. `cathedral-canopy-support-study` rendered700px/16samples in3m55s, visually only a subtle change; rounded outlines remain. Scene comparison passed for all transforms/visibility, camera lens and lights. Reference triptych saved locally.

Initial dense leaf splitting (`dense`) replaces each of7500 broad four-face leaves per family with three smaller four-face leaves and preserves branching shoots. `cathedral-canopy-fine-study.blend` saved, but render was terminated with exit137 and no PNG, possibly memory pressure while another Blender process validated the saved scene. Do not call it a completed render. Validation itself passed for intended6922 canopy objects only. Avoid concurrent Blender renders/scene-loading validation on this machine for the heavier foliage work.

`fine` instead uses three triangular blades per old four-face leaf, reducing surface triangle count while preserving shoots. Candidate `cathedral-canopy-fine-light-study` is the lower-cost follow-up. `broken` additionally warps the upper parts of shell and leaves together, retaining the lower cover. The lighter fine pass completed700px/16samples in4m32s, but visual review found too much rounded support geometry showing through; do not promote it. Its scene validation passed with only6922 intended canopy objects changed. The third `broken` candidate restores more triangular leaf area (width.24 vs.14), disables support-shell specular response, and warps shell/leaf upper vertices together with the lower cover retained. `cathedral-canopy-broken-study` completed900px/32samples in5m59s. Saved-scene validation passed: only6922 intended canopy objects change data/materials; every object transform/visibility, camera lens and existing lights match shoreline-natural. Equal-quality reference/shoreline-natural/broken comparison was visually reviewed. The upper outline is less rounded, but directional ridges are too angular and the forest still lacks convincing fine branch structure. Keep this diagnostic rather than promote it; `cathedral-shore-natural-study` remains the working scene. Next pass should replace a small group of prominently visible hillside crowns with genuine branch-and-leaf geometry, using the successful shoreline hero crown as a starting point, before any broad rollout. Do not keep repeating whole-forest shell warps or merely increasing leaf counts. New PNG/blend files remain ignored/local; no commit or push requested.

## Foreground shoreline passes — 2026-09-17

The drive is mounted at its original path. The user authorized the next few passes without routine approval questions. `tools/cathedral_shore.py` adds opt-in foreground planting through the maintained runner. `--shore-colonies` preserves but hides the original250 scattered pads and adds953 leaves in six colonies fitted to the farther camera. Local diagnostic `cathedral-shore-colonies-study` (700px/16samples) places leaves in the correct foreground region but looks too evenly scattered.

`--shore-gathered` instead builds926 leaves in tighter asymmetric colonies, weighted toward the left, and adds one downward area light named `left foreground opening` (180000W,150-world-unit diameter). It preserves the open central approach and softer pond roughness.30. Candidate `cathedral-shore-gathered-full` uses the existing ascent-lighting-full recipe plus `--shore-gathered --resolution 1200 --samples 64 --output-name cathedral-shore-gathered-full`. All outputs stay local and ignored. The earlier broad colonies remain reproducible with their original flag.

Saved-scene validation passed: camera matrix/lens, every existing object transform, every existing light and pond roughness match ascent-lighting-full. Only the250 original pads change visibility; the colony mesh and foreground light are the only added objects. The prior full-quality baseline remains intact. The1200px/64sample render completed in8m18s. Visual review retained the tighter planting direction but rejected its extra light: it creates a broad pale reflection in the lower-right water. Corrected candidate `cathedral-shore-natural-study` adds `--shore-no-light` to the gathered recipe,900px/32samples. The corrected900px/32sample render completed in4m52s and was visually reviewed: retain its denser left-weighted planting with original lighting as the latest working study. It is a modest foreground improvement, not a full reference match. Existing broad water reflections remain; the extra light is absent. Saved-scene validation confirms camera, all existing transforms/lights and pond roughness unchanged. The previous1200px ascent-lighting baseline stays intact; the corrected planting has not yet been rerendered at1200px/64samples. Finer continuous hillside canopy remains a larger unresolved difference from the reference than shoreline detail.

## Sep17 remount and pond-reflection continuation — 2026-09-17

Hitch_07 is mounted at the original path. Full-quality PNG opens and both warm-preview/full Blender files load; the post-remount geometry/camera/light-setting verification passed. Repository tests passed24 with one skip. No worktree repair or rerender of the previous result was needed. This verifies the active study files, not the entire disk's health.

New pond experiment uses --pond-roughness .18 (previous .30) while preserving water color, transmission .22, IOR1.333, existing bump, camera, geometry and all lighting. Saves a copied pond material so prior studies remain reproducible. Flag requires a separate output name. Candidate `cathedral-pond-reflection-study` uses the latest full-quality recipe with resolution700/samples16. Isolation checks passed for scene transforms/lights and water settings. Review before adopting; greater reflectivity alone may not solve the reference's brighter, textured shoreline.

Pond preview completed in4m09s and was visually reviewed. Roughness.18 sharpens the amber lamp reflections into more conspicuous vertical streaks while leaving the missing shoreline texture unresolved. Do not promote this water setting: retain roughness.30 from `cathedral-ascent-lighting-full` as the current working candidate. Trial remains available as an optional flag/output for comparison. RMS5.250 vs full baseline5.707 is not enough to override the distracting reflections, especially with different sampling/resolution. The more useful next water task is brighter irregular shoreline/foreground texture and vegetation, not simply a glossier surface. Reference/full/trial comparison is `cathedral-pond-reflection-study-comparison.png`. Final24-test suite passed with one skip, diff check clean. No commit/push; render artifacts remain local/ignored.

## Autonomous connected ascent and lighting passes — 2026-09-16

User explicitly said to continue the next passes without checking in unless critical. For this session, that authorizes several focused tests without approval pauses; it does not authorize new pushes/deployment or change the local-only render policy. Preserve candidate outputs and report visual evidence at completion. Latest checkpoint remains fc4dbee /84e6d91.

Pass1: `--ascent-lift 70` via new `tools/cathedral_ascent.py`. Raises all150 steps proportionally from top450 to520, moves landing, intact lettering, entrance components, flanking walls/cornices and lamp assemblies with the ascent. The monument below z700 moves rigidly upward70; upper spires absorb the lift linearly, leaving summit1350 fixed. Nearby terrain and planted cover rise with a lateral/back falloff; plinth plants move with their walls. Giant trunks and the shoreline hero crown remain fixed. At the accepted camera position/lens47/tilt, projected top .08000, entrance base .52745, stair foot .89000 now match the intended broad landmarks. Checks confirm equal risers meet landing520, dark rear panel remains inside doorway, and camera/trunk/hero-crown/pond transforms are preserved. Local `cathedral-ascent-proportion-study.*` preview700px/16samples took3m19s; visually longer ascent and higher entrance without moving the summit. RMS5.660 vs framing5.874, mean47.293 vs47.395.

Pass2: `--canopy-shadows` via new `tools/cathedral_forest_light.py`. Adds two irregular overhead shadow flags, invisible to camera/diffuse/glossy/transmission/volume rays and visible to shadow rays. These are intentional cinematic light blockers, not new visible tree geometry. Existing exposure and light energies stay unchanged. Local `cathedral-canopy-shadow-study.*` preview took3m01s. Broad shadowing is a restrained improvement in massing; similarly lit rounded crowns still remain. Checks confirm existing objects/materials/lights/camera unchanged. RMS5.652 vs ascent5.660 is effectively unchanged; do not claim quantitative improvement from it.

Pass3: `--entrance-wash`, also in the lighting helper, initially adds a9000W disk-area light (size30, color1/.48/.23) at (0,960,500+lift), aimed at (0,992,490+lift). Preview `cathedral-warm-ascent-study` took3m06s. The crop showed a small circular hotspot rather than the reference's wider wash, so retain it as a diagnostic candidate. Geometry/other-light checks passed; RMS5.650 vs shadow5.652 is effectively unchanged. Full-quality refinement broadens disk size to75 and power to27000 using new --entrance-wash-size and --entrance-wash-power flags (defaults preserve the initial candidate).

All use `--variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-lens 47 --camera-waterline .89 --resolution 700 --samples 16 --output-name <unique stem>`, with successive flags as above. Comparison tool supports explicit --baseline-name and --render-name for each candidate. Keep helper modules with runner changes when committing; they are new local source files, not render artifacts. No commit/push requested in this continuation.

Full-quality candidate recipe: `render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-lens 47 --camera-waterline .89 --ascent-lift 70 --canopy-shadows --entrance-wash --entrance-wash-power 27000 --entrance-wash-size 75 --resolution 1200 --samples 64 --output-name cathedral-ascent-lighting-full`. Local PNG/blend names follow that stem. Saved-scene verification against the warm preview passed: all existing object transforms/materials, monument/stair/terrain meshes, camera and other light energies identical; only facade light power/size and render quality differ. Full render completed in6m25s and was reviewed after the Sep17 remount. The connected ascent and broad warm facade wash hold up at1200px/64samples. Canopy shadows remain restrained; rounded foliage repetition and flat-looking water remain visible limitations. Reference/framing/full comparison is `cathedral-ascent-lighting-full-comparison.png`; RMS5.707 vs earlier framing5.874, mean46.995 vs47.395 (different render quality, so small metric changes are not definitive).

## Compressed camera framing refinement — 2026-09-16

User authorized adjustments after reviewing the farther-camera result. Kept camera position (0,-1147.5,72) and all scene geometry fixed. New optional --camera-lens overrides focal length after distance compensation. Increased lens44.3975 ->47mm and solved upward pitch13.04179 degrees (previous13.9584) to retain stair foot at top-down fraction .89. Tower top now .08000 rather than .12492; base .56872 rather than .58472. This corrects excess headroom while preserving water coverage, but cannot independently align every reference landmark: the stair ascent still looks shorter and monument base lower than the reference.

Rebuild: `render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-lens 47 --camera-waterline .89 --resolution 700 --samples 16 --output-name cathedral-camera-framing-study`. Local outputs are `renders/cathedral-camera-framing-study.png` and `.blend`. Compare with `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-compressed-camera-study --render-name cathedral-camera-framing-study`, producing the reference / former / refined triptych.

Preview completed in 3m37s and was visually reviewed. Tighter framing is better balanced, with the monument filling more vertical space and water restrained. Remaining stair/monument proportion relationship is unresolved; do not claim a faithful recreation or silently promote this camera to every variant. Equal-quality RMS5.874 vs6.395, mean47.395 vs47.310. Saved-scene check: camera position, every non-camera transform/material/visibility, and terrain vertices preserved; lens47 confirmed. Repository suite24 tests passed, one skip. No commit/push requested this turn; new media remain ignored/local and prior scenes preserved.

## Drive remount and completed camera review — 2026-09-16

Hitch_07 returned at the original /Volumes/Hitch_07 path after premature ejection; no worktree repair needed. Latest PNG was opened successfully; lower-camera and compressed-camera Blender files both load, and non-camera object transforms/material assignments/visibility plus terrain vertices match. This verifies the study files used here, not the health of the entire drive. Repository tests passed (24 tests, one skip). Temporary verification script had been removed during restart and was recreated in /tmp.

Completed pending comparison `renders/cathedral-compressed-camera-study-comparison.png`: reference / lower-only camera / farther longer-lens camera. Visual judgment: longer lens narrows the stair approach and reduces excess foreground water, useful steps toward reference perspective. Monument sits too low relative to the reference, leaving extra headroom and a shorter apparent stair ascent; treat as a promising camera candidate, not final reference framing. Do not silently reshape the scene to compensate. All geometry remained fixed. Cell RMS 6.395 vs lower-camera7.088; mean47.310 vs45.452. These metrics do not establish a complete reference match. The PNG/blend survived and no rerender was needed. No commit/push in this continuation; latest committed checkpoints remain study fc4dbee and main84e6d91. Next user review should settle whether to retain the compressed perspective before further framing/proportion work.

## Farther camera / longer lens experiment — 2026-09-15

User suggested the reference looks farther away and zoomed in, discussed water coverage and perceived scale, then authorized a test. Keep all scene geometry/materials fixed. Retain camera z72 from the lower-camera candidate, move 25% farther from the monument facade at y990, and multiply the focal length by1.25: y=-720 -> -1147.5, lens35.518 ->44.3975mm. This is 25% more distance to the monument, not 25% more distance to the pond. Set upward pitch13.9584 degrees to project the stair foot at top-down fraction .89, reducing the excess foreground water from the lower-only camera test.

Run `render_cathedral_study.py -- --variant canopy-groups --camera-height 72 --camera-compression 1.25 --camera-waterline .89 --resolution 700 --samples 16 --output-name cathedral-compressed-camera-study`. New optional flags require a separate output name. Compression measures distance relative to fixed facade y990. Waterline solves pitch for the stair foot using the square camera projection; do not use that calculation unchanged for non-square renders or shifted cameras. No camera settings are claimed to reconstruct the reference's unknown original camera.

Local outputs: `renders/cathedral-compressed-camera-study.png` and `.blend`. Compare using `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-water-camera-study --render-name cathedral-compressed-camera-study`. Equal 700px/16-sample review, reference / lower-only camera / farther longer-lens camera.

Saved-scene verification passed: all non-camera transforms/material assignments/visibility and terrain vertices identical. New top-down frame fractions: tower top .12492, base .58472, stair foot .89. Monument height remains close to the earlier original camera (.4598 vs .4479 frame units), but placing the shoreline lower also puts the monument lower and gives extra headroom. Judge this tradeoff visually instead of claiming all reference framing landmarks match. No new commit/push requested in this continuation; media remain local/ignored.

## Lower camera / water proximity study — 2026-09-15

User requested commit/push and explicitly reopened camera height: viewpoint should be a little lower, closer to the water compared with the reference. Approved right-bank/canopy scripts and notes pushed as study `fc4dbee` and main mirrored handoff `84e6d91`; no render assets included. Earlier fixed-camera constraints do not prohibit this newly authorized camera study.

New optional `--camera-height` in `render_cathedral_study.py` sets absolute world camera z and requires a separate --output-name, preserving archived compositions. Run `--variant canopy-groups --camera-height 72 --resolution 700 --samples 16 --output-name cathedral-water-camera-study`. This lowers camera from world (0,-720,108) to (0,-720,72), retaining lens 35.518 and original tilt. Geometry, lighting, materials and both bank contours are unchanged. Working-scale height goes 36 to24. Do not describe this as an eye-level camera at the water surface; it is a one-third reduction in the elevated viewpoint.

Local outputs: `renders/cathedral-water-camera-study.png` and `.blend`. Compare with `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-canopy-groups-study --render-name cathedral-water-camera-study` for reference / previous / lower-camera at equal 700px/16-sample quality.

Saved-scene verification passed: only camera z changes; lens/rotation/horizontal location, all non-camera transforms, material assignments, visibility and terrain vertices match. Top-down frame fractions: tower top .0803 -> .0644, tower base .5282 -> .5083, stair foot .8882 -> .8332. This gives more lower-frame room to water and slightly less tower headroom without clipping it. Scene geometry remains fixed. New camera study is subsequent uncommitted work; outputs ignored/local, no deployment.

Preview completed in 2m57s and inspected beside the reference and previous camera. Lower viewpoint gives more presence to the water but increases the foreground pond area relative to the reference, and reduces monument headroom. Keep as a camera-height candidate for user review; do not claim the framing is now a closer reference match. Comparison cell RMS worsens 5.210 -> 7.088; mean 44.311 ->45.452. Possible follow-up, if user likes lower height: small upward camera tilt to recover framing/headroom while retaining the lower position. Do not silently adjust geometry to compensate. Exact output comparison is `renders/cathedral-water-camera-study-comparison.png`. Final checks passed (24 tests, one skip; diff check clean), and all new media remain ignored/local. Current camera experiment remains uncommitted after the requested checkpoint push.

## Canopy grouping shape experiment — 2026-09-15

After the user approved the right-bank pass, test crown grouping with both bank contours fixed. New `canopy-groups` variant inherits all right-bank-contour features and widens 1,684 actual colocated crown/leaf pairs. Selected working positions satisfy 65<abs(x)<235 and 35<y<300, radius>=4, with a conservative stair-clearance filter. A smooth spatial field varies local width from 1.15 to 1.65 and depth from 1.04 to 1.16, preserving every crown height and position. No crown is shrunk or removed; the goal is overlapping irregular groups without repeating the bare-ground failure of crown compression. The separate bright shoreline crown is untouched.

Run `render_cathedral_study.py -- --variant canopy-groups --resolution 700 --samples 16`. Local outputs `renders/cathedral-canopy-groups-study.png` and `.blend` remain ignored. Compare using `compare_sprays.py -- --variant canopy-groups --baseline-name cathedral-right-bank-contour-study` for an equal-resolution/equal-sample before/after comparison. This is shape review, not a final leaf-detail render.

Saved scene verification passed: exactly 3,368 foliage objects have expanded local x/y scales; all object positions, heights, rotations, material assignments and render visibility, plus camera and terrain vertices, match the accepted right-bank study. Repository suite passed (24 tests, one skip). No commit or push requested in this continuation; last checkpoints remain study e8bc1b1 and main e3f2396.

Visual review completed: 700px/16-sample render took 2m55s. Crowns overlap into broader clusters; ground coverage and the visible trunk runs are retained, but the change is modest and similarly lit clumps remain conspicuous. Keep as a candidate for user review, not an assumed final baseline. Do not keep increasing widths: next useful experiment is selective light/shadow grouping with geometry fixed, retaining the shoreline light anchor and avoiding previously rejected global haze/exposure changes. Comparison is reference / accepted right-bank / canopy-groups, saved as `cathedral-canopy-groups-comparison.png`. Equal-quality RMS 5.210 vs baseline 5.132; means 44.311 vs 44.393, so there is no whole-image numerical improvement to claim. Full detail requires a later higher-quality render. Final scene checks and 24-test suite (one skip) passed; renders/blends remain ignored local files and this pass is uncommitted.

## Right bank contour preview — 2026-09-15

User requested commit/push and continued work. Pushed approved left-contour scripts/notes as study `e8bc1b1` and main handoff `e3f2396`; no render assets included. Initial automatic approval review rejected the push as an unverified destination; read-only checks confirmed the existing user project origin `git@github.com:lrakoto/monolith.git` and previous authorized push, after which retry succeeded. No push remains blocked.

New subsequent local work: `render_cathedral_study.py -- --variant right-bank-contour --resolution 700 --samples 16`. Inherits all accepted left contour features. A separate shallower depression affects x>65, y85..395 in working coordinates, with maximum 32 working / 96 world units versus left 55 /165. Terrain and planting move together. Camera, architecture, giant trunks, accepted left bank and bright near shoreline crown remain fixed.

The first preview lowered too much outer bank and exposed the right trunk mesh's cut lower edge near the frame boundary. Rejected outputs are kept locally as `cathedral-right-bank-outer-edge-rejected.png` and `.blend`. The correction multiplies right deformation by a smooth outer taper from x180 to zero at x245, retaining the outside bank as trunk-base cover. Do not ignore or celebrate exposed cut geometry as greater trunk scale.

Current preview filenames: `renders/cathedral-right-bank-contour-study.png` and `.blend`. Compare with `compare_sprays.py -- --variant right-bank-contour --baseline-name cathedral-left-bank-contour-full`; the new optional --baseline-name preserves the former default and supports full-quality baseline filenames. These are 700px /16-sample composition studies; inspect full quality only after silhouette review.

Validation detail: initial camera/protected object and bounded terrain tests passed. Two old crown/leaf numeric suffixes (6493,6496) refer to unrelated objects hundreds of units apart, so their offset changes are not broken matching pairs. Validate actual colocated pairs and leave unrelated historical objects independently planted; do not snap by numeric name alone. All actual colocated pair offsets were preserved in the initial test. New work remains uncommitted for review, and renders remain local/ignored.

Corrected preview completed in 2m54s (initial 3m20s). Visual review: the hard outer trunk edge is covered again, while the inner bank permits modestly more trunk exposure. This is deliberately subtler than the left adjustment. Repeating rounded crowns still dominate the remaining reference gap. Corrected totals include both banks: 2,281 terrain vertices and 5,655 plant objects moved; incremental right side is 877 terrain vertices and 2,218 plant objects. Validation passed for protected scene transforms/materials, right-only bounded terrain changes relative to the accepted left bank, and actual colocated foliage pairs. Comparison RMS 5.132 vs baseline 5.213; means 44.393 vs 44.275. Different sample counts/resolutions mean these small numerical differences are not proof of improvement. Judge silhouette from the image; fine foliage needs full-quality review later. Suggested next focus: forest mass/light grouping with these bank contours held fixed, avoiding more fine leaf detail before broad crown repetition is resolved. Repository checks passed (24 tests, one skip); no new render files staged, and this new right-bank experiment remains uncommitted for review.

## Left bank contour full quality — 2026-09-15

Following positive user review of the contour blockout, keep its composition fixed and render at 1200px/64 samples. Rebuild with `tools/render_cathedral_study.py -- --variant left-bank-contour --resolution 1200 --samples 64 --output-name cathedral-left-bank-contour-full`. This preserves the 700px/16-sample blockout. Local outputs are `renders/cathedral-left-bank-contour-full.png` and `.blend`, both ignored.

The saved full-quality scene was checked against the blockout: all object transforms, material assignments, render visibility, terrain vertices and camera matrix/lens match. Only render quality and output path change. `tools/compare_sprays.py` now accepts `--render-name cathedral-left-bank-contour-full` alongside `--variant left-bank-contour --baseline left-bank-masses`, saving a separately named full-quality comparison. Default comparison naming is unchanged. No commit/push/deployment was requested for this continuation.

Full render completed in 7m23s and was visually inspected at 1200px plus the reference / former bank / new bank triptych (`cathedral-left-bank-contour-full-comparison.png`). The longer left trunk exposure holds up at full detail. Repeated rounded crown forms and some smooth ground pockets remain visible; do not describe this as a finished realistic forest. Cell RMS 5.213 vs former bank 5.074; means 44.275 vs 44.260, so the targeted silhouette gain is not a whole-image metric improvement. Proposed next pass: a shallower, separately shaped right-bank terrain/planting adjustment to expose the second trunk, preserving the bright shoreline crown and asymmetry. Keep camera, architecture and accepted left contour fixed, and preview composition first. Final checks: 24 tests, one skip, diff check clean; scene verification passed. Full PNG/blend and comparison remain ignored local files; no push this turn.

## Coordinated left bank contour blockout — 2026-09-15

User approved committing/pushing the previous work and continuing. Checkpoint pushed: study `c44c959` (including prior local bdf68c0) and main mirrored notes `7077ed2` (including faefb05). Only scripts/notes were added; render outputs remain local. The following new blockout is subsequent uncommitted work for visual review.

`tools/render_cathedral_study.py -- --variant left-bank-contour --resolution 700 --samples 16` inherits left-bank-masses and deforms the left terrain with a smooth saddle centered around working x=-150, y=165. Maximum drop is 55 working / 165 world units, tapering to zero at y=10/320 and toward the stair corridor x=-45. It lowers 1,404 terrain vertices and translates 3,437 canopy, fine foliage, shoreline, edge and plinth objects with the same field, preserving crown dimensions and overlap. Giant trunks and attached vegetation stay fixed. The new optional --samples controls saved scene render quality; normal full studies still default to 64, --quick still uses 16 without saving a blend.

Local outputs: `renders/cathedral-left-bank-contour-study.png` and `.blend`. This is a 700px / 16-sample composition preview, not the final leaf-detail render; took 3m01s. Full-frame reference / previous / new comparison: `renders/cathedral-left-bank-contour-comparison.png`, produced with `compare_sprays.py -- --variant left-bank-contour --baseline left-bank-masses`.

Visual result: noticeably longer visible left trunk, with planted volume retained and no new large bare patches like the rejected crown compression. Keep this as the next composition candidate for user review. Reference still has quieter, less repetitive forest masses. Do not judge leaf detail against the 1200px baseline using this low-sample preview. Whole-frame cell RMS 5.157 vs previous 5.074 is not evidence of better fidelity; the targeted improvement is trunk exposure.

Verification: camera matrix/lens, architecture, giant trunks, and right-side object transforms/material assignments preserved; terrain only moves down on the left, x/y unchanged within .001 world-unit floating tolerance. Existing canopy/fine-foliage offsets are preserved exactly within tolerance (some baseline pairs already have offsets; do not assume every pair has zero offset). Repository suite passed: 24 tests, one skip. Next: review this broad silhouette, then refine bank transitions or render at 1200px/64 samples if approved before adding foliage detail. No website deployment.

## Left bank massing experiment — 2026-09-15

New local variant `left-bank-masses` in `tools/render_cathedral_study.py` inherits the complete entrance-depth treatment. It modifies 1,755 left canopy lobes and their matching fine foliage. Broad positional shade groups use object-level private materials, with two retained light islands. The initial up-to-40% base-anchored crown compression exposed smooth terrain and was rejected after viewing the full render. Its PNG/blend are retained locally as `cathedral-left-bank-compression-rejected.*`. The corrected pass preserves every original crown transform and uses shading only. Terrain, giant trunks and their clinging vegetation are unchanged. Do not claim increased trunk exposure from this corrected pass; that needs a coordinated bank terrain and forest rebuild.

Full output: `renders/cathedral-left-bank-masses-study.png` and `.blend`; both are ignored local files on Hitch_07. Compare using `tools/compare_sprays.py -- --variant left-bank-masses --baseline entrance-depth`, which makes a full-frame reference / previous / new triptych. All other non-left-canopy object transforms and material assignments, camera matrix/lens, monument mesh, 150 stair meshes and right hero crown mesh were verified against entrance-depth. Repository suite passed (24 tests, one skip). No commit, push, or website deployment requested for this pass.

Visual verdict: corrected shading is quieter, but only a modest compositional improvement. Rounded repeating crowns and limited trunk exposure remain. Treat this as an experiment, not an automatically accepted baseline. Corrected render took 7m56s (initial compression 11m20s). Cell RMS 5.074 versus entrance-depth 4.872; mean 44.260 versus 45.157. Do not interpret the darker result as a better reference match on its own. All object transforms, including restored left canopy, were additionally verified identical. Next proposal: reshape a bounded left bank terrain section and its planting together, checking a low-cost blockout before full-quality rendering; preserve camera and architecture.

## Full composition review — 2026-09-15

Lova asked to review the full composition after the entrance pass. No scene changes were made.
Compared `reference/midjourney-index2.png` with `renders/cathedral-entrance-depth-study.png`.
A local overview is saved as `renders/cathedral-composition-review.png`: reference left, current
scene right. It resizes both existing images to 600px for a composition overview; judge fine
texture and tread detail from the original full-resolution renders.

The architecture/camera are a useful stable baseline. The largest visual gap is now the forest's
large-scale grouping and distribution of light. Current banks present many similarly readable,
high-contrast clumps; the reference uses broad dark masses, quiet intervals and selected lit crowns.
The giant trunks remain visible farther down the reference frame, which strengthens their scale.
Our high banks hide much of that vertical run. The stair corridor is also cleaner and more regular.

Recommended next focused experiment: the left forest bank. Selectively adjust canopy grouping,
height/occlusion and shading to reveal more of the giant trunk and create quiet dark areas with
few lit crowns. Keep camera, monument, trunk transforms, stairs and the right-side test crown fixed.
Inspect the baseline geometry before lowering groups: avoid exposing bare terrain or floating
crowns. Do not repeat the failed global height-dependent haze/albedo adjustments documented below.
Judge the whole frame and the trunk silhouette, not only small crops or global cell RMS.

Later priorities: stronger depth separation behind the monument while retaining trunk silhouette;
more natural pond reflections/ripples and irregular shoreline; a restrained warm entrance emphasis.
The reference pond/left shore catches more light, and its entrance warms the nearby facade. Current
warm lights are very small. These should be separate passes after the bank study, not bundled.
This review is a proposed direction, not approval to change all of those areas at once.

## Entrance depth / warmth — 2026-09-14

Lova approved a focused entrance pass. `entrance-depth` inherits inscription-stone, keeping the
opening geometry, camera, monument, inscription, stairs and crown. It darkens the rear panel,
moves the existing area light deeper to working (0,340,158.5), aims it at (0,332,150), and reduces
its energy to 55 percent. The existing luminous fixture moves to (0,340.4,159.9), becomes 60 percent
as wide and uses a copied emission material at 35 percent strength. Two small warm details sit
at (+/-1.7,340.85,155), sized (0.65,0.06,1.2). Multiply these coordinates by three for Blender.

The original rear panel was behind the boolean's back face. Its center is now working Y 340.99,
so its front face at 340.93 is visible ahead of the carved back at 341. The warm details are in
front of that panel. The opening dimensions remain fixed. The panel uses a private dark stone
material (0.006,0.007,0.006), roughness 0.92. The initial render before moving the panel is kept as
`renders/cathedral-entrance-depth-initial.png`; it is not the final reviewed output.

Run Blender with `tools/render_cathedral_study.py -- --variant entrance-depth`. Outputs stay local:
`renders/cathedral-entrance-depth-study.png` and `.blend`. Compare with
`tools/compare_sprays.py -- --variant entrance-depth --baseline inscription-stone`.

Final render: 1200px/64 samples, 3m03s. RMS 4.872 versus inscription-stone 4.824; mean
luminance 45.157 versus 45.200. The darker opening with smaller interior warm lights reads deeper
than the previous lit rear wall. Warm spill onto surrounding stone is still restrained compared
with the reference; assess the whole composition before another local doorway adjustment.
A ray check from inside the opening hit the dark rear panel, proving it is now visible. Saved
scene checks confirmed monument topology, step meshes, inscription parameters, crown geometry,
camera and non-entrance object transforms unchanged. The permitted changes are the rear panel,
entrance area light, luminous fixture, and two new interior warm-detail meshes. Tests pass
(24 run, one skip). The new pass remains local/uncommitted; no render assets were uploaded.

## Limestone inscription inset — 2026-09-14

Lova liked the monument weathering and asked to continue. The next focused profile is
`inscription-stone`, inheriting monument-stone. The carving already exists in the monument mesh;
the `305` curve is a thin inset at its back and previously used damp basalt with a front-face
darkening multiplier. This made the engraving read as dark printed lettering.

The new profile copies the curve datablock and replaces only its material with the monument's
weathered limestone. No change to text size, placement, extrusion, bevel, monument geometry,
lighting or camera. The existing recess must supply the depth and edge shading.

Run Blender with `tools/render_cathedral_study.py -- --variant inscription-stone`. Local outputs:
`renders/cathedral-inscription-stone-study.png` and `.blend`. Compare with
`tools/compare_sprays.py -- --variant inscription-stone --baseline monument-stone`; the helper
crops the inscription/entrance region, showing reference / dark inset / limestone inset.

Completed render: 1200px/64 samples, 3m02s. Whole-frame RMS 4.824 versus monument-stone
4.840; mean luminance 45.200 versus 45.179. The significant result is visual: a lighter inset
with shadowed edges now reads as carved limestone, closer to the reference's outlined recess.
The saved-scene check confirmed the text body, size, extrusion, bevel and offset, monument mesh
and topology, steps, crown branches, object transforms and camera unchanged. Only the inset
material changes. Comparison generation was briefly blocked by an approval-review usage limit,
then completed successfully when Lova asked to continue. This pass remains local and uncommitted;
no render assets were pushed. Repository tests pass (24 run, one skip).

## Monument limestone study — 2026-09-14

Lova asked to commit and continue. The stair-weathering checkpoint was committed locally as
bdf68c0 (study) and faefb05 (mirrored notes); it was not pushed. The next material-only profile is
`monument-stone`. It inherits the weathered stairs and hero-leafcraft crown, and copies the
limestone monument material so other surfaces remain untouched.

The existing fine stone noise gets two world-position color multipliers: soft mottling at scale
(0.045,0.025,0.018), range 0.88–1.12, and vertical weathering at (0.14,0.04,0.005), range
0.82–1.18. Both use Noise detail 3 / roughness 0.65 and remap 0.28–0.72. This tests visible
surface variation at the distant camera without displacement, geometry changes or new lighting.

Run Blender with `tools/render_cathedral_study.py -- --variant monument-stone`. Local outputs:
`renders/cathedral-monument-stone-study.png` and `.blend`. Compare using
`tools/compare_sprays.py -- --variant monument-stone --baseline stair-weathered`; this selects a
monument crop with reference / previous stone / weathered stone. Earlier variants remain intact.

The first test used stronger mottling (0.68–1.32 at uniform scale 0.025), with vertical detail at
(0.065,0.022,0.004), range 0.85–1.15. It looked too blotchy; its PNG remains locally as
`cathedral-monument-stone-initial.png`. The refined settings above reduce those patches and
emphasize finer vertical weathering. The initial full render's RMS was 4.839 versus 4.838 before,
which shows why whole-frame metrics alone cannot judge the material.

Refined full render: 1200px/64 samples, 3m00s. RMS 4.840 versus 4.838 before, mean luminance
45.179 versus 45.190. The refined surface has faint vertical marks without the initial blotches.
Actual saved-scene comparison verified monument mesh/topology, original 150 step meshes, crown
branches, transforms and camera lens unchanged. Tests pass (24 run, one skip). This new material
pass remains local and uncommitted. The next useful topic is the 305: it reads darker/flatter than
the reference despite existing carved geometry; inspect its inset surface and edge shading before
changing the model or camera.

## Restrained stair weathering — 2026-09-14

Lova approved the recovered stair definition and asked to commit/push and continue. The prior
leaf/stair work was pushed as 1aa9625 on codex/forest-cathedral; mirrored notes as 2207590 on
scene-vegetation. No render files were uploaded. The subsequent local experiment is
`stair-weathered`, based on stair-edges and the hero-leafcraft crown.

A world-position noise field varies the stone color across adjoining steps, rather than repeating
one texture on each riser. Base stone multiplies by 0.85–1.12; edge materials by 0.65–1.40.
The noise is stretched by (0.065, 0.024, 0.035), with detail 2 and roughness 0.6. Existing bevel
widths vary by a deterministic factor of 0.88–1.12. These are surface/color and modifier changes;
no new lights or emission, no camera change, and no change to the original step meshes or their
placement. Do not call the dark surface patches new cast shadows.

Run Blender with `tools/render_cathedral_study.py -- --variant stair-weathered`. Local-only outputs:
`renders/cathedral-stair-weathered-study.png` and `.blend`. The stair comparison is generated with
`tools/compare_sprays.py -- --variant stair-weathered --baseline stair-edges`. The output shows
reference / recovered stair edges / weathered stairs. Earlier variants remain reproducible.

The initial trial used body factors 0.72–1.04 and edges 0.40–1.12. It dimmed the recovered edges
too much (RMS 4.906 versus 4.836), so the factors above bring the variation back near the previous
average brightness. The first PNG is preserved locally as `cathedral-stair-weathered-initial.png`.

Corrected full render: 1200px/64 samples, 2m59s. Cell RMS 4.838 versus stair-edges 4.836; mean
luminance 45.190 versus 45.194, effectively unchanged. The edges retain definition with modest
variation along the flight. This is a small refinement, not a major reference-match improvement.
All original step meshes, crown branch geometry, object transforms and camera were verified
unchanged. Repository tests pass (24 run, one skip). The prior checkpoint was pushed; this new
weathering source/notes pass remains local and uncommitted for review. A useful next area is
the monument's overly clean surface rather than further small stair adjustments.

## Upper stair edges — 2026-09-14

Lova agreed to focus next on upper stair readability. The `stair-edges` variant uses the previous
hero-leafcraft crown, not the inconclusive grouped-spray experiment. It retains all 150 step meshes,
transforms, camera and overall proportions. The camera is below the upper tread surfaces, making
the risers and nosings important to the visible step rhythm.

The existing bevel grows from 0.035 to 0.20 builder units over steps 33–87, then stays constant.
At the scene's factor-of-three scale the maximum bevel width is 0.60 metres. Bevels use three
segments and a private worn-edge material: the basalt color ramp is multiplied by 1.8, and the
front-face multiplier rises from 0.44 to 0.80 for bevel faces only. This tests local edge definition
without new lights, emission, a camera change, or changing the underlying step dimensions.

Run `tools/render_cathedral_study.py -- --variant stair-edges` through Blender. Local-only outputs
are `renders/cathedral-stair-edges-study.png` and `.blend`. The comparison helper automatically
crops the stairs for this variant: `tools/compare_sprays.py -- --variant stair-edges --baseline
hero-leafcraft` (put the command on one line). It shows reference / previous scene / stair edges.

Full render completed at 1200px/64 samples in 3m03s. Cell RMS 4.836 versus leafcraft 4.943;
mean luminance 45.194 versus 45.085. The useful evidence is visual: step lines are now visible
much farther up instead of dissolving into a smooth ramp. The very top remains subdued, and
the steps are more regular than the reference. Possible later refinement is subtle worn-edge
variation and uneven shadowing while preserving the recovered definition. Do not change the
camera to solve that. Actual saved-scene verification confirmed all 150 original step meshes,
woody crown geometry, object placements/visibility and camera lens are identical; only stair
bevel modifiers and their dedicated materials differ. Tests pass (24 run, one skip).

## Grouped leaf sprays — 2026-09-14

Lova liked the leaf-shape pass and asked to continue. The next focused profile is `hero-sprig`,
which retains the leafcraft geometry and materials while moving the same leaves into three
irregular growth sprays along each existing twig. This tests whether spaces between sprays and
more exposed inner stems help the crown read as branching foliage rather than an even coating.
The crown mesh remains 309,452 vertices / 267,664 faces; no extra leaf geometry is introduced.

Rebuild with Blender: `tools/render_cathedral_study.py -- --variant hero-sprig`.
Local-only outputs are `renders/cathedral-hero-sprig-study.png` and `.blend`. Compare through
`tools/compare_sprays.py -- --variant hero-sprig --baseline hero-leafcraft`.
The `clustered` argument in `build_crown` defaults false, preserving the previous profiles.
An actual comparison of saved blends verified identical woody branch geometry, all object
placements/visibility and camera lens. Keep the wider forest unchanged until visual review.

Full render: 1200px / 64 samples, 2m53s. Cell RMS 4.974 versus leafcraft 4.943; mean luminance
45.155 versus 45.085. The changes are small and the image does not show a clear win. Keep leafcraft
as the working crown choice for now, retain this experiment for comparison, and avoid more tiny
leaf-placement iterations. The recommended next focused task is upper stair tread readability:
the reference retains tread detail up to the entrance, while our upper flight reads as a ramp.
Keep camera and overall architecture proportions fixed. Repository tests pass (24 run, one skip).

## Leaf shape and surface pass — 2026-09-14

Hitch_07 remounted at the expected path, the worktree remained clean at 832450a, and all required
inputs were accessible. The new focused variant is `hero-leafcraft`, based on hero-canopy.
It replaces the diamond leaf outlines with eight-sided tapered outlines, varied proportions,
independently sampled size variation and softer folds. Leaf faces are smooth shaded, and copied
leaf materials use roughness 0.62 rather than changing shared materials elsewhere in the scene.
A separate detail RNG preserves the original branch layout and leaf attachment sequence.

Use Blender with `tools/render_cathedral_study.py -- --variant hero-leafcraft`; local-only outputs
are `renders/cathedral-hero-leafcraft-study.png` and `.blend`. Compare with the last pass using
`tools/compare_sprays.py -- --variant hero-leafcraft --baseline hero-canopy`. Earlier variants
still use the original shape and materials. The runner default remains hero-canopy until review.

Verification against the two saved blends confirmed identical woody branch geometry, all object
placements/visibility, and camera lens. Only the crown's leaf geometry and its private leaf
materials change. The full mesh has 309,452 vertices / 267,664 faces, so assess visual improvement
against this increased cost before applying it more widely. No new assets should be pushed.

Full render: 1200px, 64 samples, 2m59s. Whole-frame cell RMS 4.943 versus hero-canopy 4.937;
mean luminance 45.085 versus 45.078. These values are effectively unchanged. Visually the leaf
shapes are less uniform, but the difference is subtle at the fixed camera and costs nearly twice
the crown face count. Do not automatically promote or distribute it. Further work should consider
branch overlap and shadowed clusters before adding more leaf geometry. All 24 repository tests
pass with one skip, and the three Python study tools parse.

## Irregular canopy pass — 2026-09-11

Lova liked the fuller crown and asked to continue. The next focused variant is `hero-canopy`,
now the runner default. It keeps the approved crown placement, camera, lights and lowered ground
cover, while broadening the branch groups, changing their density, varying the hanging trails and
correlating neighbouring leaf tones. `build_crown(..., layered=False)` preserves the previous
hero-crown version; `layered=True` produces this pass. No change has been spread across the forest.

Run `tools/render_cathedral_study.py -- --variant hero-canopy` through Blender. Local-only outputs
are `renders/cathedral-hero-canopy-study.png` and `.blend`. The render is 1200px, 64 samples,
2m40s. `tools/compare_sprays.py -- --variant hero-canopy --baseline hero-crown` makes the local
comparison image: reference / previous hero crown / irregular canopy. Whole-frame RMS is 4.937
versus 4.995 before; this is a small change, not proof of improved realism. The silhouette is wider
and has more shadow gaps; the individual leaves remain too crisp and uniformly sized compared
with the reference. That is a useful next topic for visual feedback.

The initial output name collided with historical `cathedral-canopy-study.*`. Both historical files
were restored from HEAD after preserving the new result under `hero-canopy`; the historical blend
was verified against its committed LFS SHA256. The new blend's embedded render path was corrected.
The runner now refuses any tracked output filename. To reproduce an archived profile, supply a
unique `--output-name`, e.g. `--variant sprays --output-name cathedral-sprays-rebuild`.
An actual Blender invocation verified the overwrite guard refused the archived name and left its
checksum unchanged. The 24 repository tests pass with one skip, and all three study scripts parse.

## Fuller shoreline crown experiment — 2026-09-11

Continue the maintained runner with `-- --variant hero-crown`. It loads Lace, hides the same 34
right-bank shoreline stands used in the Sprays test, and replaces them with one connected crown.
`tools/cathedral_crown.py` supplies the mesh: eleven unequal branch systems carry small cupped
leaves and irregular hanging trails. Geometry is shared within this one specimen, with 222,530
vertices and 171,079 faces. It is a focused test, not a replacement for the entire forest.

Placement is final Blender coordinates `(240, 54, 66)`, scale `(99, 75, 87)`. Camera, monument,
lights, world and foliage materials are inherited unchanged. The 98 original `canopy lobe`
objects in working X 55–115, Y -18–18, Z < 24 are reduced to 32 percent and lowered by 36 percent
of their old Z scale, along with their fine-leaf partners. This retains ground cover under the
hanging growth; fully hiding these clumps exposed a bare bank. `--retain-understory` keeps the
old foreground clumps to reproduce the first composition. Originals remain in the Lace source.

Do not use `cathedral-crown-study.*` for this work: that name belongs to an earlier archived pass.
New local-only outputs are `renders/cathedral-hero-crown-study.png` and `.blend`.
The first preview is `renders/cathedral-crown-quick.png`; the cleared-ground trial is
`renders/cathedral-hero-crown-quick.png`. The final full render retains low ground cover instead.
Run `tools/compare_sprays.py -- --variant hero-crown` through Blender to create a local
reference / Lace / new-crown crop at `renders/cathedral-hero-crown-comparison.png`.

The full 1200px/64-sample render saved successfully in 2m46s. Cell RMS is 4.995 versus Lace
5.019, effectively unchanged; mean luminance is 45.261 versus 45.022 (reference 45.894).
Visually the crown has fuller volume and hanging growth, but is still rounder and more uniformly
speckled than the reference. Next consider broader shadow pockets, a less regular outline and
more variation in leaf density. This is waiting for visual feedback, not approved for wider rollout.
All 24 repository tests ran successfully with one skip; the three study tools parse.

## Focused foliage experiment — 2026-09-11

Lova approved changing the iteration approach: preserve camera/proportions, test a representative
foliage patch, compare visually, and only then extend a successful treatment. The Lace scene is
still the comparison baseline; the new Sprays experiment is not yet approved for wider use.

`tools/render_cathedral_study.py` loads `renders/cathedral-lace-study.blend` and applies a named
variant, avoiding another copy of the full scene builder. Keep that source blend available through
Git LFS. It offers `baseline`, `sprays-flat`, and `sprays`; run with Blender's `--python` option,
then `-- --variant sprays`. Add `--quick` for 16 samples without saving a blend. Both modes default
to 1200px because this test concerns foliage structure. The normal run uses 64 samples and writes
`renders/cathedral-sprays-study.png` and `renders/cathedral-sprays-study.blend`.

Only the 34 positive-X `shoreline stand` objects and their matching leaf objects are replaced.
Their original geometry remains hidden in the saved experiment. Seven shared mesh families contain
connected woody scaffolds, twigs and cupped leaves; there is no opaque supporting crown shell.
Object placement, camera, architecture, other planting, materials and lights are inherited from Lace.
The runner asserts the expected target count and unchanged camera transform/lens.

The first quick test made overly flat shelves. `sprays-flat` retains that configuration and
`renders/cathedral-sprays-flat-quick.png` retains its preview. The second version spreads branches
through several heights and uses more leaders. It opens the silhouette but still reads too fern-like;
do not describe the experiment as finished realistic foliage or automatically spread it over the forest.

`tools/compare_sprays.py` runs under Blender and writes `renders/cathedral-sprays-comparison.png`:
reference on the left, Lace in the middle, Sprays on the right. It compares the same normalized
lower-right region at the final camera and prints whole-frame cell RMS as a regression check.
The source reference is a browser capture, so this is a visual guide rather than an exact pixel target.

Full render verification: 1200px, 64 samples, saved successfully in 2m47s. Whole-frame cell RMS
was 5.250 versus Lace's 5.019; mean luminance was 44.863 versus 45.022 (reference 45.894).
The crop shows the new sprays are more open but too sparse and horizontally layered, while many
unchanged foreground clumps still dominate the patch. This is an experimental asset, not a visual
win to promote. A better next test is one fuller, deliberately shaped crown with drooping edge
growth, keeping its overall footprint and checking its silhouette before distributing it.
Repository verification: 24 tests ran, passed with one skip; both new Python tools parsed.

## How the work is produced

Python scripts build the entire editable scene in Blender and render with Cycles. These are real 3D renders, not generated image edits. Blender runs as a separate background process; the user's open Blender window does not automatically update. Deliver both PNG and `.blend` links. Do not claim the visible Blender UI was used.

From `/Volumes/Hitch_07/Blender/Data/monolith-cathedral`:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup --threads 8 \
  --python tools/render_cathedral_lace.py
```

That is the current builder; each pass has its own, and the newest one is named at the top of this
file. A full pass is about 2m45 at 1200px and 64 samples on eight CPU threads.

Two environment variables shorten the loop while iterating:

```sh
CATHEDRAL_QUICK=/tmp/q.png CATHEDRAL_QUICK_RES=1200 <blender ...>
```

`CATHEDRAL_QUICK` redirects the render and skips saving a blend, and drops to 16 samples; with
`CATHEDRAL_QUICK_RES` left unset it also drops to 600px and takes about 24 seconds. Set the
resolution to 1200 whenever the question is about texture rather than value, because frequency
cannot be judged at 600 at all. **Confirm anything under about 0.2 rms with a full render**: at 16
samples the noise is worth about that much, and two passes were built on differences that turned
out not to exist.

`renders/cathedral-presentation.png` is a 1800px, 200 sample version of the latest pass for showing
the work; it took about 14 minutes on CPU and measures the same as the study render at rms 5.0. The
extra resolution is worth having for judging the canopy, which shows its lobe structure far more
plainly there than at 1200.

A filepath beginning `//` in Blender is relative to the blend file, not the working directory. The
blend files live in `renders/`, so `//renders/x.png` writes `renders/renders/x.png` and the render
still exits 0. Pass an absolute path or check where the file actually landed.

Blender 5.2.1 LTS is installed. CPU rendering works; Metal previously stalled while waiting for kernels. Sandboxed Blender previously crashed before executing the script, so background render commands have needed the normal `require_escalated` execution path. Do not bypass approval review or kill the user's GUI Blender. Poll the exact process/session started for this task, using waits of at most 30–60 seconds and concise progress updates.

Every pass renders at 1200 × 1200, 64 Cycles samples, denoising, AgX and 8 CPU threads. More samples improve noise, not proportions or modeling.

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
- `tools/compare_page/serve.sh` — serves every pass and the reference as one page on
  http://127.0.0.1:5199/, symlinking `renders/` in so it always shows what is there now. Its flip
  mode is the useful one: side by side lets the eye adapt to each image separately, so a global
  value change reads as "both look about the same", while swapping in place makes it obvious.

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

## The largest remaining difference

`tools/compare_band_map.py` shows where a given luminance band is over or under represented. Run on
the 40 to 50 band it puts almost the entire excess in the upper middle of the frame: our cells there
are 100 percent inside that band and the reference's are at zero. Cropping the reference explains
it. **It has no open sky.** Behind the monument is a dark wall of distant forest under faint vertical
streaking, with the tower bright against it. Ours is luminous haze sitting at about 45, and
attribution says the volume supplies that, not the backdrop.

Six full renders went into this without converging, so the findings are here rather than the fix:

- Cutting the volume's scattering albedo does fix the band: 40 to 50 goes from 30 percent to 13.9
  against the reference's 15.3, and 30 to 40 from 35 to 41.7. But it drops the whole frame by six,
  because that glow was carrying much of the level.
- Restoring the level with exposure undoes the gain exactly, pushing the same pixels back up into
  40 to 50. Exposure cannot separate the sky from the mass.
- Restoring it with the environment lifts the shadows but blows p95 to 85 against 78, because the
  environment lights the tower and the water along with everything else.
- **Thinning the haze density brightens the frame rather than darkening it**, by about five. The
  volume both scatters and attenuates, so less of it means less glow but also less extinction, and
  the distance comes through stronger. This is worth knowing before reaching for density again.
- The height falloff already in the material was set from generated z .27 upward, but a ray into the
  upper middle only reaches about .26 of the box, so it has never engaged at all.

That shape was then tried properly and **it should not be tried again**. Varying the scattering
albedo by height, full strength near the ground where it lifts the shadows and cut to a quarter up
where it reads as sky, works on every number that had been wrong: the 30 to 40 band goes from 35.5
to 43.1 percent, the median from 42.2 to 39.9 against the reference's 39.6, and p5 and p95 both hold.

Then look at the render. **The two colossal trunks disappear.** The haze glow behind them is what
silhouettes them, and without it they merge into the dark background entirely. They are the subject
of the reference and the whole point of the composition, so no histogram is worth that.

The upper frame reading as luminous haze rather than distant forest is therefore a known, measured,
and currently accepted difference. Any future attempt has to keep enough background luminance behind
the trunks to silhouette them: the glow is doing two jobs, and only one of them is wrong.

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
- **scale** — cropping both banks at matched magnification, the reference shows whole trees several
  hundred pixels across carrying fine texture, while ours showed rounded lobes about a hundred
  across: our crowns were too small for the trees they stand for, so their lobe structure was doing
  the reading. Larger and fewer keeps the coverage and pushes the lump scale above what the eye
  picks out, and the canopy texture is much closer for it.
  It costs rms, 5.0 to 5.2, and the cost is all in one place: larger crowns occlude each other less,
  so the upper right bank comes up about a dozen where the reference has it in deep shade. Tightening
  the lit tier there recovered half. Kept because canopy character is visible across the whole frame
  and a fifth of a point of rms is not.
- **lace** — the crown templates had not been touched since the branch study: a few large lobes
  packed close, which closes the silhouette. The reference's crowns are lacy, so the templates now
  carry many more, smaller lobes spread wider, with stronger displacement. The canopy stops reading
  as cauliflower and starts reading as forest. Opening the crowns lets background through and drops
  the mean by most of a point, so the tone comes back up to meet it; rms and mean absolute error
  both hold at their best while the median and contrast improve.
- **shade** — that residual is then closed. Raycasting the bright cells put them within a few dozen
  units of the `near bank opening` fill again, so it comes down a second time. rms returns to 5.0
  with the larger crowns kept and mean absolute error reaches 4.1, the best of the run. That fill
  has now been the cause twice: check it first when the right bank runs bright.
- **taper** — the trunk widening added in the edge pass is linear in height, so it arrives far too
  early and leaves the trunk bulging at mid frame. Cropping both there shows ours filling about two
  thirds of the cell against the reference's two fifths: the trunk is not too dark there, it is too
  wide. Squared, it still fills the top corners and leaves the middle alone. A small change, and
  the cell it was aimed at barely moved, but the geometry is right and p5 and p95 both improve.
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

## Where to pick up

Use `tools/render_cathedral_study.py` for the focused foliage experiment described above.
The unchanged comparison baseline is `tools/render_cathedral_lace.py`; Shade is historical.
The following recorded Shade measurements are context, not measurements of Sprays: rms 5.0 against the reference, mean absolute error 4.1, mean 45.6 against 45.9, p95 77.3
against 78.2, contrast 50.2 against 46.1. Keep the camera and proportions steady unless the user
reopens them.

The open items, in the order they look worth taking:

- **The upper frame.** Measured, characterised, and deliberately left alone; see "The largest
  remaining difference" above, including why the obvious fix costs the trunks.
- **Contrast is about four over**, entirely through the shadows: p5 sits at 27 against 32. Every
  global lever for that has been tried and the results are recorded in "Lessons from those passes".
  A local one might still exist.
- The canopy templates were opened up in the lace pass and now read much closer. What is still
  visibly different is the very edge of each crown, which the reference breaks into individual
  sprays rather than a continuous fuzzy outline.
- The stair treads stop reading about sixty percent up; the reference keeps them to the top.

## Historical: backdrop pass reference comparison

The exact index-2 reference was reopened for the backdrop pass. Its distant forest is much quieter than the modeled bands in our previous renders. Increasing haze alone did not adequately remove that pattern. The 28 distant stems are now hidden (retained for comparison); a remote procedural emissive surface with subtle elongated noise serves as the distant forest in this composition study. Be explicit about this approach: the main scene is modeled, while the far background is a procedural backdrop. Camera pose and lens remain fixed; far clipping increases to include the background. The first new near-bank light made a strong lower-right water reflection, so it was raised and reduced in radius before the final comparison.

## Historical: first selective foliage pass

Superseded by the crown, separation and scale passes. Kept for the failure modes it records.

Seven shared leaf meshes each contain 11,000 small cupped leaves sampled by triangle area from their corresponding crown mesh. These are instanced on crowns with working Y < 365 and |X| < 265, preserving the underlying planting/camera. Distant crowns remain simple. Each leaf uses one of four muted greens; the supporting core gets fine material bump. A dedicated RNG prevents template changes from moving the rest of the scene. The first full render took about 2m36s on CPU, at 1200px/64 samples. Surface detail is more visible on the nearer banks, but the rounded support shapes still read; do not call this finished realistic foliage. Inspect the detail crop before the next iteration.

The initial builder failed because a scalar named `area` shadowed the light helper. It was renamed `triangle_area`, and leaf winding was corrected before the successful render. Blender returned process exit 0 even for that Python exception, so inspect logs for exceptions and confirm a new image was actually saved.

## Historical: branch cluster refinement

Superseded. The leaf counts and sizes quoted here are no longer current; see the crowns pass.

The branch study retains the accepted camera, architecture, planting positions, and backdrop. Each crown family now combines 7,500 surface leaves with up to 550 small branching shoots (downward-facing samples are skipped), each carrying 12 varied leaves. Thin tapered woody stems share the foliage mesh and use the bark material. Separate random generators keep the rest of the scene stable. The full 1200px/64-sample render completed in about 2m40s on CPU. The change is subtle at full-frame scale; inspect the matching close-up before assessing whether the rounded supporting masses need a larger structural change.

## Repository archive and Blender files

The accumulated work was committed and pushed to `codex/forest-cathedral` as `f46b7bd`; the GitHub checks workflow completed successfully. All `.blend` files use Git LFS; install Git LFS and run `git lfs pull` after cloning if they appear as pointer files. PNGs, scene builders, and handoff notes are ordinary Git files. Prior passes are preserved. The Cathedral preview workflow is manual and excludes `renders/`, tools, and the handoff from uploads. An archive push is not a production deployment. The main checkout contains a mirrored copy of these agent notes for discoverability.
