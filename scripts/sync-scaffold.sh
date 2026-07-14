#!/usr/bin/env bash
# Sync the root framework sources (templates/, prompts/, guides/) into the
# scaffold's bundled copy at scaffold/.ai-framework/.
#
# Usage:
#   scripts/sync-scaffold.sh           # regenerate the scaffold copy
#   scripts/sync-scaffold.sh --check   # exit non-zero if the copy has drifted (CI / pre-commit)
#
# scaffold/.ai-framework/README.md and VERSION are maintained by hand and are
# never touched by this script.
set -euo pipefail
cd "$(dirname "$0")/.."

DIRS=(templates prompts guides)

if [[ "${1:-}" == "--check" ]]; then
  status=0
  for d in "${DIRS[@]}"; do
    if ! diff -rq "$d" "scaffold/.ai-framework/$d"; then
      status=1
    fi
  done
  if [[ $status -ne 0 ]]; then
    echo "Drift detected between root sources and scaffold/.ai-framework/ — run scripts/sync-scaffold.sh" >&2
  fi
  exit $status
fi

for d in "${DIRS[@]}"; do
  rm -rf "scaffold/.ai-framework/$d"
  cp -r "$d" "scaffold/.ai-framework/$d"
done

echo "Scaffold synced: ${DIRS[*]} -> scaffold/.ai-framework/"
