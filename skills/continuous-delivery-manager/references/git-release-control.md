# CDM Git and Release Control

## Preflight

Before every mutation:

1. Resolve exact root, frontend, and backend repository paths.
2. Inspect status, current branch, remotes, upstreams, recent commits, tags, and
   repository instructions.
3. Preserve unrelated work and reject ambiguous targets.
4. Verify frontend and backend contain independent `.git` directories.
5. Verify root ignores both exact nested directories and tracks neither as
   files, submodules, nor gitlinks.
6. Read the slice compatibility, migration, merge, deployment, feature-flag,
   and rollback plan.
7. Check branch protection, required approvals, CI, deployment authority, and
   version conventions.

Never force-push, rewrite a published tag, bypass required checks, or use a
broad staging command without inspecting the staged file list.

## Root integration

- Keep canonical initiative, slice, delivery, CDM control, and release evidence
  in root.
- Review team-owned changes before staging.
- Stage only accepted root-owned paths.
- Inspect the staged diff and verify nested repositories are absent.
- Commit and push directly to root `main`; do not create a root PR.
- If root `main` advanced, synchronize normally, reread append-only documents,
  reconcile without erasing evidence, revalidate, and push without force.

## Code integration

- Use `slice/<slice-key>` in frontend and backend.
- Verify Dev Team local commits and complete changed-file lists.
- Push the two slice branches only after root launch artifacts are accepted.
- Create or update exactly one frontend PR and one backend PR.
- Cross-link slice key, root contract commit, compatibility plan, tests,
  migration, merge/deploy order, feature flag, and rollback in both PRs.
- Observe required reviews and CI. Never treat a push or open PR as acceptance.

## Merge and deployment

1. Prefer additive and backward-compatible changes.
2. Follow the recorded expand → migrate → switch → contract sequence.
3. Merge and deploy in the slice's explicit order.
4. Keep incomplete behavior hidden behind the recorded feature flag.
5. Verify compatibility after each merge and deployment step.
6. Run contract, integration, security, migration, regression, and whole-slice
   E2E checks.
7. Enable the release flag only after both deployed sides pass the release
   gate.
8. Record monitoring, support, and rollback evidence.

One merged or deployed component is integration progress, never a partial slice
release.

## Versions and tags

Use the shared slice key for cross-repository identity while allowing each code
repository to keep its own version sequence.

For each code repository:

1. Read its version policy, manifests, changelog, and existing tags.
2. Determine the required semantic increment from the delivered change and
   repository policy.
3. If no policy exists, propose one and require user approval before the first
   release.
4. Update required version and changelog files.
5. Verify the version commit is the accepted merge commit or an explicit
   release commit allowed by repository policy.
6. Create an immutable annotated release tag using the existing convention.
7. If a requested tag already exists, verify it targets the exact expected
   commit. Escalate any mismatch; never move it.

Do not force frontend and backend to share the same semantic version.

After successful deployment and E2E:

1. Complete `docs/releases/<slice-key>.md`.
2. Commit and push the manifest and final delivery-control checkpoint to root
   `main`.
3. Create annotated root tag `release/<slice-key>` on that exact commit.
4. Verify the root tag plus frontend and backend tags are mutually cross-linked
   in the release manifest.

## Idempotency and recovery

Before retrying an action, inspect whether it already succeeded:

- branch exists at expected commit;
- commit exists on expected remote;
- PR exists for the expected head and base;
- CI run belongs to the expected commit;
- merge commit matches the accepted PR;
- tag targets the expected commit;
- deployment identifies the expected artifact;
- release manifest records the same immutable evidence.

Reuse matching state. Do not create duplicate PRs, tags, releases, deployments,
or control records.

On failure, record:

- expected and observed state;
- last trustworthy checkpoint;
- affected repository and slice;
- whether rollback is required;
- owner and exact remediation;
- retry fingerprint and count.

Return code defects to Dev Team. Return slice defects to Vertical Slice Team.
Return initiative intent defects to Meta Grill. Require the user for destructive
recovery or authority outside the recorded envelope.
