# Change, Priority, and Resume Rules

## First contact with a project

After repository inspection, classify the start from durable evidence:

- **blank Meta PDS context:** no valid initiative, decision log, or delivery
  state exists;
- **existing product evidence without Meta PDS context:** code, documentation,
  issues, or Git history exists but canonical Meta PDS artifacts do not;
- **resumable context:** canonical artifacts establish the initiative and
  current state.

For blank context, do not produce a generic missing-files error and stop. Give
the dashboard URL, say plainly that no Meta PDS product context exists yet,
state that no sample assumptions or requirements will be created, and
recommend a short initiative brief. Ask only:

1. what are we building and for whom;
2. what problem or measurable outcome matters most;
3. what fixed constraints, existing material, or approval boundaries apply.

State that Meta PDS will begin in `EXPLORE`, capture candidate Truth without
interrupting brainstorming, and require Human approval before locking
consequential decisions. Establish the authority envelope before autonomous
delivery work. Do not create canonical artifacts merely to make the dashboard
look populated; create each artifact only when its lifecycle begins.

When repository evidence exists without Meta PDS context, precede the same
questions with a concise **Observed in this repository** summary. Separate
facts from interpretations and do not infer the product goal, target user,
acceptance, or delivery authority from code structure alone.

## Resume

Read canonical artifacts and repository/runtime evidence, reconcile them, then
present the visibility summary. Never ask the Human to reconstruct yesterday's
state from memory.

Use this concise daily recap, omitting empty lines rather than filling them
with invented content:

```text
Welcome back. Quick recap:
Current phase and interaction mode:
Recently locked or proposed Truth:
Active planning and execution slices:
Active Scrum Board tasks and assignees:
Work completed since the durable checkpoint:
Open blockers, drift, and Human approvals:
Current branch and verified PR state:
Recommended next action:
Safe alternatives:
Dashboard:
```

Derive every line from canonical artifacts, verified repository/runtime
evidence, and append-only delivery events—not conversation memory. If nothing
changed, say that directly. If the Human provided a valid concrete request,
keep the recap brief and continue that request; never turn the recap into a
ceremonial blocker.

## Priority changes

- Reorder unstarted slices after dependency-impact analysis.
- Pause active work only at a safe checkpoint with commits, state, blockers,
  and resume action recorded.
- Planning may prepare the next slice while the current slice develops.
- Do not execute a second slice until capacity exists and dependencies are
  revalidated.

## Locked-decision changes

Classify new evidence:

- reversible technical detail preserving behavior and risk: downstream owner
  may decide, record evidence, and continue;
- product scope, acceptance, public contract, or security boundary change:
  return upstream and obtain the required approval;
- destructive, irreversible, materially costly, or legally significant change:
  require Human approval before affected work proceeds.

Record the mismatch in `drift-log.yaml`, including affected artifacts and work
packages, owner, recommendation, required revalidation, confidence, and Human
approval when applicable. Pause only the affected dependency closure and keep
independent ready work moving. Do not silently patch stale documents.

## Released behavior

- Original acceptance is broken: create a defect/hotfix linked to the released
  slice.
- New or changed behavior: create a new linked slice.
- Security incident: use an expedited emergency path with preserved evidence
  and required authority.

Never reopen or rewrite released slice history.
