#!/bin/sh
# Run the diagnostic with the interpreter, environment, and cache inside this repository.
set -eu
RING_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export UV_PYTHON_INSTALL_DIR="$RING_ROOT/.uv-python"
export UV_CACHE_DIR="$RING_ROOT/.uv-cache"
cd "$RING_ROOT"
exec uv run --locked ring-diagnostics "$@"
