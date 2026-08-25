# Dashboard Contract

The local dashboard is optional visibility. It must not be launched as part of
every PM message or context restore.

## Sources

Read only repository-backed evidence:

- `docs/solo-founder/canonical-truth.yaml`;
- `docs/solo-founder/product-ledger.yaml`;
- `docs/solo-founder/slices/*.md`;
- research, reports, typed delegated handoffs, and local Git evidence when
  useful.

The dashboard never maintains a separate product projection file.

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

Bind only to `127.0.0.1`. Reuse one healthy runtime for the same product root.
