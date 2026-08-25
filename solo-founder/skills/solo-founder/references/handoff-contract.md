# Delegated Work Handoff Contract

Direct PM work does not need a handoff. A durable handoff is required whenever
work crosses from the PM to a Prototype Engineer or Full-Stack Engineer.
Internal batched tool calls remain PM work and do not create a handoff.

## Lifecycle

```text
PM creates bounded Work Package and names handoff type/path
→ Engineer creates the handoff envelope
→ Engineer performs work and completes the typed payload
→ Engineer requests VERIFYING
→ validator checks handoff identity, type, path, and required content
→ PM consumes the handoff
→ PM records DONE or REWORK
```

The Work Package remains authoritative for instruction, scope, acceptance,
role, owner identity, focus, and owned paths. The handoff returns outputs and
evidence; it cannot change the assignment or create Canonical Truth.

## Universal envelope

Every file handoff contains:

- Work Package ID, handoff ID and type;
- producer role and owner identity;
- PM as consumer and creation time;
- outcome summary;
- deliverables and artifact paths;
- evidence;
- risks and limitations;
- open decisions, including `None` when there are none;
- the exact PM consumption target.

The producer writes the return payload. The PM verifies it against the Work
Package and uses it only at the named consumption point. Worker conclusions
remain evidence until the PM incorporates them into a canonical document,
Truth proposal, Slice, verification decision, release decision, or next work.

## Typed payloads

| Type | Required payload | PM consumption point | Default path |
| --- | --- | --- | --- |
| `RESEARCH` | Sources and findings; conflicts and confidence; preliminary implications | Before the PM writes final research, recommends direction, or proposes Truth | `handoffs/research/<work-id>.md` |
| `DOCUMENTATION` | Target documents; draft contribution; traceability and conflicts | Before the PM updates canonical research, Stories, Slices, plans, or reports | `handoffs/documentation/<work-id>.md` |
| `PROTOTYPE` | Checkpoint; implemented behavior/states; promotion inputs; proposed product findings | Before prototype review, Truth proposals, or Fat Slice shaping | `handoffs/prototype/<work-id>.md` |
| `IMPLEMENTATION` | Changed paths/commits; contracts/migrations; tests/rollback | At `VERIFYING`, before `DONE`, `REWORK`, release, or promotion | `handoffs/implementation/<work-id>.md` |
| `VERIFICATION` | Acceptance matrix; test results; failures and residual risk | Before completion or release decisions | `handoffs/verification/<work-id>.md` |
| `EXCEPTION` | Exception/impact; blocked work; options and recommendation | Immediately when a complex blocker, drift, risk, or external dependency needs PM action | `handoffs/exception/<work-id>.md` |

All paths are relative to `docs/solo-founder/` in the table. Simple blockers
remain in the Product Ledger and do not require an extra file. Use an
`EXCEPTION` handoff only when durable analysis is needed.

## Consumption rules

- Research workers provide sources and preliminary findings; the PM writes the
  final research conclusion and any Truth proposal.
- Documentation workers provide drafts; the PM owns and edits canonical files.
- Prototype workers return code plus behavior evidence; the PM decides which
  findings become proposed Truth.
- Implementation workers return an integrated change and reproducible evidence;
  the PM verifies the whole Work Package, not only a commit.
- Verification workers report failures as well as passes; they cannot waive
  acceptance criteria or residual risk.
- Exception handoffs interrupt only affected work. The PM resolves within
  authority or asks the Human one focused decision.

`VERIFYING` means the handoff has been submitted. `DONE` or `REWORK` means the
PM consumed it. No separate handoff status is introduced. Repository artifact
validation re-checks every submitted or consumed handoff so later corruption or
deletion is visible. Submission records a content hash; the producer must not
edit the handoff while it is `VERIFYING` or after consumption. `REWORK` returns
it to `ACTIVE`, clears the prior submission, and permits revision.
