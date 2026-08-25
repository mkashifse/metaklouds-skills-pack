# Dashboard Contract

The local dashboard is an optional, minimal product cockpit. It preserves the
proven Meta PDS visual language: compact dark header, orange active accents,
horizontal tabs, sticky toolbars, quiet document rows, hairline separators,
semantic status colors, and progressive detail. It must not be launched as
part of every PM message or context restore.

## Sources

Read only repository-backed evidence:

- `docs/solo-founder/canonical-truth.yaml`;
- `docs/solo-founder/product-ledger.yaml`;
- `docs/solo-founder/slices/*.md`;
- typed delegated handoffs through their Product Ledger references.

The dashboard never maintains a separate product projection file.

When `index.html` is opened directly from the skill assets, show the bundled,
clearly labelled demo dataset so the visual system can be reviewed without a
product repository. Demo data is read-only and must never replace, merge into,
or mask canonical data when the local dashboard server is running.

## Visible projection

Keep one compact context strip visible above every view:

- current Mode and proposed Truth count;
- current Layer and affected Layers;
- active initiative title/ID and status;
- next recommended action, impact, and Human-approval requirement.

Use exactly four primary views:

1. `Truth`: every `PROPOSED` and `APPROVED` Truth item, newest first, with
   Layer, statement, evidence, affected Layers, replacement, and approval
   metadata. Do not render ten empty Layer sections; show one honest empty
   state when no Truth exists.
2. `Slices`: the current Fat Slice files with ID, title, status, priority,
   capability outcome, dependencies, Story/Test counts, prototype checkpoint,
   promotion map, and linked Work Packages. Selecting a Slice opens the Meta
   PDS-style detail modal with Overview, User Stories and acceptance criteria,
   related Work Packages, and Test Cases with Story traceability.
3. `Work`: Product Ledger Work Packages with status, activity, classification,
   direct/delegated execution, role, owner, focus, acceptance, result, evidence,
   blocker, and handoff state/path. Default to active work while keeping review,
   blocked, complete, and all filters available.
4. `Issues`: Product Ledger `DRIFT`, `BLOCKER`, `RISK`, and
   `EXTERNAL_DEPENDENCY` records, including Human attention and available
   links/evidence.

Do not restore obsolete Meta PDS views for branches, pull requests, Scrum,
generic activity, or a separate prototype tab. Solo Founder does not maintain
the canonical sources required for those projections. The dashboard should
display less data rather than infer or duplicate it.

Use status text and a small state dot rather than filled pills:

- complete and approved: green;
- active: orange;
- proposed, verifying, rework, or Human review: blue;
- ready: amber;
- blocked, failed, or at risk: red;
- planned, paused, cancelled, or unknown: neutral.

Rows begin compact and expand in place for evidence and properties. The
dashboard reparses canonical artifacts on refresh. Malformed Slice files are
quarantined and shown in the data-health banner while valid Truth and Ledger
data remain visible.

## Write boundary

The dashboard is read-only except for explicit Human approval of one
`PROPOSED` Truth. Approval must:

1. show Layer, statement, replacement, and affected Layers;
2. require Human confirmation;
3. reload the current file and verify its content hash;
4. confirm the item remains `PROPOSED`;
5. validate ID, Layer, evidence, affected Layers, and replacement;
6. set `APPROVED`, `approved_by: HUMAN`, `approved_via: DASHBOARD`, and time;
7. validate the complete artifact;
8. lock and atomically replace the original;
9. leave the original unchanged on conflict or failure.

The dashboard cannot edit the Product Ledger, create product decisions, change
Mode or Layer, assign work, or approve without an explicit Human click.

Active work visibility should distinguish `DIRECT` PM execution from
`DELEGATED` parallel execution. For delegated work, show its handoff type and
whether it is awaiting submission or PM consumption. The dashboard remains a
projection of the Product Ledger and must not invent another handoff status.

Bind only to `127.0.0.1`. Reuse one healthy runtime for the same product root
and runtime version; replace stale runtimes after dashboard upgrades.
