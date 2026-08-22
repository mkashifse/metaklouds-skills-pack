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
docs/meta-pds/drift-log.yaml                       # created on first detected drift
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
- `assets/drift-log-template.yaml`
- `assets/delivery-state-template.yaml`

Each functional skill provides its owned artifact template.

## Ownership

| Artifact | Canonical owner | Other functions |
| --- | --- | --- |
| `initiative.md` | Product Manager with Human approval | read; changes return to PM |
| `decision-log.yaml` | Product Manager | submit evidence; do not edit |
| `drift-log.yaml` | Product Manager | report evidence and affected dependency closure |
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
5. unresolved verified drift evidence;
6. `delivery-state.yaml` current-state projection;
7. draft artifacts and prototype behavior.

The prototype is evidence, never product authority. `delivery-state.yaml` is a
current-state ledger, not a narrative activity log. Use the optional JSONL file
for append-only history. The dashboard is a read-only in-memory view and never
overrides a canonical artifact or verified runtime evidence. Never persist a
separate dashboard data file.

## Decision truth

Every Truth has one stable semantic `key` and an append-only sequence of
revision records. Every revision has an immutable, globally unique `id`, a
contiguous integer `revision`, and—after revision 1—a `supersedes` link to the
immediately previous revision ID. The key is the cross-session and cross-
artifact reference; IDs identify exact historical records. A primary decision
`type` places the choice in the upstream-to-
downstream chain, `phases` scope when it applies, `depends_on` records upstream
decision keys, and `contradicts` records incompatible decision keys.

Only the active `LOCKED` revision without an unresolved locked
contradiction is canonical product truth. Proposed and testing decisions are
durable candidates, not authority. One candidate may coexist with the current
locked revision; it does not replace canonical truth until Human approval.
When approved, mark the former locked revision `SUPERSEDED` and lock the new
revision. Never mutate or delete an earlier revision. Contradiction links are
interpreted in both directions even when declared by only one record. Two
active locked decisions that contradict each other are a structural error and
block affected gates.

Use this primary-type chain so review and dependency direction stay explicit:

1. product direction: `GOAL`, `USER_PROBLEM`, `OUTCOME_METRIC`,
   `SCOPE_PRIORITY`;
2. product behavior: `FEATURE_CAPABILITY`, `BUSINESS_RULE`;
3. experience: `UI_UX`, `CONTENT_ACCESSIBILITY`;
4. domain and data: `DOMAIN_MODEL`, `SCHEMA`;
5. system design: `ARCHITECTURE`, `API_INTEGRATION`, `SECURITY_PRIVACY`;
6. technology: `STACK`, `DATABASE_STORAGE`;
7. quality: `TESTING_QUALITY`;
8. delivery: `RELEASE_MIGRATION`;
9. operations: `OBSERVABILITY_OPERATIONS`.

Use `GLOBAL` for an initiative-wide decision or one or more `PHASE-N` values
for phased applicability. Do not combine `GLOBAL` with numbered phases.

## Revisions and traceability

- Every initiative and slice has an integer revision and source commit when
  version control is available.
- A locked upstream revision is immutable. Corrections append a new revision
  with the same key and a new ID; history remains queryable in the Truth item.
- Every work package cites slice requirements or user stories, its contract
  version, dependencies, required Test IDs from the slice, owned paths, and
  evidence. It also records assignment metadata and one immutable Lead brief:
  issuer and time, original instruction, expected outcome, scope, explicit
  exclusions, and acceptance criteria. Later clarification is append-only and
  never silently rewrites that original instruction. Test definitions are not
  copied into the execution plan or report.
- Every report cites exact commits, test commands/results, deployments, and
  remaining risks.
- Do not duplicate code-native OpenAPI, JSON Schema, migrations, or similar
  contracts; link their paths and immutable revisions.

## Structural validation

The templates, validator, and dashboard share one parsing and validation
contract. The dashboard does not maintain a second schema or product-side data
file.

After any owned slice, execution plan, report, decision log, drift log, delivery state, or
initiative change, validate the affected slice. Before every gate or resume,
validate the entire product:

```text
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --slice-id <slice-id>
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --all
```

Repository-wide validation discovers every slice, execution plan, report,
optional drift log, and optional delivery event. It rejects duplicate YAML keys,
stable IDs, or revisions within one Truth key, invalid
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
