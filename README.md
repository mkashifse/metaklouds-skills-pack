# Solo Founder Skills Pack

Three thin, explicitly invoked roles for a solo founder:

| Skill | Use it for |
| --- | --- |
| `$solo-founder` | Product discovery, decisions, planning, governed documents, prototype checkpoints, Fat Slices, and Work Packages |
| `$prototype-engineer` | Direct rapid prototype edits with an edit-run-view loop |
| `$full-stack-engineer` | Direct implementation and verification of a Work Package or bounded production change |

```text
Founder ──chooses──> Solo Founder PM
       ├───────────> Prototype Engineer
       └───────────> Full-Stack Engineer
```

The roles do not automatically delegate to each other. They do not restore the
full product context on every message. Each reads only the files necessary for
the current request.

## Operating model

The PM owns upstream product work and durable decisions. Prototype Engineer
owns fast reversible experiments. Full-Stack Engineer owns verified production
delivery. The founder switches roles explicitly instead of paying orchestration
and handoff overhead for every change.

Prototype and delivery work do not update Canonical Truth, the Product Ledger,
handoffs, or planning documents unless the founder explicitly asks to record a
checkpoint or result.

Product repositories may still use these durable artifacts when governance is
useful:

```text
docs/solo-founder/canonical-truth.yaml
docs/solo-founder/product-ledger.yaml
docs/solo-founder/slices/
```

The PM's `restore_context.py` remains available for an explicit product-wide
status, audit, reconciliation, or initialization. It is not a per-message hook.

## Installation

Install the complete profile for Codex:

```bash
./scripts/install.sh codex
```

Replace an existing installation:

```bash
./scripts/install.sh codex --force
```

Install only one execution role:

```bash
./scripts/install.sh codex --only prototype-engineer
./scripts/install.sh codex --only full-stack-engineer
```

The complete profile also installs conditional technical support skills for
React, frontend design, FastAPI, Node.js, testing, Playwright, Supabase, and
Postgres. Support skills are loaded only when relevant to the current task.

## Examples

```text
$solo-founder Define and lock the onboarding behavior.

$prototype-engineer Make the signup card more compact and show me the result.

$full-stack-engineer Implement and verify WORK-ONBOARDING-001.
```
