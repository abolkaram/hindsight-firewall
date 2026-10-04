# Verification

## Static gate

`genvm-lint check contracts/contract.py --json` returns `ok: true`, three lint checks passed, and six exported methods validated.

## Adversarial suite

The direct tests cover a sound decision with a bad outcome, unauthorized auditing, a forged assumption classification, a single evidence-bound challenge, and duplicate case rejection.

The current Windows direct-test harness fails before loading any contract with `genlayer.py.calldata.DecodingError: unexpected end of memory`. The same failure reproduces on an already deployed legacy contract, so it is recorded as a local harness limitation, not reported as a passing test.

## Network gate

Acceptance requires the exact checked-in source to deploy on StudioNet, reach `FINALIZED` with `SUCCESS`, accept a live state transition, and return that state through a view call. The resulting identifiers are stored in `deployment.json` and `evidence/live-record.json`.

