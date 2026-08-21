/*
 * Demonstration projection for the Meta PDS dashboard.
 * Replace this object from canonical artifacts; never treat it as authority.
 */
window.META_PDS_DASHBOARD_DATA = {
  schemaVersion: 1,
  projection: {
    kind: "seed-demonstration",
    generatedAt: "2026-08-21T22:42:00+05:00",
    source: "Meta PDS seed artifacts",
    staleAfterMinutes: 90
  },
  initiative: {
    id: "INIT-0042",
    name: "Learning Platform V1",
    shortName: "Learning Platform",
    phase: "PROTOTYPING",
    health: "ON_TRACK",
    progress: 62,
    objective: "A focused learning experience from secure access to measurable progress.",
    humanOwner: "Human Product Owner",
    currentRevision: 3,
    nextAction: {
      title: "Review password recovery prototype",
      detail: "Confirm the recovery route before Slice 02 planning locks.",
      owner: "Human review",
      impact: "Unblocks 2 work items"
    }
  },
  attention: [
    {
      id: "ATT-01",
      kind: "decision",
      title: "Choose the account recovery route",
      detail: "Email link and one-time-code variants are ready for manual review.",
      age: "12 min",
      affects: ["SLICE-02"]
    },
    {
      id: "ATT-02",
      kind: "review",
      title: "Validate the expired-session experience",
      detail: "Manual navigation is required before the prototype checkpoint can close.",
      age: "24 min",
      affects: ["DEC-009"]
    },
    {
      id: "ATT-03",
      kind: "blocker",
      title: "Confirm transactional email provider",
      detail: "Development can continue locally, but production recovery cannot release.",
      age: "1 hr",
      affects: ["WP-BE-12"]
    }
  ],
  prototype: {
    id: "PROTO-0042-AUTH",
    name: "Authentication journeys",
    description: "Testing recovery, validation, and expired-session states with local fixtures.",
    status: "HUMAN_REVIEW",
    checkpoint: "Checkpoint 07",
    checkpointAt: "2026-08-21T22:36:00+05:00",
    route: "/prototype/auth",
    persistence: "localStorage",
    seedProfiles: 4,
    journeys: {
      reviewed: 5,
      total: 7
    },
    assumptionsTested: 6,
    openQuestions: 2,
    manualReview: "Awaiting Human"
  },
  decisions: [
    {
      id: "DEC-003",
      title: "Email and password are the initial sign-in methods",
      summary: "Social sign-in stays outside V1 scope until adoption evidence exists.",
      status: "LOCKED",
      revision: 2,
      updatedAt: "2026-08-21T20:05:00+05:00",
      affects: ["SLICE-01", "SLICE-02"]
    },
    {
      id: "DEC-006",
      title: "Learner and instructor roles stay explicit",
      summary: "Role switching is not allowed within one active session.",
      status: "LOCKED",
      revision: 1,
      updatedAt: "2026-08-21T20:48:00+05:00",
      affects: ["SLICE-01", "SLICE-03"]
    },
    {
      id: "DEC-008",
      title: "Recovery uses a single-use email link",
      summary: "The prototype is comparing link-only and link-plus-code recovery.",
      status: "TESTING",
      revision: 3,
      updatedAt: "2026-08-21T22:30:00+05:00",
      affects: ["SLICE-02"]
    },
    {
      id: "DEC-009",
      title: "Expired sessions preserve the intended destination",
      summary: "After sign-in, the learner returns to the page that required access.",
      status: "PROPOSED",
      revision: 1,
      updatedAt: "2026-08-21T22:18:00+05:00",
      affects: ["SLICE-01"]
    },
    {
      id: "DEC-010",
      title: "Prototype stores fixtures in localStorage",
      summary: "Local persistence supports manual review without a temporary backend.",
      status: "LOCKED",
      revision: 1,
      updatedAt: "2026-08-21T19:40:00+05:00",
      affects: ["PROTO-0042-AUTH"]
    },
    {
      id: "DEC-002",
      title: "Invite-only learner onboarding",
      summary: "Replaced by controlled self-registration with email verification.",
      status: "SUPERSEDED",
      revision: 2,
      updatedAt: "2026-08-20T17:15:00+05:00",
      affects: ["SLICE-01"]
    }
  ],
  slices: [
    {
      id: "SLICE-01",
      order: 1,
      title: "Identity and secure access",
      outcome: "A learner can create, verify, and securely access an account.",
      status: "RELEASED",
      progress: 100,
      revision: 4,
      priority: "P0",
      dependencies: [],
      stories: 5,
      active: false
    },
    {
      id: "SLICE-02",
      order: 2,
      title: "Account recovery",
      outcome: "A learner can recover access without support intervention.",
      status: "IN_PROGRESS",
      progress: 58,
      revision: 2,
      priority: "P0",
      dependencies: ["SLICE-01"],
      stories: 4,
      active: true
    },
    {
      id: "SLICE-03",
      order: 3,
      title: "Course discovery and enrolment",
      outcome: "A learner can find an eligible course and begin learning.",
      status: "READY_FOR_DEVELOPMENT",
      progress: 26,
      revision: 3,
      priority: "P1",
      dependencies: ["SLICE-01"],
      stories: 6,
      active: false
    },
    {
      id: "SLICE-04",
      order: 4,
      title: "Learning progress",
      outcome: "A learner can resume and understand progress across lessons.",
      status: "DRAFT",
      progress: 9,
      revision: 1,
      priority: "P1",
      dependencies: ["SLICE-03"],
      stories: 5,
      active: false
    },
    {
      id: "SLICE-05",
      order: 5,
      title: "Instructor reporting",
      outcome: "An instructor can identify engagement and completion risks.",
      status: "PROPOSED",
      progress: 0,
      revision: 0,
      priority: "P2",
      dependencies: ["SLICE-04"],
      stories: 0,
      active: false
    }
  ],
  workPackages: [
    {
      id: "WP-BE-08",
      sliceId: "SLICE-01",
      title: "Session and refresh-token lifecycle",
      description: "Issue, rotate, revoke, and audit authenticated sessions.",
      status: "DONE",
      area: "backend",
      owner: "Backend Engineer",
      ownerInitials: "BE",
      storyIds: ["US-101", "US-103"],
      dependsOn: [],
      tests: { passed: 18, total: 18 },
      critical: true
    },
    {
      id: "WP-FE-09",
      sliceId: "SLICE-01",
      title: "Accessible sign-in states",
      description: "Render validation, loading, failure, and session-expired states.",
      status: "DONE",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-101", "US-103"],
      dependsOn: ["WP-BE-08"],
      tests: { passed: 14, total: 14 },
      critical: false
    },
    {
      id: "WP-QA-10",
      sliceId: "SLICE-01",
      title: "Identity lifecycle verification",
      description: "Verify registration, verification, sign-in, expiry, and sign-out.",
      status: "DONE",
      area: "integration",
      owner: "Slice QA",
      ownerInitials: "QA",
      storyIds: ["US-101", "US-102", "US-103"],
      dependsOn: ["WP-BE-08", "WP-FE-09"],
      tests: { passed: 11, total: 11 },
      critical: true
    },
    {
      id: "WP-DB-11",
      sliceId: "SLICE-02",
      title: "Recovery token persistence",
      description: "Store hashed single-use tokens with expiry and audit metadata.",
      status: "VERIFYING",
      area: "database",
      owner: "Database Engineer",
      ownerInitials: "DB",
      storyIds: ["US-201", "US-203"],
      dependsOn: [],
      tests: { passed: 8, total: 8 },
      critical: true
    },
    {
      id: "WP-BE-12",
      sliceId: "SLICE-02",
      title: "Recovery request and redemption API",
      description: "Create rate-limited recovery requests and redeem valid tokens.",
      status: "BLOCKED",
      area: "backend",
      owner: "Backend Engineer",
      ownerInitials: "BE",
      storyIds: ["US-201", "US-202"],
      dependsOn: ["WP-DB-11"],
      tests: { passed: 9, total: 13 },
      critical: true,
      blocker: "Transactional email provider decision"
    },
    {
      id: "WP-FE-13",
      sliceId: "SLICE-02",
      title: "Recovery request interface",
      description: "Collect account email and show privacy-safe confirmation states.",
      status: "IN_PROGRESS",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-201"],
      dependsOn: [],
      tests: { passed: 5, total: 8 },
      critical: false
    },
    {
      id: "WP-FE-14",
      sliceId: "SLICE-02",
      title: "Set-new-password interface",
      description: "Validate an active recovery session and set a compliant password.",
      status: "READY",
      area: "frontend",
      owner: "Frontend Engineer",
      ownerInitials: "FE",
      storyIds: ["US-202", "US-203"],
      dependsOn: ["WP-DB-11"],
      tests: { passed: 0, total: 7 },
      critical: true
    },
    {
      id: "WP-INT-15",
      sliceId: "SLICE-02",
      title: "Recovery lifecycle integration",
      description: "Verify expiry, replay prevention, notification, and session invalidation.",
      status: "BLOCKED",
      area: "integration",
      owner: "Integration Engineer",
      ownerInitials: "IE",
      storyIds: ["US-201", "US-202", "US-203", "US-204"],
      dependsOn: ["WP-BE-12", "WP-FE-13", "WP-FE-14"],
      tests: { passed: 0, total: 12 },
      critical: true,
      blocker: "Upstream packages incomplete"
    },
    {
      id: "WP-CT-16",
      sliceId: "SLICE-03",
      title: "Course catalogue contract",
      description: "Freeze browse, eligibility, enrolment, and error payloads.",
      status: "READY",
      area: "integration",
      owner: "Development Lead",
      ownerInitials: "DL",
      storyIds: ["US-301"],
      dependsOn: [],
      tests: { passed: 0, total: 5 },
      critical: false
    }
  ],
  stories: [
    {
      id: "US-101",
      sliceId: "SLICE-01",
      title: "Sign in with a verified account",
      status: "DONE",
      workPackageIds: ["WP-BE-08", "WP-FE-09", "WP-QA-10"],
      acceptance: { passed: 7, total: 7 }
    },
    {
      id: "US-102",
      sliceId: "SLICE-01",
      title: "Verify a newly registered email",
      status: "DONE",
      workPackageIds: ["WP-QA-10"],
      acceptance: { passed: 5, total: 5 }
    },
    {
      id: "US-103",
      sliceId: "SLICE-01",
      title: "Recover from an expired session",
      status: "DONE",
      workPackageIds: ["WP-BE-08", "WP-FE-09", "WP-QA-10"],
      acceptance: { passed: 6, total: 6 }
    },
    {
      id: "US-201",
      sliceId: "SLICE-02",
      title: "Request account recovery safely",
      status: "IN_PROGRESS",
      workPackageIds: ["WP-DB-11", "WP-BE-12", "WP-FE-13", "WP-INT-15"],
      acceptance: { passed: 4, total: 7 }
    },
    {
      id: "US-202",
      sliceId: "SLICE-02",
      title: "Set a new password from a valid link",
      status: "READY",
      workPackageIds: ["WP-BE-12", "WP-FE-14", "WP-INT-15"],
      acceptance: { passed: 2, total: 6 }
    },
    {
      id: "US-203",
      sliceId: "SLICE-02",
      title: "Reject expired or replayed recovery links",
      status: "VERIFYING",
      workPackageIds: ["WP-DB-11", "WP-FE-14", "WP-INT-15"],
      acceptance: { passed: 4, total: 6 }
    },
    {
      id: "US-204",
      sliceId: "SLICE-02",
      title: "Notify the account owner after recovery",
      status: "BLOCKED",
      workPackageIds: ["WP-BE-12", "WP-INT-15"],
      acceptance: { passed: 0, total: 4 }
    },
    {
      id: "US-301",
      sliceId: "SLICE-03",
      title: "Browse courses available for enrolment",
      status: "READY",
      workPackageIds: ["WP-CT-16"],
      acceptance: { passed: 0, total: 5 }
    }
  ],
  dependencies: {
    criticalPath: ["WP-DB-11", "WP-BE-12", "WP-FE-14", "WP-INT-15"],
    currentNode: "WP-BE-12",
    risk: "MEDIUM",
    readyPackages: 2,
    blockedPackages: 2,
    executionWave: "Wave 2 of 4",
    nextUnblock: "Approve email provider or record a local-only adapter"
  },
  quality: {
    evidenceCoverage: 74,
    suites: [
      { name: "Unit and component", passed: 54, total: 58 },
      { name: "API contract", passed: 17, total: 21 },
      { name: "Playwright CLI", passed: 11, total: 16 },
      { name: "Security checks", passed: 8, total: 10 }
    ],
    openDefects: 2,
    criticalDefects: 0,
    lastVerifiedAt: "2026-08-21T22:11:00+05:00"
  },
  release: {
    status: "NOT_READY",
    target: "Local integration",
    gates: [
      { name: "Planning revision locked", status: "PASSED" },
      { name: "Execution packages complete", status: "IN_PROGRESS" },
      { name: "Independent QA evidence", status: "NOT_READY" },
      { name: "Rollout and rollback prepared", status: "READY" }
    ],
    featureFlag: "account-recovery-v1",
    rollback: "Disable flag; retain token audit records"
  },
  drift: [
    {
      id: "DRIFT-01",
      severity: "medium",
      title: "Provider choice is outside the locked execution contract",
      detail: "The affected backend package is paused; independent frontend work continues.",
      affects: "WP-BE-12"
    },
    {
      id: "DRIFT-02",
      severity: "info",
      title: "Slice 03 contract package is ready early",
      detail: "Planning may continue without consuming the active development WIP slot.",
      affects: "SLICE-03"
    },
    {
      id: "DRIFT-03",
      severity: "low",
      title: "One proposed decision has no Human response",
      detail: "Expired-session destination remains proposed and cannot be treated as locked.",
      affects: "DEC-009"
    }
  ],
  activity: [
    {
      at: "2026-08-21T22:42:00+05:00",
      kind: "prototype",
      title: "Prototype checkpoint recorded",
      detail: "Recovery and expired-session variants prepared for manual review."
    },
    {
      at: "2026-08-21T22:30:00+05:00",
      kind: "decision",
      title: "DEC-008 moved to TESTING",
      detail: "Two recovery variants remain visible; no product behavior was locked."
    },
    {
      at: "2026-08-21T22:11:00+05:00",
      kind: "completed",
      title: "WP-DB-11 entered VERIFYING",
      detail: "Migration and token replay tests passed locally."
    },
    {
      at: "2026-08-21T21:54:00+05:00",
      kind: "blocked",
      title: "WP-BE-12 paused safely",
      detail: "External provider decision escalated; unrelated work remained active."
    },
    {
      at: "2026-08-21T20:48:00+05:00",
      kind: "decision",
      title: "DEC-006 locked by Human",
      detail: "Learner and instructor sessions keep explicit roles."
    },
    {
      at: "2026-08-21T19:32:00+05:00",
      kind: "completed",
      title: "SLICE-01 released",
      detail: "Identity lifecycle passed independent QA and local release evidence."
    }
  ]
};
