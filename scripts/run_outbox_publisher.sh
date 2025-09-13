#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR/.."

: "${BATCH_SIZE:=50}"  # default 50
: "${LOOP:=false}"     # set LOOP=true for polling mode
: "${SLEEP:=5}"        # seconds between polls
: "${DRY_RUN:=false}"  # set DRY_RUN=true to not mark published

ARGS=("--batch-size" "$BATCH_SIZE")
[[ "$LOOP" == "true" ]] && ARGS+=("--loop" "--sleep" "$SLEEP")
[[ "$DRY_RUN" == "true" ]] && ARGS+=("--dry-run")

exec python scripts/outbox_publisher.py "${ARGS[@]}"
