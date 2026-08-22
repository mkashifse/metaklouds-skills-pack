(async function () {
  "use strict";

  const demoRequested = new URLSearchParams(location.search).get("demo") === "1";
  const safeError = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  let data;
  try {
    if (location.protocol === "file:") throw new Error("Launch the Meta PDS dashboard service from the product root; direct file access cannot read canonical artifacts.");
    const response = await fetch(demoRequested ? "/api/dashboard?demo=1" : "/api/dashboard", { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) {
      const firstDiagnostic = payload.diagnostics?.[0];
      const detail = firstDiagnostic ? `${firstDiagnostic.file}: ${firstDiagnostic.message}` : "";
      throw new Error([payload.error || "Canonical artifact parsing failed.", detail].filter(Boolean).join(" — "));
    }
    data = payload;
  } catch (error) {
    document.body.innerHTML = `<main class="empty-state"><strong>Dashboard unavailable</strong><p>${safeError(error.message || error)}</p></main>`;
    return;
  }

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  const pretty = (value) => String(value ?? "")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());
  const time = (value) => new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(new Date(value));
  const dateTime = (value) => {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? "Unknown" : new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(parsed);
  };
  const externalUrl = (value) => /^https?:\/\//i.test(String(value || "")) ? String(value) : "";
  const setText = (selector, value) => { const node = $(selector); if (node) node.textContent = value; };
  const icon = (name, className = "") => `<svg class="lucide-icon ${esc(className)}" aria-hidden="true" focusable="false"><use href="#icon-${esc(name)}"></use></svg>`;

  const STATUS_TONES = Object.freeze({
    RELEASED: "released", OUTCOME_VALIDATED: "released", DONE: "released", COMPLETED: "released",
    LOCKED: "released", PASSED: "released", VERIFIED: "released", ON_TRACK: "released", MERGED: "released", SYNCED: "released", CLEAN: "released", APPROVED: "released",
    IN_PROGRESS: "active", ACTIVE: "active", EXECUTING: "active", MOBILIZING: "active",
    VERIFYING: "verifying", TESTING: "verifying", HUMAN_REVIEW: "verifying", IN_REVIEW: "verifying", OPEN: "verifying", REVIEW_REQUIRED: "verifying",
    READY: "ready", READY_FOR_DEVELOPMENT: "ready", EXECUTION_READY: "ready", RELEASE_READY: "ready", AHEAD: "ready",
    BLOCKED: "blocked", REWORK_REQUIRED: "blocked", REVERIFY_REQUIRED: "blocked", FAILED: "blocked",
    AT_RISK: "blocked", OFF_TRACK: "blocked", BEHIND: "blocked", AHEAD_BEHIND: "blocked", UPSTREAM_GONE: "blocked", CONFLICTING: "blocked", CHANGES_REQUESTED: "blocked"
  });
  const normalizeStatus = (status) => String(status ?? "").trim().replaceAll("-", "_").replaceAll(" ", "_").toUpperCase();
  const statusLabel = (status) => pretty(normalizeStatus(status));
  const tone = (status) => STATUS_TONES[normalizeStatus(status)] || "draft";

  function badge(status, label = statusLabel(status)) {
    return `<span class="state-badge ${tone(status)}">${esc(label)}</span>`;
  }

  function normalizeProgress(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? Math.min(100, Math.max(0, numeric)) : 0;
  }

  function segmentedProgress(value, status, label) {
    const progress = normalizeProgress(value);
    const progressTone = progress === 100 ? "released" : tone(status);
    const segments = Array.from({ length: 10 }, (_, index) => {
      const fill = Math.min(100, Math.max(0, (progress - (index * 10)) * 10));
      return `<i aria-hidden="true" style="--segment-fill:${fill}%"></i>`;
    }).join("");
    return `<span class="progress-steps ${progressTone}" role="progressbar" aria-label="${esc(label)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}">${segments}</span>`;
  }

  function progressDisplay(value, status, label, className = "") {
    const progress = normalizeProgress(value);
    return `<span class="progress-display ${esc(className)}" title="Derived from current canonical statuses">${segmentedProgress(progress, status, label)}<strong>${progress}%</strong></span>`;
  }

  function sliceStories(sliceId) {
    return data.stories.filter((story) => story.sliceId === sliceId);
  }

  function sliceTasks(sliceId) {
    return data.workPackages.filter((task) => task.sliceId === sliceId);
  }

  function sliceContracts(sliceId) {
    return (data.contracts || []).filter((contract) => contract.sliceId === sliceId);
  }

  function sliceTests(sliceId) {
    return (data.testCases || []).filter((test) => test.sliceId === sliceId);
  }

  function acceptanceLabel(story) {
    if (story.acceptance.evidenceStatus === "VERIFIED") return `${story.acceptance.total}/${story.acceptance.total} verified`;
    return `${story.acceptance.total} criteria`;
  }

  function renderHeader() {
    setText("#slice-count", data.slices.length);
    setText("#decision-count", data.decisions.length);
    setText("#branch-count", data.repository?.branches?.length || 0);
    setText("#projection-source", `${data.projection.source} · schema v${data.schemaVersion}`);
    const isDemo = data.projection.kind === "demo-fixture";
    const demoBanner = $("#demo-banner");
    demoBanner.hidden = !isDemo;
    demoBanner.innerHTML = isDemo ? `
      <div class="demo-marker"><span>Demo</span><strong>Example decision map</strong></div>
      <p>Bundled examples for visual review. They are not project decisions and are never written into this repository.</p>
      <a href="/#truth">Return to live project data</a>` : "";
    setText("#view-authority", isDemo
      ? "Read-only demo view · Bundled examples are not canonical product truth"
      : "Read-only live view · Canonical Meta PDS artifacts remain authoritative");
  }

  function renderDataHealth() {
    const health = data.dataHealth || { status: "VALID", errors: 0, warnings: 0, diagnostics: [] };
    const panel = $("#data-health");
    if (!health.errors && !health.warnings) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    panel.hidden = false;
    panel.innerHTML = `
      <details>
        <summary>${icon("triangle-alert")}<strong>Canonical data needs attention</strong><span>Valid artifacts remain visible; unsafe files are quarantined and other issues are flagged.</span><span class="data-health-count">${esc(health.errors)} errors · ${esc(health.warnings)} warnings</span></summary>
        <ul class="diagnostic-list">${(health.diagnostics || []).map((item) => `<li><code>${esc(item.file)} · ${esc(item.code)}</code><span>${esc(item.message)}</span></li>`).join("")}</ul>
      </details>`;
  }

  let currentView = "slices";
  function showView(view) {
    currentView = view;
    $$(".top-tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.view === view));
    $$(".view-panel").forEach((panel) => panel.classList.toggle("is-active", panel.dataset.panel === view));
    $("#slice-summary").classList.toggle("is-hidden", view !== "slices");
    if (history.replaceState) history.replaceState(null, "", `${location.pathname}${location.search}#${view}`);
  }

  function bindTopTabs() {
    $$(".top-tab").forEach((tab) => tab.addEventListener("click", () => showView(tab.dataset.view)));
    const requested = location.hash.slice(1);
    const resolved = requested === "decisions" ? "truth" : requested;
    showView(["truth", "slices", "repository", "prototype", "activity"].includes(resolved) ? resolved : "slices");
  }

  let sliceFilter = "ALL";
  const collapsedSlices = new Set();
  function matchesFilter(slice) {
    if (sliceFilter === "ALL") return true;
    if (sliceFilter === "ACTIVE") return ["IN_PROGRESS", "VERIFYING"].includes(slice.status);
    if (sliceFilter === "BLOCKED") return sliceTasks(slice.id).some((task) => task.status === "BLOCKED");
    if (sliceFilter === "READY") return ["READY", "READY_FOR_DEVELOPMENT", "EXECUTION_READY"].includes(slice.status);
    if (sliceFilter === "COMPLETE") return ["RELEASED", "OUTCOME_VALIDATED"].includes(slice.status);
    return true;
  }

  function renderSliceSummary() {
    const active = data.slices.filter((slice) => ["IN_PROGRESS", "VERIFYING"].includes(slice.status)).length;
    const complete = data.slices.filter((slice) => ["RELEASED", "OUTCOME_VALIDATED"].includes(slice.status)).length;
    const blocked = data.slices.filter((slice) => sliceTasks(slice.id).some((task) => task.status === "BLOCKED")).length;
    $("#slice-summary").innerHTML = [
      ["Total", data.slices.length], ["Active", active], ["Complete", complete], ["Blocked", blocked]
    ].map(([label, value]) => `<span class="summary-chip">${label}<strong>${value}</strong></span>`).join("");
  }

  function renderSliceFilters() {
    const filters = ["ALL", "ACTIVE", "READY", "BLOCKED", "COMPLETE"];
    $("#slice-filters").innerHTML = filters.map((filter) =>
      `<button class="filter-button ${filter === sliceFilter ? "is-active" : ""}" type="button" data-slice-filter="${filter}">${pretty(filter)}</button>`
    ).join("");
  }

  function activeTaskRows(tasks) {
    let visible = tasks.filter((task) => task.status !== "DONE");
    if (!visible.length) visible = tasks.filter((task) => task.status === "DONE").slice(-2);
    if (!visible.length) return "";
    return `
      <div class="active-work">
        <div class="active-work-label"><span>Work packages</span><span>${Math.min(visible.length, 4)} of ${visible.length} shown</span></div>
        ${visible.slice(0, 4).map((task) => `
          <div class="task-line">
            <span class="task-id">${esc(task.id)}</span>
            <span class="task-name">${esc(task.title)}</span>
            <span class="assignee"><i>${esc(task.ownerInitials)}</i>${esc(task.owner)}</span>
            ${badge(task.status)}
          </div>
        `).join("")}
      </div>`;
  }

  function sliceCard(slice) {
    const stories = sliceStories(slice.id);
    const tasks = sliceTasks(slice.id);
    const tests = sliceTests(slice.id);
    const passedTests = tests.filter((test) => test.status === "PASSED").length;
    const doneTasks = tasks.filter((task) => task.status === "DONE").length;
    const blockers = tasks.filter((task) => task.status === "BLOCKED");
    const dependencies = slice.dependencies.length ? slice.dependencies.join(", ") : "None";
    const collapsed = collapsedSlices.has(slice.id);

    return `
      <article class="slice-item ${collapsed ? "is-collapsed" : ""}" data-slice-id="${esc(slice.id)}">
        <header class="slice-main" data-slice-card-header="${esc(slice.id)}">
          <span class="slice-entity-icon" aria-hidden="true">${icon("layers")}</span>
          <div class="slice-heading-copy">
            <div class="slice-title-row">
              <span class="state-dot ${tone(slice.status)}"></span>
              <span class="slice-code">${String(slice.order).padStart(2, "0")} · ${esc(slice.id)}</span>
              <h2 class="slice-card-title"><button type="button" data-open-slice="${esc(slice.id)}">${esc(slice.title)}</button></h2>
            </div>
          </div>
          <div class="slice-body-copy">
            <p class="slice-outcome"><strong>Outcome:</strong> ${esc(slice.outcome)}</p>
            <div class="slice-meta">
              <span>Priority <strong>${esc(slice.priority)}</strong></span>
              <span>Revision <strong>${esc(slice.revision)}</strong></span>
              <span>Depends on <strong>${esc(dependencies)}</strong></span>
            </div>
          </div>
          <div class="slice-status-summary">
            ${badge(slice.status)}
            ${progressDisplay(slice.progress, slice.status, `${slice.title} completion`, "compact-progress")}
            <span class="compact-stories">Stories <strong>${stories.length}</strong></span>
            <span class="compact-tasks">Tasks <strong>${doneTasks}/${tasks.length}</strong></span>
            <span class="compact-tests">Tests <strong>${passedTests}/${tests.length}</strong></span>
            ${blockers.length ? `<span class="compact-blockers">${blockers.length} blocked</span>` : ""}
          </div>
          <button class="slice-collapse-toggle" type="button" data-toggle-slice-card="${esc(slice.id)}" aria-expanded="${collapsed ? "false" : "true"}" aria-label="${collapsed ? "Expand" : "Collapse"} ${esc(slice.title)} slice">${icon("chevron-down")}</button>
        </header>
        <div class="slice-content">
          ${activeTaskRows(tasks)}
        </div>
      </article>`;
  }

  function renderSlices() {
    renderSliceSummary();
    renderSliceFilters();
    const slices = data.slices.filter(matchesFilter);
    $("#slice-list").innerHTML = slices.length ? slices.map(sliceCard).join("") : '<div class="empty-state">No slices match this filter.</div>';
  }

  function bindSliceList() {
    $("#slice-filters").addEventListener("click", (event) => {
      const button = event.target.closest("[data-slice-filter]");
      if (!button) return;
      sliceFilter = button.dataset.sliceFilter;
      renderSlices();
    });
    $("#slice-list").addEventListener("click", (event) => {
      const open = event.target.closest("[data-open-slice]");
      if (open) {
        openModal(open.dataset.openSlice);
        return;
      }
      const toggle = event.target.closest("[data-toggle-slice-card]");
      const header = event.target.closest("[data-slice-card-header]");
      const id = toggle?.dataset.toggleSliceCard || header?.dataset.sliceCardHeader;
      if (id) {
        collapsedSlices.has(id) ? collapsedSlices.delete(id) : collapsedSlices.add(id);
        renderSlices();
      }
    });
  }

  function renderDecisions() {
    const meta = data.decisionMeta || {};
    $("#decision-summary").innerHTML = [
      ["Current mode", pretty(meta.interactionMode || "EXPLORE"), "mode"],
      ["Total decisions", data.decisions.length, "total"],
      ["Canonical truth", meta.canonicalCount || 0, "canonical"],
      ["Needs review", meta.reviewCount || 0, "review"],
      ["Contradictions", meta.contradictionCount || 0, "contradictions"]
    ].map(([label, value, kind]) => `<div class="decision-stat ${esc(kind)}"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`).join("");

    const statuses = [
      ["ALL", "All"], ["CANONICAL", "Canonical"], ["NEEDS_REVIEW", "Needs review"], ["CONTRADICTORY", "Contradictory"]
    ];
    $("#decision-status-filters").innerHTML = statuses.map(([value, label]) =>
      `<button class="filter-button ${decisionStatusFilter === value ? "is-active" : ""}" type="button" data-decision-status="${value}">${label}</button>`
    ).join("");
    $("#decision-type-filter").innerHTML = `<option value="ALL">All types</option>${(meta.types || []).map((type) => `<option value="${esc(type.id)}">${esc(type.label)}</option>`).join("")}`;
    $("#decision-phase-filter").innerHTML = `<option value="ALL">All phases</option>${(meta.phases || []).map((phase) => `<option value="${esc(phase)}">${esc(pretty(phase))}</option>`).join("")}`;
    $("#decision-type-filter").value = decisionTypeFilter;
    $("#decision-phase-filter").value = decisionPhaseFilter;

    const filtered = data.decisions.filter((decision) => {
      const statusMatch = decisionStatusFilter === "ALL"
        || (decisionStatusFilter === "CANONICAL" && decision.canonical)
        || (decisionStatusFilter === "NEEDS_REVIEW" && decision.needsReview)
        || (decisionStatusFilter === "CONTRADICTORY" && decision.hasContradiction);
      const typeMatch = decisionTypeFilter === "ALL" || decision.type === decisionTypeFilter || decision.secondaryTypes?.some((type) => type.id === decisionTypeFilter);
      const phaseMatch = decisionPhaseFilter === "ALL" || decision.phases?.includes(decisionPhaseFilter);
      return statusMatch && typeMatch && phaseMatch;
    });
    if (!filtered.length) {
      const demoLink = data.projection.kind === "live-project"
        ? '<a class="empty-action" href="?demo=1#truth">Preview bundled demo decisions</a>'
        : "";
      $("#decision-list").innerHTML = `<div class="empty-state"><p>No decisions match these filters.</p>${demoLink}</div>`;
      return;
    }
    const groups = [];
    filtered.forEach((decision) => {
      let group = groups.find((candidate) => candidate.layer === decision.layer);
      if (!group) {
        group = { layer: decision.layer, layerKey: decision.layerKey, decisions: [] };
        groups.push(group);
      }
      group.decisions.push(decision);
    });
    $("#decision-list").innerHTML = groups.map((group) => `
      <section class="decision-group layer-${esc(group.layerKey)}">
        <header><span>${esc(group.layer)}</span><strong>${group.decisions.length}</strong></header>
        <div class="decision-group-list">${group.decisions.map((decision) => `
          <article class="decision-item ${decision.hasContradiction ? "is-contradictory" : ""}">
            <i class="decision-rail" aria-hidden="true"></i>
            <div class="decision-card-head">
              <div class="decision-identity"><code>${esc(decision.key)}</code><span>${esc(decision.id)} · r${esc(decision.revision)}</span></div>
              <div class="decision-labels"><span class="decision-type-label">${esc(decision.typeLabel)}</span>${decision.secondaryTypes.map((type) => `<span class="decision-type-secondary">${esc(type.label)}</span>`).join("")}</div>
              <div class="decision-state">${decision.canonical ? '<span class="decision-canonical">Canonical truth</span>' : ""}${badge(decision.status)}</div>
            </div>
            <div class="decision-copy"><h3>${esc(decision.title)}</h3><p>${esc(decision.summary)}</p>${decision.rationale ? `<small><strong>Why:</strong> ${esc(decision.rationale)}</small>` : ""}</div>
            <div class="decision-context">
              <div><span>Phases</span><p class="decision-phases">${decision.phases.map((phase) => `<em>${esc(pretty(phase))}</em>`).join("")}</p></div>
              <div><span>Depends on</span><p>${decision.dependsOn.length ? decision.dependsOn.map((key) => `<code>${esc(key)}</code>`).join(" ") : "None"}</p></div>
              <div><span>Affects</span><p>${decision.affects.length ? decision.affects.map(esc).join(", ") : "Not recorded"}</p></div>
            </div>
            ${decision.contradictions.length ? `<div class="decision-contradiction">${icon("triangle-alert")}<div><strong>Contradictory decision${decision.contradictions.length > 1 ? "s" : ""}</strong>${decision.contradictions.map((conflict) => `<p><code>${esc(conflict.key)}</code> · ${esc(conflict.title)} · ${badge(conflict.status)}</p>`).join("")}</div></div>` : ""}
          </article>`).join("")}</div>
      </section>`).join("");
  }

  let decisionStatusFilter = "ALL";
  let decisionTypeFilter = "ALL";
  let decisionPhaseFilter = "ALL";

  function bindDecisionControls() {
    $("#decision-status-filters").addEventListener("click", (event) => {
      const button = event.target.closest("[data-decision-status]");
      if (!button) return;
      decisionStatusFilter = button.dataset.decisionStatus;
      renderDecisions();
    });
    $("#decision-type-filter").addEventListener("change", (event) => { decisionTypeFilter = event.target.value; renderDecisions(); });
    $("#decision-phase-filter").addEventListener("change", (event) => { decisionPhaseFilter = event.target.value; renderDecisions(); });
  }

  function renderPrototype() {
    const prototype = data.prototype;
    $("#prototype-card").innerHTML = `
      <div class="prototype-top">
        <div><span class="simple-code">${esc(prototype.id)} · ${esc(prototype.checkpoint)}</span><h2>${esc(prototype.name)}</h2><p>${esc(prototype.description)}</p></div>
        ${badge(prototype.status)}
      </div>
      <div class="prototype-grid">
        <div class="prototype-stat"><span>Journeys reviewed</span><strong>${prototype.journeys.reviewed}/${prototype.journeys.total}</strong></div>
        <div class="prototype-stat"><span>Assumptions tested</span><strong>${prototype.assumptionsTested}</strong></div>
        <div class="prototype-stat"><span>Open questions</span><strong>${prototype.openQuestions}</strong></div>
        <div class="prototype-stat"><span>Human review</span><strong>${esc(prototype.manualReview)}</strong></div>
      </div>`;
  }

  function renderActivity() {
    const activityStatus = (kind) => ({
      approved: "DONE",
      completed: "DONE",
      released: "DONE",
      verifying: "VERIFYING",
      assigned: "READY",
      blocked: "BLOCKED",
      started: "IN_PROGRESS",
      updated: "IN_PROGRESS"
    })[String(kind ?? "").toLowerCase()] || "IN_PROGRESS";
    $("#activity-list").innerHTML = data.activity.length ? data.activity.map((item) => `
      <article class="simple-item">
        <span class="simple-code">${esc(time(item.at))}</span>
        <div class="simple-copy"><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></div>
        ${badge(activityStatus(item.kind), pretty(item.kind))}
      </article>`).join("") : '<div class="empty-state">No durable delivery events are recorded.</div>';
  }

  function repositoryTracking(branch) {
    const parts = [];
    if (branch.upstream) parts.push(branch.upstream);
    if (branch.ahead) parts.push(`${branch.ahead} ahead`);
    if (branch.behind) parts.push(`${branch.behind} behind`);
    if (branch.upstreamGone) parts.push("upstream gone");
    return parts.join(" · ") || "No upstream branch";
  }

  function renderRepository() {
    const repository = data.repository || { available: false, branches: [], pullRequests: [], pullRequestSource: {} };
    setText("#repository-branch-total", repository.branches?.length || 0);
    setText("#repository-pr-total", repository.pullRequests?.length || 0);
    if (!repository.available) {
      $("#repository-summary").innerHTML = `<div class="repository-notice">${icon("triangle-alert")}<div><strong>Git evidence unavailable</strong><span>${esc(repository.message || "The product root is not a Git repository.")}</span></div></div>`;
      $("#repository-branch-list").innerHTML = '<div class="empty-state">No local branches are available.</div>';
      $("#repository-pr-list").innerHTML = '<div class="empty-state">No pull-request evidence is available.</div>';
      return;
    }

    const pullRequestsByNumber = new Map((repository.pullRequests || []).map((pullRequest) => [pullRequest.number, pullRequest]));
    $("#repository-summary").innerHTML = `
      <div><span>Current branch</span><strong>${esc(repository.currentBranch || "Detached HEAD")}</strong></div>
      <div><span>Default branch</span><strong>${esc(repository.defaultBranch || "Unknown")}</strong></div>
      <div><span>Working tree</span><strong>${repository.dirtyPaths ? `${esc(repository.dirtyPaths)} changed paths` : "Clean"}</strong></div>
      <div><span>PR evidence</span><strong class="${repository.pullRequestSource?.available ? "repository-source-live" : "repository-source-unavailable"}">${esc(repository.pullRequestSource?.available ? "Live" : "Unavailable")}</strong></div>`;

    $("#repository-branch-list").innerHTML = repository.branches?.length ? repository.branches.map((branch) => {
      const pullRequest = pullRequestsByNumber.get(branch.pullRequestNumber);
      const url = externalUrl(pullRequest?.url);
      return `
        <article class="repository-row branch-row ${branch.isCurrent ? "is-current" : ""}">
          <span class="repository-entity-icon">${icon("git-branch")}</span>
          <div class="repository-row-copy">
            <div class="repository-title-line"><strong>${esc(branch.name)}</strong>${branch.isCurrent ? "<em>Current</em>" : ""}${branch.isManaged ? "<em>Meta PDS</em>" : ""}</div>
            <p>${esc(branch.subject || "No commit subject")}</p>
            <small><code>${esc(branch.head)}</code> · ${esc(repositoryTracking(branch))} · Updated ${esc(dateTime(branch.updatedAt))}${pullRequest ? ` · ${url ? `<a href="${esc(url)}" target="_blank" rel="noreferrer">PR #${esc(pullRequest.number)}${icon("external-link")}</a>` : `PR #${esc(pullRequest.number)}`}` : ""}</small>
          </div>
          ${badge(branch.status)}
        </article>`;
    }).join("") : '<div class="empty-state">No local branches were found.</div>';

    if (!repository.pullRequestSource?.available) {
      $("#repository-pr-list").innerHTML = `<div class="repository-unavailable">${icon("triangle-alert")}<strong>Pull-request status unavailable</strong><p>${esc(repository.pullRequestSource?.message || "Install and authenticate GitHub CLI to show PR evidence.")}</p></div>`;
      return;
    }
    $("#repository-pr-list").innerHTML = repository.pullRequests?.length ? repository.pullRequests.map((pullRequest) => {
      const url = externalUrl(pullRequest.url);
      const review = pullRequest.reviewDecision !== "UNKNOWN" ? pretty(pullRequest.reviewDecision) : "No review decision";
      const mergeState = pullRequest.mergeState !== "UNKNOWN" ? pretty(pullRequest.mergeState) : "Merge state unknown";
      return `
        <article class="repository-row pull-request-row">
          <span class="repository-entity-icon">${icon("git-pull-request")}</span>
          <div class="repository-row-copy">
            <div class="repository-title-line">${url ? `<a href="${esc(url)}" target="_blank" rel="noreferrer"><strong>#${esc(pullRequest.number)} · ${esc(pullRequest.title)}</strong>${icon("external-link")}</a>` : `<strong>#${esc(pullRequest.number)} · ${esc(pullRequest.title)}</strong>`}</div>
            <p><code>${esc(pullRequest.headBranch || "Unknown head")}</code> → <code>${esc(pullRequest.baseBranch || "Unknown base")}</code></p>
            <small>${esc(review)} · ${esc(mergeState)} · Updated ${esc(dateTime(pullRequest.updatedAt))}</small>
          </div>
          ${badge(pullRequest.status)}
        </article>`;
    }).join("") : '<div class="empty-state">No pull requests were returned for this repository.</div>';
  }

  let modalSliceId = null;
  let modalTaskId = null;
  let modalContractId = null;
  let modalEntity = "slice";
  let modalTab = "overview";
  let modalReturnFocus = null;

  function inlineMarkdown(value) {
    return esc(value)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  }

  function renderMarkdown(markdown) {
    const lines = String(markdown || "").trim().split("\n");
    const output = [];
    let listOpen = false;
    const closeList = () => {
      if (listOpen) output.push("</ul>");
      listOpen = false;
    };

    lines.forEach((rawLine) => {
      const line = rawLine.trim();
      if (!line) { closeList(); return; }
      const heading = line.match(/^(#{1,4})\s+(.+)$/);
      if (heading) {
        closeList();
        const level = heading[1].length;
        output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
        return;
      }
      const item = line.match(/^[-*]\s+(.+)$/);
      if (item) {
        if (!listOpen) { output.push("<ul>"); listOpen = true; }
        output.push(`<li>${inlineMarkdown(item[1])}</li>`);
        return;
      }
      closeList();
      output.push(`<p>${inlineMarkdown(line)}</p>`);
    });
    closeList();
    return output.join("");
  }

  function sliceIntroMarkdown(slice) {
    return ["## Capability outcome", slice.outcome].join("\n\n");
  }

  function renderModalTabs(slice, visible = true) {
    const tabs = [
      ["overview", "Overview", null],
      ["stories", "User Stories", sliceStories(slice.id).length],
      ["work-packages", "Work Packages", sliceTasks(slice.id).length],
      ["tests", "Test Cases", sliceTests(slice.id).length],
    ];
    $("#modal-tabs").hidden = !visible;
    $("#modal-tabs").innerHTML = visible ? tabs.map(([id, label, count]) => `
      <button class="modal-tab ${modalTab === id ? "is-active" : ""}" type="button" role="tab" data-modal-tab="${id}" aria-selected="${modalTab === id}">
        ${esc(label)}${count === null ? "" : `<span>${count}</span>`}
      </button>`).join("") : "";
  }

  function storyAccordion(story) {
    const criteria = story.acceptanceCriteria || [];
    return `
      <details class="story-accordion-item">
        <summary>
          <span class="story-accordion-dot"><i class="state-dot ${tone(story.status)}"></i></span>
          <span class="story-accordion-copy"><small>${esc(story.id)} · ${esc(statusLabel(story.status))}</small><strong>${esc(story.title)}</strong></span>
          <span class="story-accordion-count">${esc(acceptanceLabel(story))}</span>
          <span class="story-accordion-chevron">${icon("chevron-down")}</span>
        </summary>
        <div class="story-accordion-body">
          ${story.description ? `<p>${esc(story.description)}</p>` : ""}
          <h4>Acceptance criteria</h4>
          <ul>${criteria.length ? criteria.map((criterion) => `<li>${esc(criterion)}</li>`).join("") : "<li>See the canonical slice artifact.</li>"}</ul>
          <div class="linked-test-ids"><strong>Linked tests</strong><span>${story.testIds?.length ? story.testIds.map((id) => `<code>${esc(id)}</code>`).join("") : "No tests linked"}</span></div>
        </div>
      </details>`;
  }

  function testCaseAccordion(test) {
    const linkedStories = (test.supports || [])
      .map((id) => data.stories.find((story) => story.id === id))
      .filter(Boolean);
    return `
      <details class="story-accordion-item test-accordion-item">
        <summary>
          <span class="story-accordion-dot"><i class="state-dot ${tone(test.status)}"></i></span>
          <span class="story-accordion-copy"><small>${esc(test.id)} · ${esc(pretty(test.level))} · ${esc(test.owner)}</small><strong>${esc(test.title)}</strong></span>
          <span class="story-accordion-count">${esc(pretty(test.type))}</span>
          <span class="story-accordion-chevron">${icon("chevron-down")}</span>
        </summary>
        <div class="story-accordion-body test-accordion-body">
          <h4>Expected result</h4>
          <p>${esc(test.expected || "Expected result is not yet defined.")}</p>
          <dl class="test-case-properties">
            <div><dt>Status</dt><dd>${badge(test.status)}</dd></div>
            <div><dt>Level</dt><dd>${esc(pretty(test.level))}</dd></div>
            <div><dt>Method</dt><dd>${esc(pretty(test.type))}</dd></div>
            <div><dt>Owner</dt><dd>${esc(test.owner)}</dd></div>
          </dl>
          <h4>Supports stories</h4>
          <ul>${linkedStories.length ? linkedStories.map((story) => `<li><code>${esc(story.id)}</code> — ${esc(story.title)}</li>`).join("") : "<li>No linked story.</li>"}</ul>
          ${test.validatesContracts?.length ? `<h4>Validates contracts</h4><ul>${test.validatesContracts.map((contract) => `<li>${esc(contract)}</li>`).join("")}</ul>` : ""}
          ${test.command ? `<h4>Executed command</h4><code class="test-command">${esc(test.command)}</code>` : ""}
          ${test.evidence ? `<h4>QA evidence</h4><p>${esc(test.evidence)}</p>` : ""}
        </div>
      </details>`;
  }

  function taskMarkdown(task) {
    const linkedStories = task.storyIds
      .map((id) => data.stories.find((story) => story.id === id))
      .filter(Boolean);
    const markdownList = (heading, values, fallback = "None") => [
      `## ${heading}`,
      ...(values?.length ? values.map((value) => `- ${value}`) : [`- ${fallback}`]),
    ].join("\n");
    return [
      "## Description",
      task.description,
      task.blocker ? `## Current blocker\n${task.blocker}` : "",
      markdownList("Supports stories", linkedStories.map((story) => `${story.id} — ${story.title}`)),
      markdownList("Dependencies", task.dependsOn),
      markdownList("Inputs", task.inputs),
      markdownList("Produces", task.produces),
      markdownList("Owned paths", task.ownedPaths),
      markdownList("Forbidden paths", task.forbiddenPaths),
      markdownList("Entry checks", task.entryChecks),
      markdownList("Exit checks", task.exitChecks),
      markdownList("Required Test IDs", task.requiredTestIds),
      "## Completion evidence",
      `- Required test progress: ${task.tests.passed}/${task.tests.total}`,
      `- Execution wave: ${task.wave || "Unassigned"}`,
      `- Contract version: ${task.contractVersion || "Unspecified"}`,
      `- Integration owner: ${task.integrationOwner || "Unassigned"}`,
      `- Preserve the parent slice's locked contracts and assigned ${pretty(task.area)} boundary.`,
      "- Record changed paths, local commit, CLI test evidence, risks, and remaining work before handoff."
    ].filter(Boolean).join("\n\n");
  }

  function propertyRow(label, value) {
    return `<div class="property-row"><span>${esc(label)}</span><strong>${value}</strong></div>`;
  }

  function contractLink(contract) {
    return `
      <button class="property-contract" type="button" data-open-contract="${esc(contract.id)}">
        <span><small>${esc(contract.id)} · ${esc(contract.version)}</small><strong>${esc(contract.name)}</strong></span>
        ${icon("chevron-right")}
      </button>`;
  }

  function sliceProperties(slice) {
    const contracts = sliceContracts(slice.id);
    return `
      <aside class="issue-properties">
        <section><h3>Properties</h3>
          ${propertyRow("Status", badge(slice.status))}
          ${propertyRow("Priority", esc(slice.priority))}
          ${propertyRow("Revision", `r${esc(slice.revision)}`)}
          ${propertyRow("Progress", progressDisplay(slice.progress, slice.status, `${slice.title} completion`, "property-progress"))}
        </section>
        <section><h3>Dependencies</h3>
          ${propertyRow("Upstream", esc(slice.dependencies.join(", ") || "None"))}
        </section>
        <section><h3>Contracts</h3>
          <div class="property-contract-list">${contracts.length ? contracts.map(contractLink).join("") : '<div class="property-empty">No contracts recorded.</div>'}</div>
        </section>
        <section><h3>Source</h3><code class="property-code">${esc(slice.artifactPath || `docs/meta-pds/slices/${slice.id}.md`)}</code></section>
      </aside>`;
  }

  function workPackageAccordion(task) {
    return `
      <details class="story-accordion-item work-package-accordion-item">
        <summary>
          <span class="story-accordion-dot"><i class="state-dot ${tone(task.status)}"></i></span>
          <span class="story-accordion-copy"><small>${esc(task.id)} · ${esc(pretty(task.area))}</small><button class="work-package-title-link" type="button" data-open-task="${esc(task.id)}" aria-label="Open full detail for ${esc(task.title)}">${esc(task.title)}</button></span>
          <span class="story-accordion-count">${esc(task.owner)}</span>
          ${badge(task.status)}
          <span class="story-accordion-chevron">${icon("chevron-down")}</span>
        </summary>
        <div class="story-accordion-body work-package-accordion-body">
          <div class="markdown-body work-package-markdown">${renderMarkdown(taskMarkdown(task))}</div>
        </div>
      </details>`;
  }

  function sliceIssueDetail(slice) {
    const tasks = sliceTasks(slice.id);
    const stories = sliceStories(slice.id);
    const tests = sliceTests(slice.id);
    const panes = {
      overview: `
        <section class="issue-section tab-pane">
          <header><h3>Description</h3><span>Markdown</span></header>
          <div class="markdown-body">${renderMarkdown(sliceIntroMarkdown(slice))}</div>
        </section>`,
      stories: `
        <section class="story-accordion tab-pane">
          <header><div><h2>User stories and acceptance</h2><span>${stories.length} stories</span></div><span>Click a story to expand</span></header>
          <div class="story-accordion-list">${stories.length ? stories.map(storyAccordion).join("") : '<div class="empty-state">No stories are defined.</div>'}</div>
        </section>`,
      "work-packages": `
        <section class="story-accordion tab-pane work-package-tab">
          <header><div><h2>Development work packages</h2><span>${tasks.length} assigned packages</span></div><span>Click a package to expand</span></header>
          <div class="story-accordion-list">${tasks.length ? tasks.map(workPackageAccordion).join("") : '<div class="empty-state"><strong>Not mobilized yet</strong><p>Work packages are created, sequenced, and assigned when Slice Development starts.</p></div>'}</div>
        </section>`,
      tests: `
        <section class="story-accordion test-accordion tab-pane">
          <header><div><h2>Test cases</h2><span>${tests.length} slice-owned test cases</span></div><span>Click a test to expand</span></header>
          <div class="story-accordion-list">${tests.length ? tests.map(testCaseAccordion).join("") : '<div class="empty-state">No test cases are defined in this slice.</div>'}</div>
        </section>`,
    };
    return `
      <div class="issue-layout">
        <div class="issue-main">
          ${panes[modalTab] || panes.overview}
        </div>
        ${sliceProperties(slice)}
      </div>`;
  }

  function taskProperties(task, slice) {
    return `
      <aside class="issue-properties">
        <section><h3>Properties</h3>
          ${propertyRow("Status", badge(task.status))}
          ${propertyRow("Assignee", esc(task.owner))}
          ${propertyRow("Code area", esc(pretty(task.area)))}
          ${propertyRow("Wave", esc(task.wave || "Unassigned"))}
          ${propertyRow("Contract", esc(task.contractVersion || "Unspecified"))}
          ${propertyRow("Integration owner", esc(task.integrationOwner || "Unassigned"))}
          ${propertyRow("Critical path", task.critical ? "Yes" : "No")}
          ${propertyRow("Tests", `${task.tests.passed}/${task.tests.total}`)}
        </section>
        <section><h3>Hierarchy</h3>
          ${propertyRow("Parent slice", esc(slice.id))}
          ${propertyRow("User stories", esc(task.storyIds.join(", ")))}
          ${propertyRow("Depends on", esc(task.dependsOn.join(", ") || "None"))}
        </section>
      </aside>`;
  }

  function taskIssueDetail(task, slice) {
    const stories = task.storyIds.map((id) => data.stories.find((story) => story.id === id)).filter(Boolean);
    return `
      <div class="issue-layout">
        <div class="issue-main">
          <section class="issue-section">
            <header><h3>Description</h3><span>Markdown</span></header>
            <div class="markdown-body">${renderMarkdown(taskMarkdown(task))}</div>
          </section>
          <section class="issue-section linked-section">
            <header><h3>Linked user stories</h3><span>${stories.length}</span></header>
            ${stories.map((story) => `<article class="linked-story"><div><small>${esc(story.id)}</small><strong>${esc(story.title)}</strong></div><span>${esc(acceptanceLabel(story))}</span>${badge(story.status)}</article>`).join("")}
          </section>
        </div>
        ${taskProperties(task, slice)}
      </div>`;
  }

  function contractMarkdown(contract) {
    if (contract.markdown) return contract.markdown;
    return [
      "## Required behavior",
      contract.description || "No detailed contract behavior has been recorded yet.",
      contract.path ? `## Canonical source\n\`${contract.path}\`` : "",
    ].filter(Boolean).join("\n\n");
  }

  function contractProperties(contract, slice) {
    return `
      <aside class="issue-properties">
        <section><h3>Properties</h3>
          ${propertyRow("Status", badge(contract.status))}
          ${propertyRow("Version", esc(contract.version))}
          ${propertyRow("Type", esc(pretty(contract.type)))}
          ${propertyRow("Owner", esc(contract.owner))}
        </section>
        <section><h3>Hierarchy</h3>
          ${propertyRow("Parent slice", esc(slice.id))}
        </section>
        <section><h3>Source</h3><code class="property-code">${esc(contract.path || slice.artifactPath || `docs/meta-pds/slices/${slice.id}.md`)}</code></section>
      </aside>`;
  }

  function contractIssueDetail(contract, slice) {
    return `
      <div class="issue-layout">
        <div class="issue-main">
          <section class="issue-section">
            <header><h3>Contract detail</h3><span>Markdown</span></header>
            <div class="markdown-body contract-markdown">${renderMarkdown(contractMarkdown(contract))}</div>
          </section>
        </div>
        ${contractProperties(contract, slice)}
      </div>`;
  }

  function renderModal() {
    const slice = data.slices.find((item) => item.id === modalSliceId);
    if (!slice) return;
    const task = modalEntity === "task" ? data.workPackages.find((item) => item.id === modalTaskId) : null;
    const contract = modalEntity === "contract" ? data.contracts.find((item) => item.id === modalContractId && item.sliceId === slice.id) : null;
    if (task) {
      renderModalTabs(slice, false);
      $("#modal-entity-icon").innerHTML = icon("package");
      setText("#modal-id", `${pretty(task.area)} · ${task.owner || "Unassigned"}`);
      setText("#modal-title", task.title);
      $("#modal-breadcrumbs").innerHTML = `<button type="button" data-modal-root>Slices</button>${icon("chevron-right", "breadcrumb-icon")}<button type="button" data-modal-slice>${esc(slice.id)}</button>${icon("chevron-right", "breadcrumb-icon")}<strong>${esc(task.id)}</strong>`;
      $("#modal-content").innerHTML = taskIssueDetail(task, slice);
    } else if (contract) {
      renderModalTabs(slice, false);
      $("#modal-entity-icon").innerHTML = icon("git-branch");
      setText("#modal-id", `${contract.version} · ${pretty(contract.type)}`);
      setText("#modal-title", contract.name);
      $("#modal-breadcrumbs").innerHTML = `<button type="button" data-modal-root>Slices</button>${icon("chevron-right", "breadcrumb-icon")}<button type="button" data-modal-slice>${esc(slice.id)}</button>${icon("chevron-right", "breadcrumb-icon")}<strong>${esc(contract.id)}</strong>`;
      $("#modal-content").innerHTML = contractIssueDetail(contract, slice);
    } else {
      modalEntity = "slice";
      modalTaskId = null;
      modalContractId = null;
      renderModalTabs(slice, true);
      $("#modal-entity-icon").innerHTML = icon("layers");
      setText("#modal-id", `${slice.priority} priority · Revision ${slice.revision}`);
      setText("#modal-title", slice.title);
      $("#modal-breadcrumbs").innerHTML = `<button type="button" data-modal-root>Slices</button>${icon("chevron-right", "breadcrumb-icon")}<strong>${esc(slice.id)}</strong>`;
      $("#modal-content").innerHTML = sliceIssueDetail(slice);
    }
    $("#modal-content").scrollTop = 0;
  }

  function openModal(sliceId) {
    modalSliceId = sliceId;
    modalTaskId = null;
    modalContractId = null;
    modalEntity = "slice";
    modalTab = "overview";
    modalReturnFocus = document.activeElement;
    renderModal();
    $("#slice-modal").classList.add("is-open");
    $("#slice-modal").setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-open");
    $("#modal-close").focus();
  }

  function closeModal() {
    $("#slice-modal").classList.remove("is-open");
    $("#slice-modal").setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-open");
    if (modalReturnFocus) modalReturnFocus.focus();
  }

  function bindModal() {
    $("#modal-close").addEventListener("click", closeModal);
    $("#slice-modal").addEventListener("click", (event) => { if (event.target === $("#slice-modal")) closeModal(); });
    $("#slice-modal").addEventListener("click", (event) => {
      const task = event.target.closest("[data-open-task]");
      if (task) { event.preventDefault(); modalTaskId = task.dataset.openTask; modalContractId = null; modalEntity = "task"; renderModal(); return; }
      const contract = event.target.closest("[data-open-contract]");
      if (contract) { modalContractId = contract.dataset.openContract; modalTaskId = null; modalEntity = "contract"; renderModal(); return; }
      const tab = event.target.closest("[data-modal-tab]");
      if (tab) { modalTab = tab.dataset.modalTab; modalTaskId = null; modalContractId = null; modalEntity = "slice"; renderModal(); return; }
      if (event.target.closest("[data-modal-slice]")) { modalTaskId = null; modalContractId = null; modalEntity = "slice"; renderModal(); return; }
      if (event.target.closest("[data-modal-root]")) closeModal();
    });
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && $("#slice-modal").classList.contains("is-open")) closeModal(); });
  }

  renderHeader();
  renderDataHealth();
  renderSlices();
  renderDecisions();
  renderPrototype();
  renderActivity();
  renderRepository();
  bindTopTabs();
  bindSliceList();
  bindDecisionControls();
  bindModal();
})();
