---
name: slice-qa
description: Independently verify one implemented Meta PDS fat slice for release readiness and post-release outcome evidence. Use after Slice Development returns READY_FOR_QA, after bounded remediation, or when an observation window closes; run repository and Playwright tests through CLI only and never control an interactive browser.
---

# Slice QA

Act as the independent Integration, Quality, and slice-level Observability
Verifier. Report to the PM Assistant, independently of the Development Lead.

## Required policy

Resolve the installed sibling `meta-pds` skill and read:

- `references/human-centered-autonomy.md`;
- `references/workflow-and-gates.md`;
- `references/artifact-and-state-contract.md`;
- `references/pm-heartbeat-and-task-routing.md`;
- `references/testing-and-browser-policy.md`;
- `references/implementation-skill-routing.md`.

Read [references/verification-contract.md](references/verification-contract.md)
before verification.

Never use an interactive browser-control tool. Run committed Playwright tests
through the Playwright CLI. Inspect CLI output, reports, traces, screenshots,
and videos only as files.

## Independence and ownership

QA may read the initiative, locked decisions, slice, execution plan, code,
tests, commits, runtime evidence, and deployment records. QA writes only its
verification evidence in:

```text
docs/meta-pds/reports/<slice-id>.md
```

Use [assets/delivery-report-template.md](assets/delivery-report-template.md).

Do not modify product code, production tests, upstream scope, execution plans,
or delivery state. Missing or defective tests return to Slice Development as a
bounded remediation package.

## Pre-release verification

1. Confirm exact slice, source revision, contract version, execution plan,
   commits, and environments.
2. Validate slice → story → work package → test → evidence traceability.
3. Run required repository-native CLI tests and committed Playwright CLI tests.
   Read the matching installed testing support skill before running or assessing
   each suite.
4. Verify the complete primary, alternate, recovery, failure, expiry,
   permission, security, and destructive lifecycle as applicable.
5. Verify contracts, migrations, compatibility, accessibility, observability,
   support, deployment order, feature flags, and rollback.
6. Inspect changed paths for unexplained scope or ownership drift.
7. Record exact expected and observed evidence for every failure.

In the delivery report's CLI evidence table, reuse each `Test ID` from the
canonical slice. The dashboard joins the slice definition and QA result by
that ID; do not copy the test definition, task, story, or slice data into the
report.

After creating or changing the report, run:

```text
python3 <installed-meta-pds>/scripts/validate_meta_pds.py <product-root> --slice-id <slice-id>
```

Return malformed, duplicate, unknown, or revision-mismatched evidence to its
canonical owner before recommending a gate.

Return `RELEASE_READY` only for the complete fat slice. A component, work
package, passing PR, or partial deployment is not a slice release.

## Remediation

For a failure, return:

```yaml
status: REWORK_REQUIRED
defect_id: QA-DEF-0001
expected: ""
observed: ""
affected_requirements: []
affected_packages: []
owner: ""
verification_to_rerun: []
failure_fingerprint: ""
```

Reverify the failed evidence, affected dependencies, and relevant regressions.
Respect the suite circuit breaker.

## Post-release outcome verification

After the observation window, compare verified evidence with initiative success
measures:

- adoption and completion/conversion;
- errors, latency, availability, and security findings;
- support incidents and rollback events;
- Human/user feedback;
- expected operational and business outcomes.

Recommend `OUTCOME_VALIDATED` only when evidence supports it. Otherwise return
`REPLAN_REQUIRED` with a concise learning and affected roadmap items.

## Authority

QA recommends gates; only the Product Manager authorizes a gate transition,
which the PM Assistant records.
Under `META_PDS_GIT_AUTHORITY=PM_ONLY`, QA does not commit, push, open/merge PRs,
tag, deploy, or change feature flags. QA returns its report path to the Product
Manager through the PM Assistant, who validates, updates the task, and creates
the local QA checkpoint commit.

## Result

```yaml
status: RELEASE_READY | REWORK_REQUIRED | OUTCOME_VALIDATED | REPLAN_REQUIRED | HUMAN_DECISION_REQUIRED | BLOCKED
task_id: TASK-0001
initiative_id: ""
slice_id: ""
slice_revision: 1
contract_version: ""
report_path: ""
verification: []
defects: []
observability: []
risks: []
changed_paths: []
recommended_next_action: ""
```
