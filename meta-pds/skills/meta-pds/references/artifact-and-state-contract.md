# Artifact and State Contract

## Canonical paths

Use one Git repository as the product root. The locked default layout is:

```text
<product-root>/
├── docs/meta-pds/             # canonical Meta PDS artifacts
├── prototypes/                # disposable prototype evidence
├── frontend/                  # frontend application and frontend tests
└── backend/                   # backend, database migrations, and backend tests
```

This is a single-repository product workspace. Do not create nested `.git`
directories, Git submodules, or separately cloned repositories inside it.

Frontend and backend share delivery coordination, not application source code:

- no direct source-code imports or runtime package dependency across
  `frontend/` and `backend/`;
- integration uses an explicit versioned API, event, or data contract;
- generated clients or schemas must record their source contract and generation
  command and live inside the consuming area;
- work packages declare owned and forbidden paths;
- tests and CI are path-scoped where possible, while whole-slice verification
  covers the integrated behavior;
- one slice may change both areas, but each change remains owned and tested in
  its area.

Adding another top-level production code area or permitting cross-area source
sharing is an architecture decision requiring Human approval and a recorded
decision revision.

Use this compact artifact set in the product root:

```text
docs/meta-pds/initiative.md
docs/meta-pds/decision-log.yaml
docs/meta-pds/delivery-state.yaml
docs/meta-pds/delivery-events.jsonl              # optional append-only audit
docs/meta-pds/slices/<slice-id>.md
docs/meta-pds/execution/<slice-id>.yaml
docs/meta-pds/reports/<slice-id>.md
prototypes/<initiative-id>/
```

Each non-empty `delivery-events.jsonl` line is one JSON object with `at` (ISO
8601 timestamp), `kind`, `title`, and `detail`. Append only meaningful durable
changes such as Human approvals, gate changes, assignments, work starts,
verification handoffs, completions, blockers, and releases. Do not record chat,
keystroke, or file-save noise. The dashboard orders valid events newest first.

Create artifacts from the suite assets:

- `assets/initiative-template.md`
- `assets/decision-log-template.yaml`
- `assets/delivery-state-template.yaml`

Each functional skill provides its owned artifact template.

## Ownership

| Artifact | Canonical owner | Other functions |
| --- | --- | --- |
| `initiative.md` | Product Manager with Human approval | read; changes return to PM |
| `decision-log.yaml` | Product Manager | submit evidence; do not edit |
| `delivery-state.yaml` | Product Manager | return structured status |
| prototype | Rapid Prototype Engineer | inspect as behavioral evidence |
| slice file, including test definitions | Planning Lead | Development/QA read; gaps return upstream |
| execution plan, including Test ID assignments | Development Lead | QA reads; PM controls gate |
| production code/tests | Assigned Development worker | other roles inspect only |
| delivery report | Development Lead + independent QA evidence | PM records final gate |
| dashboard runtime view | derived in memory from canonical artifacts | no function edits it |

Under Meta PDS control, only the Product Manager changes canonical gate status.
Functional leads provide evidence-backed recommendations.

## Truth and precedence

1. verified runtime/release evidence;
2. locked Human decisions and current initiative revision;
3. current locked slice revision;
4. frozen execution contract and plan;
5. `delivery-state.yaml` current-state projection;
6. draft artifacts and prototype behavior.

The prototype is evidence, never product authority. `delivery-state.yaml` is a
current-state ledger, not a narrative activity log. Use the optional JSONL file
for append-only history. The dashboard is a read-only in-memory view and never
overrides a canonical artifact or verified runtime evidence. Never persist a
separate dashboard data file.

## Revisions and traceability

- Every initiative and slice has an integer revision and source commit when
  version control is available.
- A locked upstream revision is immutable. Corrections create a new revision.
- Every work package cites slice requirements or user stories, its contract
  version, dependencies, required Test IDs from the slice, owned paths, and
  evidence. Test definitions are not copied into the execution plan or report.
- Every report cites exact commits, test commands/results, deployments, and
  remaining risks.
- Do not duplicate code-native OpenAPI, JSON Schema, migrations, or similar
  contracts; link their paths and immutable revisions.

## Structural validation

The templates, validator, and dashboard share one parsing and validation
contract. The dashboard does not maintain a second schema or product-side data
file.

After any owned slice, execution plan, report, decision log, delivery state, or
initiative change, validate the affected slice. Before every gate or resume,
validate the entire product:

```text
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --slice-id <slice-id>
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --all
```

Repository-wide validation discovers every slice, execution plan, report, and
optional delivery event. It rejects duplicate keys and stable IDs, invalid
types and statuses, filename/identity or revision drift, unknown references,
dependency cycles, malformed Markdown grammar, and invalid event records.

YAML artifacts support mappings, lists, inline collections, quoted and plain
scalars, comments, and literal or folded multiline scalars. Do not use anchors,
aliases, explicit tags, tabs for indentation, or duplicate keys. These are
rejected deliberately so agent output stays deterministic.

Structural validation supports but does not replace Planning, Development
Intake, or independent QA judgment. A failed check blocks only the affected
gate; preserve valid unrelated artifacts and return each diagnostic to its
canonical owner.
