# Metaklouds Skills Pack

A human-centered product delivery system for Codex and Claude Code.

`meta-pds` is the flagship and the Human's single point of contact. It turns an
idea into locked product Truth, manually reviewed prototypes, approved fat
slices, bounded implementation tasks, independent QA, release evidence, and
outcome validation. The Product Manager coordinates the internal skills and
specialist workers; the Human receives one concise status, the decisions that
need judgment, and one recommended next action.

Every invocation reconstructs delivery state from repository artifacts and
runtime evidence instead of relying on chat memory. Meta PDS starts or reuses
one local dashboard per project, checkpoints meaningful work with local commits,
and keeps unfinished or approval-dependent work visible without inventing
progress. Bundled examples are available only through an explicitly labelled
demo view and are never copied into a user's project.

The flagship supports five working modes—Explore, Decision Review, Prototype,
Slice Shaping, and Delivery—so consequential choices can be captured without
breaking a brainstorming flow. Locked Truth uses stable semantic keys,
append-only revisions, upstream-to-downstream types, phase assignments,
dependencies, and explicit contradiction links.

The complete profile turns an idea into a validated initiative, plans it as fat
end-to-end vertical slices, and implements each slice as one releasable unit:

```text
meta-pds (the Human-facing flagship)
  -> rapid-prototyping
  -> slice-planning
  -> slice-development
  -> slice-qa
  -> stack-specific implementation and testing support
```

Meta PDS owns change control and continuously projects authoritative decisions,
slices, Scrum tasks, detected drift, repository branches, pull requests, and
release evidence into its installed local dashboard. Earlier Metaklouds delivery
workflows are retired and are not publicly discoverable or installed.

## Included skills

The full installer provides the sixteen-skill Meta PDS profile:

| Skill | Ownership | Purpose |
| --- | --- | --- |
| `meta-pds` | Metaklouds | Coordinate the human-centered delivery suite and its per-project dashboard |
| `rapid-prototyping` | Metaklouds | Build disposable prototypes for manual Human review |
| `slice-planning` | Metaklouds | Define implementation-ready fat slices |
| `slice-development` | Metaklouds | Mobilize and execute bounded slice work packages |
| `slice-qa` | Metaklouds | Independently verify release and outcome evidence |
| `prototype` | Upstream | Keep exploratory prototypes fast, explicit, and disposable |
| `vercel-react-best-practices` | Upstream | Guide React and Next.js implementation |
| `frontend-design` | Upstream | Create distinctive, intentional production interfaces |
| `vercel-composition-patterns` | Upstream | Structure scalable React components and reusable APIs |
| `fastapi` | Upstream | Guide FastAPI and Pydantic implementation |
| `nodejs-backend-patterns` | Upstream | Build production Node.js and TypeScript APIs |
| `python-testing-patterns` | Upstream | Test Python APIs, async services, databases, and integrations with pytest |
| `vitest` | Upstream | Test TypeScript and frontend units, components, mocks, and coverage |
| `playwright-best-practices` | Upstream | Build reliable Playwright E2E, component, API, visual, and accessibility tests |
| `supabase` | Upstream | Guide Supabase implementation and security |
| `supabase-postgres-best-practices` | Upstream | Guide Postgres schemas, migrations, RLS, and performance |

The flagship and its four functional skills are bundled in this repository.
The eleven upstream support skills are downloaded at pinned revisions from
their original repositories during installation. See
[THIRD_PARTY.md](THIRD_PARTY.md) and
[manifest.json](manifest.json).

## Delivery dashboard

The dashboard is a read-only projection of the selected project's canonical
artifacts and live repository evidence:

| View | What it shows |
| --- | --- |
| **Truth** | Canonical and proposed decisions, revision history, phases, dependencies, contradictions, and affected artifacts |
| **Slices** | Fat-slice status, outcomes, progress, dependencies, work packages, contracts, and tests |
| **Drifts Detected** | Auto-resolved and approval-pending drift, confidence, recommendations, evidence, and paused versus continuing work |
| **Branches** | Current and local branches, working-tree state, commit evidence, and GitHub pull-request status when available |
| **Scrum Board** | Canonical execution tasks grouped by Backlog, Ready, In Progress, Review, Done, and blocked states |

The dashboard server is owned by the installed `meta-pds` skill. It reuses a
healthy runtime for the same project and returns both the live URL and, when
useful, a separate demo URL. No dashboard application or sample data is written
into the product repository.

## Operating model

- **New project:** Meta PDS explains that no canonical context exists, asks for
  a short brief, records the authority envelope, and recommends the first
  discovery action.
- **Returning project:** it reads the current Truth, slices, Scrum tasks, drift,
  branches, PRs, and evidence, then gives a compact recap and next action.
- **Human approval:** only affected dependency paths pause. Independent ready
  work continues inside the approved authority envelope.
- **Drift control:** safe, reversible, high-confidence drift may be resolved and
  logged automatically. Ambiguous or consequential drift carries a recommendation
  and waits for Human approval.
- **Git control:** workers make bounded local checkpoints. Pushes, PR creation,
  merges, releases, migrations, and other external actions remain with the
  Product Manager and require the recorded authority.
- **Completion:** a component, task, or PR is not a completed slice. A slice
  completes only after whole-slice QA, release evidence, and the release gate.

## Install for Codex

```bash
git clone https://github.com/mkashifse/metaklouds-skills-pack.git
cd metaklouds-skills-pack
./scripts/install.sh codex
```

Skills are installed into `${CODEX_HOME}/skills` when `CODEX_HOME` is set,
otherwise into `~/.codex/skills`.

Start a new Codex task after installation so the skill catalog refreshes.

## Install for Claude Code

```bash
git clone https://github.com/mkashifse/metaklouds-skills-pack.git
cd metaklouds-skills-pack
./scripts/install.sh claude
```

Skills are installed into `${CLAUDE_HOME}/skills` when `CLAUDE_HOME` is set,
otherwise into `~/.claude/skills`.

Restart Claude Code after installation so it discovers the new skills.

## Update an existing installation

Pull the latest pack and run the installer with `--force`:

```bash
git pull
./scripts/install.sh codex --force
# or
./scripts/install.sh claude --force
```

`--force` does not delete the current copy. It moves every replaced skill to a
timestamped `metaklouds-skills-backups` directory outside the discoverable
skills directory. A complete-profile install also moves any earlier legacy
Metaklouds workflows there so they remain recoverable but inactive.

Selecting the flagship always installs its complete dependency profile:

```bash
./scripts/install.sh codex --force --only meta-pds
```

For an isolated or CI installation, provide an explicit destination:

```bash
./scripts/install.sh codex --dest /absolute/path/to/skills
```

## Use the workflow

Start with:

```text
Use $meta-pds to start or resume this product initiative.
```

Meta PDS starts or reuses the project's local dashboard and returns its URL.
It routes internally to its four functional skills and selects the installed
implementation and testing skills from actual repository evidence. Users do
not need to coordinate those skills directly.

For a bounded autonomous delivery window, state the objective, completion
condition, authority limits, and stopping time explicitly. The proposed Codex
scheduled-supervision design uses a thread-attached heartbeat to wake Meta PDS,
while canonical project artifacts remain the memory and authority source. The
design includes a single-supervisor lease, overlap protection, daily resume
briefs, approval-aware continuation, and terminal shutdown conditions. It is
documented in
[`scheduled-supervision-strategy.md`](meta-pds/skills/meta-pds/references/scheduled-supervision-strategy.md)
and remains **proposed** until the delivery-state schema, validator, dashboard,
and automation lifecycle implement it together.

For visual inspection without initializing a project, open the explicitly
labelled demo URL printed by the dashboard launcher. Demo delivery data is
served by the same per-project runtime, never copied into the repository, and
kept separate from the ordinary live URL and API response.

The canonical product documents, prototype, frontend, and backend live in one
product repository:

```text
product-root/
├── docs/meta-pds/
├── prototypes/
├── frontend/
└── backend/
```

Do not create nested repositories or submodules. Frontend and backend remain
path-isolated and integrate through an explicit versioned contract. A slice is
complete only after independent whole-slice QA and release evidence pass.

Canonical delivery artifacts live under `docs/meta-pds/`:

```text
docs/meta-pds/
├── initiative.md
├── decision-log.yaml
├── delivery-state.yaml
├── drift-log.yaml              # created when drift is first detected
├── delivery-events.jsonl       # optional append-only audit
├── slices/
├── execution/
└── reports/
```

Truth and delivery state stay in these artifacts. The dashboard never becomes
a second source of truth.

## Installation contract

Use `scripts/install.sh` to install the pack. Generic repository skill scanners
can discover the five bundled Meta PDS skills, but they cannot fetch the eleven
required upstream supports and therefore do not produce a complete profile.

## Repository layout and validation

```text
metaklouds-skills-pack/
├── README.md
├── THIRD_PARTY.md
├── manifest.json
├── scripts/install.sh
└── meta-pds/
    ├── manifest.json
    ├── scripts/install.sh
    └── skills/
        ├── meta-pds/
        ├── rapid-prototyping/
        ├── slice-planning/
        ├── slice-development/
        └── slice-qa/
```

Before publishing a change, run the Meta PDS test suite and perform an isolated
installer smoke test against a temporary destination. The installer must leave
the user's existing skills recoverable, keep upstream dependencies pinned, and
install the dashboard with the flagship skill.

## License

Metaklouds-authored files are available under the [MIT License](LICENSE).
Upstream skills retain their original ownership and licensing and are not
vendored in this repository.
