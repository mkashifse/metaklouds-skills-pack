# Interaction Modes and Decision Capture

Interaction modes change how Meta PDS assists the Human; they do not replace
initiative or slice gates. Select the mode from current intent and durable
state, and let the Human override it in ordinary language.

## Modes

- `EXPLORE`: preserve conversational flow. Quietly capture consequential goals,
  scope, capability, experience, data, architecture, technology, quality, and
  delivery choices as `PROPOSED`. Do not interrupt merely to request locking.
- `DECISION_REVIEW`: present the unresolved decision delta in upstream-to-
  downstream order. Lock, keep testing, revise, or supersede each candidate
  from explicit Human confirmation; the Human need not use the word “lock.”
- `PROTOTYPE`: turn unresolved product and experience decisions into bounded
  experiments. A request for entities, fields, profiles, seed records,
  permissions, forms, or relationships triggers a conceptual-schema decision
  packet before the prototype is treated as durable product evidence.
- `SLICE_SHAPING`: when implementation is requested without approved slices,
  propose an ordered fat-slice roadmap. The Human approves slices individually
  before detailed planning begins.
- `DELIVERY`: plan, implement, verify, and release only approved slices through
  the existing Meta PDS gates.

## Durable capture

Save a meaningful decision cluster to `decision-log.yaml` before topic changes,
session handoff, or context pressure can make reconstruction unreliable. A
captured candidate is durable but not approved. Preserve one unique semantic
`key`, a primary `type`, applicable `phases`, upstream `depends_on` keys, and
explicit `contradicts` keys.

Only the active `LOCKED` revision without an unresolved locked
contradiction is canonical product truth. Never auto-lock a consequential
choice. Never overwrite a locked decision; append a uniquely identified
candidate revision under the same key and link `supersedes` to the immediately
previous revision ID. Keep the current locked revision authoritative until
Human approval. On approval, mark it `SUPERSEDED` and lock the candidate.
Use `contradicts` for incompatible Truth keys, not revision history.

Do not interrupt `EXPLORE` unless the discussion introduces an irreversible,
destructive, security-sensitive, legally material, or locked-decision conflict.
At natural pauses, offer one concise decision digest and allow the Human to
continue exploring.

## Resume behavior

Read the decision log before accepting a short resume brief as complete. Show:

- candidates ready for review;
- decisions still under test;
- unresolved contradictions;
- locked upstream decisions affected by the requested work;
- the recommended next mode.

The dashboard is visibility only. It shows modes and decisions but never locks,
supersedes, or resolves them.
