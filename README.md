# Metaklouds Skills Pack

An installable product-to-engineering workflow for Codex and Claude Code.

The pack turns an idea into a validated initiative, plans it as fat end-to-end
vertical slices, and implements each slice as one releasable unit:

```text
meta-grill-team
  -> vertical-slice-team
    -> dev-team
```

Runtime discoveries are handled by `change-management`, so team leads can lock
contained decisions, request human approval for material changes, run a quick
impact analysis, and keep unaffected work moving.

## Included skills

The full installer provides nine skills:

| Skill | Ownership | Purpose |
| --- | --- | --- |
| `meta-grill-team` | Metaklouds | Define the initiative while building a JSON-backed React prototype |
| `vertical-slice-team` | Metaklouds | Convert an approved initiative into fat, end-to-end vertical slices |
| `dev-team` | Metaklouds | Map one fat slice into stories/tasks, implement it, test it, and release it |
| `change-management` | Metaklouds | Control runtime decisions, approvals, impact analysis, and synchronization |
| `prototype` | Upstream | Keep exploratory prototypes fast, explicit, and disposable |
| `vercel-react-best-practices` | Upstream | Guide React and Next.js implementation |
| `fastapi` | Upstream | Guide FastAPI and Pydantic implementation |
| `supabase` | Upstream | Guide Supabase implementation and security |
| `supabase-postgres-best-practices` | Upstream | Guide Postgres schemas, migrations, RLS, and performance |

The four Metaklouds skills are bundled in this repository. Upstream skills are
downloaded at pinned revisions from their original repositories during
installation. See [THIRD_PARTY.md](THIRD_PARTY.md) and
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
timestamped backup beside the installation directory.

For an isolated or CI installation, provide an explicit destination:

```bash
./scripts/install.sh codex --dest /absolute/path/to/skills
```

## Use the workflow

Start with:

```text
Use $meta-grill-team to define this initiative and build its React prototype.
```

After the initiative is approved:

```text
Use $vertical-slice-team to plan fat, end-to-end vertical slices.
```

For each approved slice:

```text
Use $dev-team to implement and release this entire vertical slice.
```

The canonical product documents should live in a coordination repository. Keep
the prototype, production frontend, and production backend in separate
repositories or workspaces, as described by the `dev-team` repository-layout
reference.

## Install only the bundled Metaklouds skills

Agents compatible with the open skills format can discover the four bundled
skills under `skills/`. For example:

```bash
npx skills add mkashifse/metaklouds-skills-pack --all
```

This shortcut does not install the five upstream implementation dependencies;
use `scripts/install.sh` for the complete pack.

## License

Metaklouds-authored files are available under the [MIT License](LICENSE).
Upstream skills retain their original ownership and licensing and are not
vendored in this repository.
