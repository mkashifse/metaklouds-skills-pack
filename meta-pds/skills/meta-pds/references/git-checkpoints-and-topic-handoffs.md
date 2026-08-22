# Git Checkpoints and Topic Handoffs

## Repository and branch model

Use the product's single Git repository and follow its existing branch naming
convention. When the repository has no convention, use these topic branches:

```text
codex/<initiative-id>-discovery
codex/<slice-id>-planning
codex/<slice-id>-delivery
codex/<slice-id>-<defect-id>
```

The Product Manager owns discovery, planning, delivery-integration, and
remediation branches. Development workers may use short-lived assigned work
package branches based on the active delivery branch. Do not create nested Git
repositories, submodules, or branches that mix unrelated initiatives or slices.

Before creating or switching a branch, inspect the current branch, worktree,
and unpushed commits. Preserve unrelated Human changes. Do not commit, stash,
discard, or relocate files outside the active assignment.

## Checkpoint commits

Keep completed work durable through local commits at meaningful checkpoints:

- a prototype round is ready for Human review;
- an initiative decision or revision is approved and recorded;
- a slice draft or revision passes its structural checks;
- an execution plan or work package reaches a durable state;
- QA evidence or a gate transition is recorded;
- work pauses, context is handed off, or the Human changes topic.

Before a normal checkpoint commit, inspect the exact changed paths and run the
relevant validation and tests. Commit only active-topic paths. Use a concise
message containing the initiative, slice, decision, or work-package identity.
Do not create noise commits for editor saves or unchanged files.

Development workers commit their assigned code and test paths locally and
return commit hashes. Functional leads return their owned artifact changes to
the Product Manager. Under `META_PDS_GIT_AUTHORITY=PM_ONLY`, only the Product
Manager commits canonical Meta PDS artifacts, prototype checkpoints, execution
plans, and QA reports.

If a topic handoff occurs before work is complete, preserve recoverable work in
an explicit local WIP checkpoint only when the changed paths are understood.
Record failing checks, blockers, and the exact resume action. Never represent a
WIP commit as validated or ready to merge.

## Topic-change detection and nudge

A topic change means the Human moves to another initiative, slice, defect, or
unrelated repository objective. A clarification, status question, review, or
small correction within the active objective is not a topic change.

At a topic change:

1. Inspect the active branch, working tree, validation state, and commits ahead
   of its base.
2. Create the appropriate local checkpoint for in-scope uncommitted work.
3. Report the branch, checkpoint commit, checks, and remaining blockers.
4. When the branch contains unmerged durable work, give one concise nudge:
   recommend creating a PR and merging it after required checks and approvals;
   offer keeping the branch open or parking it when merge readiness is absent.
5. Do not repeat the nudge on every message unless branch readiness changes.

A topic-change nudge is not authority to push, open a PR, merge, deploy, or
release. Perform those external actions only when the authority envelope
delegates them. Never recommend merging a WIP, structurally invalid artifact,
failed implementation, or QA-rejected slice. A draft PR may preserve review
visibility when work is not merge-ready.

## Upstream changes

Commit an approved initiative, decision, or slice revision on its PM-owned
topic branch before synchronizing downstream delivery work. Merge the upstream
change first, then update affected delivery or work-package branches, mark them
`REVERIFY_REQUIRED`, and rerun the cited checks. Never patch locked upstream
content inside a development worker branch.
