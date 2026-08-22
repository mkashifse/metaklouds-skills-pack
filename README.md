# Metaklouds Skills Pack

Installable product-to-engineering workflows for Codex and Claude Code.

`meta-pds` is the human-centered entrypoint for new initiatives. It coordinates
rapid prototyping, fat-slice planning, bounded development, independent QA, and
release evidence while automatically starting or reusing one local delivery
dashboard per project. It preserves meaningful checkpoints with local commits
and, when the Human changes delivery topic, nudges them to create and merge a PR
once the branch satisfies its checks and approvals. The dashboard includes live
local branch visibility and verified GitHub pull-request status when available.
It never substitutes bundled sample delivery data for the selected project;
missing canonical artifacts remain visible as setup diagnostics.

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
slices, work packages, repository branches, pull requests, and release evidence
into its installed local dashboard. Earlier Metaklouds delivery workflows are
retired and are not publicly discoverable or installed.

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

## Installation contract

Use `scripts/install.sh` to install the pack. Generic repository skill scanners
can discover the five bundled Meta PDS skills, but they cannot fetch the eleven
required upstream supports and therefore do not produce a complete profile.

## License

Metaklouds-authored files are available under the [MIT License](LICENSE).
Upstream skills retain their original ownership and licensing and are not
vendored in this repository.
