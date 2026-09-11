#!/bin/sh
# Serve the pass comparison page. Renders are symlinked in rather than copied, so the page always
# shows what is currently in renders/ and the worktree stays clean.
#
#   sh tools/compare_page/serve.sh [port]
#
# Flip mode is the useful one: side by side lets the eye adapt to each image separately, so a
# global value change reads as "both look about the same". Swapping in place makes it obvious.
set -e
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
port=${1:-5199}
ln -sfn "$root/renders" "$here/renders"
ln -sfn "$root/reference/midjourney-index2.png" "$here/reference.png"
echo "serving $here on http://127.0.0.1:$port/"
cd "$here" && exec python3 -m http.server "$port" --bind 127.0.0.1
