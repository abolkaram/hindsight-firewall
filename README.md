# Hindsight Firewall

## The split verdict

A bad result does not prove that a decision was careless. A good result does not prove that it was sound. Hindsight Firewall keeps those questions separate.

Before acting, an owner seals the context, assumptions, rule, selected action, rejected alternative, known risks, and one independent auditor. After the outcome exists, only that auditor can add later evidence. GenLayer validators classify the record on two independent axes:

| Decision process | Later outcome | Verdict |
|---|---|---|
| sound | favorable | `SOUND_GOOD_OUTCOME` |
| sound | unfavorable | `SOUND_BAD_OUTCOME` |
| unsound | favorable | `UNSOUND_LUCKY_OUTCOME` |
| unsound | unfavorable | `UNSOUND_BAD_OUTCOME` |

The owner has one evidence-bound challenge. The contract records whether the original verdict was confirmed or revised; it never silently overwrites the first audit trail.

## Invariants

- The case owner and auditor must be different wallets.
- The contemporaneous record is immutable after sealing.
- Unsupported assumptions and later-invalidated assumptions are separate, disjoint index sets.
- A sound process cannot contain an unsupported assumption.
- Every nondeterministic result is independently recomputed and exact-compared by validators.
- Free-form model explanations are not stored as authority.

## Contract surface

Writes: `seal_decision`, `audit_decision`, `challenge_audit`.

Reads: `get_case`, `get_cases_page`, `get_summary`.

The contract is in [`contracts/contract.py`](contracts/contract.py). It has no frontend because this contribution is an Intelligent Contract primitive, not a dApp submission.

## Verification route

1. Run `genvm-lint check contracts/contract.py --json`.
2. Review the adversarial cases in [`tests/direct/test_firewall.py`](tests/direct/test_firewall.py).
3. Compare [`deployment.json`](deployment.json) with the StudioNet Explorer source.
4. Read the live case identified in [`evidence/live-record.json`](evidence/live-record.json).

Exact network addresses and transactions are recorded after deployment.

