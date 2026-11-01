# f3-ring

Python diagnostics for the F3 Bluetooth ring on macOS. We are using **T mode**
for three single-tap mappings and two outer-button hold mappings. The current
package captures input; action dispatch is not implemented yet.

[Measured behavior and the T-mode decision](docs/reports/2026-11-01_f3_t_mode_synthesis.md)

## Run

Requires macOS, `uv`, and an F3 paired through macOS Bluetooth settings.
The launcher keeps Python, its environment, and the uv cache inside this repo.

```sh
./f3-ring --inventory
./f3-ring
./f3-ring --guided-part2
```

The default command opens all exactly named F3 HID entries exclusively and logs
raw input until Ctrl-C. `--guided-part2` runs eight short, self-paced prompts;
`--guided` runs the original 24-case exploration. In guided mode, Enter advances,
`r` repeats, `s` skips, and `q` exits. A failed seizure prevents the prompts from
starting. `--request-access` requests macOS Input Monitoring permission if needed.

`./ring` remains an alias. The installed entry point is `f3-ring`; the Python
package is `f3_ring` under `src/`.

## Recordings

Every invocation creates `sessions/<UTC timestamp>-<id>/events.jsonl`. Sessions
are local and ignored by Git. Logs retain untouched report bytes, callback IDs,
receipt times, device descriptors and hashes, source hashes, physical trial
labels, errors, and lifecycle events. Each record is flushed and fsynced by a
writer thread. HID callbacks copy the bytes and enqueue them without file I/O.
The queue is unbounded; overload/drop behavior has not been stress-tested.

A prompt marked finished is a user annotation, not a passed hardware test.
The recorder stops on device removal; automatic reconnection is not implemented.
A successful exclusive open is recorded separately from observed suppression
of native input. The latter is still unverified.

## Develop and verify

```sh
export UV_PYTHON_INSTALL_DIR="$PWD/.uv-python"
export UV_CACHE_DIR="$PWD/.uv-cache"
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv build
```

`tests/` contains hardware-independent capture/interaction tests and checks
against the measured fixtures in `tests/fixtures/2026-11-01/`. These checks do
not replace physical press, release-timing, or suppression experiments.

To export a new capture for review before publication:

```sh
uv run --locked python scripts/export_capture.py sessions/<session>/events.jsonl --output tests/fixtures/<name>.jsonl
```

The exporter retains an explicit set of diagnostic fields and omits personal
paths, runtime process/location identifiers, and free-text notes. The committed
fixture manifest records source and exported hashes. Original recordings remain
untouched in `sessions/`.
