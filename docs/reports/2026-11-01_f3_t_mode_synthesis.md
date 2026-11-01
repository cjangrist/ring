# F3 ring: rolling with T mode

2026-11-01 · macOS 27.2 / arm64 · Python 3.12.16

We're rolling with **T mode**: three single-tap actions, plus top and bottom
press-and-hold actions. That's five useful mappings to build first. The signals
are promising and distinguishable in our captures; the finished remapper and its
end-to-end reliability still need implementation and testing.

This decision comes from our own ring recordings. Manufacturer instructions and
other people's devices are background material, not the specification for this unit.

## What we measured

The [first guided run](../../tests/fixtures/2026-11-01/baseline.jsonl) contains
557 input reports across 24 labeled cases. Each T-mode single-tap case produced
five byte-identical eight-report sequences. The three buttons produced different
sequences. Labels follow the user's top/middle/bottom orientation during testing.

| T-mode input | Observed output | First-version decision |
|---|---|---|
| Top tap | Report 3, upward coordinate sequence | Map one action per completed gesture |
| Middle tap | Report 3, leftward coordinate sequence | Map one action per completed gesture |
| Bottom tap | Report 3, downward coordinate sequence | Map one action per completed gesture |
| Top hold | Repeating `02ea00 → 020000` | Recognize the hold pattern; suppress duplicate actions from repeats |
| Bottom hold | Repeating `02e900 → 020000` | Recognize the other hold pattern; suppress duplicate actions from repeats |
| Middle hold | Three identical short, four-report sequences | Promising sixth action; defer initially |

The displayed hex is the untouched macOS callback buffer, including its report-ID
prefix. Top/bottom holds use report 2; taps use report 3. Holds therefore differ
in content, not just speed. Hold cycles usually arrived roughly 120–135 ms apart
in these trials, with variation. These are host receipt intervals, not physical
button timing or a guaranteed firmware repeat rate.

C mode also yielded distinct single-tap signals. Its middle tap alternated volume
values; its outer holds emitted repeating two-contact gestures. The
[short confirmation run](../../tests/fixtures/2026-11-01/confirmation.jsonl)
reproduced the C-bottom hold pattern: five identical five-report cycles, matching
the pattern in the first run. T is our simpler starting point because the outer
hold and single-tap signals use different report types.

## Why doubles and triples wait

Double/triple taps are tricky for humans to repeat at a consistent pace. The
operator reported counting and timing uncertainty, and the initial multi-click
recordings mixed special sequences, ordinary swipes, and silence. C-middle double
was a promising exception: three identical four-report sequences. We are not
calling all double clicks unreliable; they simply aren't needed for the first
five mappings.

The eight-prompt confirmation run produced no reports for its first seven actions
and 25 for its final C-bottom hold. Silence remains an observation, not proof of
unsupported behavior: we did not bracket those attempts with known-working single
taps. No timing thresholds or complete click-count model have been established.

## Release timing: promising, still unmeasured

Exact release timing is not essential for a one-shot shortcut. A decoder can
recognize a hold signature, fire once, and ignore its automatic repeats. That is
the intended behavior, not something the current recorder implements.

We still need to measure how output stops and when another hold can safely fire.
A zero consumer value or synthetic touch lift is part of the ring's generated
sequence; it does not necessarily mean the plastic button was released.

Two short experiments can resolve the practical questions later:

1. **Hold, release, watch the tail.** Record top and bottom holds of visibly
   different lengths, with a synchronized video of the physical release and the
   capture clock. Measure how long reports continue after release and whether
   there is a unique final signal. Keyboard annotations alone give approximate
   release timing. Use the results to choose a conservative quiet-time rule if
   there is no explicit physical-release report.
2. **One hold, one action; then a second hold.** With a harmless action counter,
   try a brief tap, a longer hold, and two separate holds with a comfortable gap.
   Check that taps do not also trigger holds, repeats do not multiply actions,
   and the second hold triggers again. Then shorten the gap only if needed.

## Capture status and evidence

macOS accepted exclusive opening and delivered reports. Native-input suppression
is still unverified: volume stayed unchanged both with and without our recorder.
No custom actions or firmware writes were performed. Automatic reconnect, a final
hold classifier, and release-aware action dispatch are not implemented. The
118-item research checklist is not complete.

The macOS descriptor is 223 bytes, SHA-256
`fd81cdbd9b45ed36f690830726654c70dc91cc5528516f84389aa79010a61941`.
Our reports differ from the public BLE sample's layout; do not use that sample's
byte decoder without checking the descriptor.

The [fixture manifest](../../tests/fixtures/2026-11-01/manifest.json) records source
and exported hashes. Published fixtures retain report bytes, timestamps, sequence
numbers, descriptors, and trial labels; personal paths, runtime identifiers, and
free-text notes are omitted. Original sessions remain intact locally. The final
hold in the first run was performed once, despite a prompt requesting three holds.

The `f3-ring` package provides raw capture, the original guided exploration, and
the eight-prompt self-paced confirmation. Tests check the capture machinery,
interaction flow, fixture integrity, and measured signatures. They do not turn
operator annotations into verified physical counts.
