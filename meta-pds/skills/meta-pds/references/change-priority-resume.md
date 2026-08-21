# Change, Priority, and Resume Rules

## Resume

Read canonical artifacts and repository/runtime evidence, reconcile them, then
present the visibility summary. Never ask the Human to reconstruct yesterday's
state from memory.

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

Record the decision, affected artifacts and work packages, owner, required
revalidation, and Human approval when applicable. Do not silently patch stale
documents.

## Released behavior

- Original acceptance is broken: create a defect/hotfix linked to the released
  slice.
- New or changed behavior: create a new linked slice.
- Security incident: use an expedited emergency path with preserved evidence
  and required authority.

Never reopen or rewrite released slice history.
