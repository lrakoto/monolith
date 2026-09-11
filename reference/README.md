# Reference

`midjourney-index2.png` is the target for the Cathedral study: index 2 of
https://www.midjourney.com/jobs/1d1707f0-f59c-4585-9c60-3d25c745643c, Lova's own
generation, captured from the page because ordinary fetching of the asset fails.

It is a browser capture rather than the original file, so it carries a few percent
of jpeg and display profile error. Every gap that has mattered so far is far larger
than that, but do not chase its last digit.

The comparison tools in `tools/` all take it as their first argument and are
useless without it, which is why it lives here rather than in a scratch directory:

    blender --background --factory-startup --python tools/compare_diff_map.py -- \
      reference/midjourney-index2.png renders/cathedral-foreground-study.png
