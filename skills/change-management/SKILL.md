---
name: change-management
description: Lightweight runtime change-control protocol for team leads. Use when new evidence, prototype feedback, implementation constraints, or cross-document misalignment requires a decision after requirements were locked; records the decision in change-management.md, determines lead versus human approval, runs a quick impact analysis, and keeps unaffected work moving.
---

# Change Management

Resolve uncommon runtime changes without normalizing silent scope drift or
turning routine delivery into an approval queue.

## Canonical file

Use one append-only file per initiative:

```text
docs/initiatives/<initiative-id>/change-management.md
```

Create it from
[assets/change-management-template.md](assets/change-management-template.md)
when the initiative starts. The Initiative Lead, Planning Lead, and Engineering
Manager may append and lock records. Never delete or rewrite a locked record;
append a correction or superseding change.

The active team's lead is the single writer while that stage is active. Other
leads submit evidence or synchronization results to that lead. Before allocating
an ID or writing, re-read the file; use the next unused `CHG-000N`. If a
collision is found before lock, renumber the newer draft. Never renumber a
locked record.

Routine implementation details that do not change locked behavior, scope,
contracts, risk, or acceptance belong in normal team documents, not this log.

## Decision authority

A team lead may decide and lock a change without waiting when all are true:

- the lead is confident and has evidence;
- the change remains inside the approved initiative outcome and non-goals;
- it is contained, reversible, and does not remove a mandatory lifecycle flow;
- it does not trigger a severe-change condition below;
- affected owners can execute it without unresolved cross-team conflict.

Log the decision, continue affected work, and inform the user with a concise
decision and impact summary. “Inform” is not an approval gate.

Require human approval when the change:

- materially changes the target user, business outcome, success measure,
  initiative scope, non-goal, or fat-slice release promise;
- creates material security, privacy, compliance, legal, safety, or data-loss
  risk;
- is destructive, hard to reverse, or requires an irreversible migration;
- breaks a public/external contract or makes a foundational architecture,
  vendor, spend, or operating-model commitment;
- materially changes release risk, cost, or schedule;
- lacks lead confidence or has unresolved disagreement between accountable
  leads.

Resolve the human approver from the PRD's decision-authority section. For a
single-user workflow, the requesting user is the default approver. For multiple
stakeholders, use the named owner for product/business, security/compliance,
architecture/vendor/spend, or release decisions. If authority is missing or
contested, ask the requesting user to identify it before locking the affected
change; unrelated work continues.

Set the record to `AWAITING_HUMAN_APPROVAL` and pause only affected work.
Continue unrelated work. After approval or rejection, record the human,
timestamp, decision, and rationale; then lock the record.

## Runtime workflow

1. Detect and state the misalignment or new evidence.
2. Search existing change records to avoid duplication or contradiction.
3. Allocate the next `CHG-000N` ID and record the originating team/lead.
4. Classify authority as `LEAD` or `HUMAN_REQUIRED`.
5. Record options considered, recommendation, evidence, reversibility, and
   affected work.
6. Decide:
   - lead-authorized: set `LOCKED`, proceed, and inform the user;
   - human-required: set `AWAITING_HUMAN_APPROVAL`, ask one focused decision,
     and pause only affected work.
7. After the decision is locked, run and record the quick impact analysis.
8. Update documents owned by the current team. Assign named owners for other
   affected documents; the locked change record is the temporary authoritative
   overlay until synchronization completes.
9. Notify downstream leads and continue delivery.

## Synchronization gates

A locked change may temporarily overlay stale documents while affected work
continues, but it cannot cross these gates:

- `READY_FOR_SLICE_PLANNING`: all affected PRD, UX, prototype-validation,
  context, and ADR artifacts are synchronized.
- `READY_FOR_DEV_TEAM`: all affected initiative and vertical-slice artifacts
  are synchronized.
- Dev-team worker launch: story map, stories/tasks, technical design, contract,
  and test plan reflect every relevant locked change.
- `COMPLETE`: all canonical documents, production contracts/code, tests,
  rollout/rollback evidence, and repository records are synchronized.

If synchronization cannot finish at a gate, record the blocker and stop only
that transition.

## Quick impact analysis

Immediately after locking, assess:

- PRD, business rules, success measures, and terminology;
- UX specification, prototype flows, navigation, fixtures, and state coverage;
- vertical-slice scope, lifecycle completeness, acceptance, and sequencing;
- user stories, engineering tasks, contracts, architecture, API, and data;
- security, privacy, compliance, accessibility, and operational risk;
- tests, migrations, rollout, rollback, repositories, owners, cost, and
  schedule.

For each area, record `NONE`, `UPDATE_REQUIRED`, or `REPLAN_REQUIRED`, with an
owner and action. Escalate a newly discovered severe impact even if the original
change was lead-authorized.

## Boundaries

- Do not use change management to bypass fat-slice completeness.
- Do not let a downstream lead silently redefine upstream intent.
- Do not pause the entire workflow when only one flow, story, or repository is
  affected.
- Do not treat notification as a request for approval when lead authority is
  sufficient.
- Do not mark document synchronization complete without traceable updates.
