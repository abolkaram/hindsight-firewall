# Architecture

## Record boundary

`seal_decision` freezes information that was available before the outcome. It rejects duplicate identifiers, self-audits, weak context, missing alternatives, and unbounded assumption lists.

## Consensus boundary

`_judge` asks validators for four typed values only: two booleans and two assumption-index arrays. Every validator reruns the same audit and exact-compares the complete result. Deterministic code checks bounds, uniqueness, exclusivity, and the sound-process invariant.

## Revision boundary

`challenge_audit` is callable once, only by the case owner, and only with new evidence. The contract recomputes the audit against the combined evidence and records `CONFIRMED` or `REVISED`.

## Storage boundary

Cases live in a keyed `TreeMap`; a separate ordered index supports bounded pagination. Text and arrays are capped before storage to control transaction size.

