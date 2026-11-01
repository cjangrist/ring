#!/bin/sh
set -eu
RING_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$RING_ROOT/f3-ring" "$@"
