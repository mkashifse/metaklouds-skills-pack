(function () {
  "use strict";

  const data = window.META_PDS_DASHBOARD_DATA;
  if (!data) {
    document.body.innerHTML = "<main class='empty-state'>Dashboard data is unavailable.</main>";
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
  const percent = (passed, total) => total ? Math.round((passed / total) * 100) : 0;
  const time = (value) => new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(new Date(value));
  const dateTime = (value) => new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
  const setText = (selector, value) => { const node = $(selector); if (node) node.textContent = value; };

  function tone(status) {
    if (["RELEASED", "OUTCOME_VALIDATED", "DONE", "LOCKED", "PASSED"].includes(status)) return "released";
    if (["IN_PROGRESS", "VERIFYING", "HUMAN_REVIEW", "TESTING"].includes(status)) return "active";
    if (["BLOCKED", "REWORK_REQUIRED", "REVERIFY_REQUIRED", "FAILED"].includes(status)) return "blocked";
    if (["READY", "READY_FOR_DEVELOPMENT", "EXECUTION_READY", "RELEASE_READY"].includes(status)) return "ready";
    return "draft";
  }

  function badge(status, label = pretty(status)) {
    return `<span class="state-badge ${tone(status)}">${esc(label)}</span>`;
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

  function taskTests(tasks) {
    return tasks.reduce((result, task) => ({
      passed: result.passed + task.tests.passed,
      total: result.total + task.tests.total
    }), { passed: 0, total: 0 });
  }

  function storyProgress(stories) {
    const totals = stories.reduce((result, story) => ({
      passed: result.passed + story.acceptance.passed,
      total: result.total + story.acceptance.total
    }), { passed: 0, total: 0 });
    return { ...totals, percent: percent(totals.passed, totals.total) };
  }

  function renderHeader() {
    const initiative = data.initiative;
    setText("#initiative-name", initiative.name);
    setText("#initiative-id", initiative.id);
    setText("#initiative-phase", pretty(initiative.phase));
    setText("#initiative-health", pretty(initiative.health));
    setText("#updated-at", `Updated ${dateTime(data.projection.generatedAt)}`);
    setText("#slice-count", data.slices.length);
    setText("#decision-count", data.decisions.length);
    setText("#next-action", initiative.nextAction.title);
    setText("#next-action-detail", initiative.nextAction.detail);
    setText("#next-action-owner", initiative.nextAction.owner);
    setText("#projection-source", `${data.projection.source} · schema v${data.schemaVersion}`);
  }

  let currentView = "slices";
  function showView(view) {
    currentView = view;
    $$(".top-tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.view === view));
    $$(".view-panel").forEach((panel) => panel.classList.toggle("is-active", panel.dataset.panel === view));
    if (history.replaceState) history.replaceState(null, "", `#${view}`);
  }

  function bindTopTabs() {
    $$(".top-tab").forEach((tab) => tab.addEventListener("click", () => showView(tab.dataset.view)));
    const requested = location.hash.slice(1);
    showView(["slices", "decisions", "prototype", "activity"].includes(requested) ? requested : "slices");
  }

  let sliceFilter = "ALL";
  const expandedSlices = new Set(data.slices.filter((slice) => slice.active).map((slice) => slice.id));

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
        <div class="active-work-label"><span>${tasks.some((task) => task.status !== "DONE") ? "Current development work" : "Recently completed work"}</span><span>${visible.length} shown</span></div>
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

  function storyDrawer(slice) {
    const stories = sliceStories(slice.id);
    if (!stories.length) return `<div class="story-drawer"><div class="empty-state">Stories have not been defined for this slice.</div></div>`;
    return `
      <div class="story-drawer">
        <div class="story-table">
          <div class="story-row header"><span>ID</span><span>User story</span><span>Acceptance</span><span>Work packages</span><span>State</span></div>
          ${stories.map((story) => `
            <div class="story-row">
              <span class="task-id">${esc(story.id)}</span>
              <span class="story-name"><strong>${esc(story.title)}</strong><span>${esc((story.acceptanceCriteria || []).length)} explicit criteria</span></span>
              <span>${story.acceptance.passed}/${story.acceptance.total} · ${percent(story.acceptance.passed, story.acceptance.total)}%</span>
              <span class="mini-packages">${story.workPackageIds.map((id) => `<i class="mini-package">${esc(id)}</i>`).join("")}</span>
              ${badge(story.status)}
            </div>
          `).join("")}
        </div>
      </div>`;
  }

  function sliceCard(slice) {
    const stories = sliceStories(slice.id);
    const tasks = sliceTasks(slice.id);
    const contracts = sliceContracts(slice.id);
    const tests = taskTests(tasks);
    const acceptance = storyProgress(stories);
    const doneTasks = tasks.filter((task) => task.status === "DONE").length;
    const blockers = tasks.filter((task) => task.status === "BLOCKED");
    const dependencies = slice.dependencies.length ? slice.dependencies.join(", ") : "None";
    const expanded = expandedSlices.has(slice.id);
    const lockedContracts = contracts.filter((contract) => contract.status === "LOCKED").length;

    return `
      <article class="slice-item ${expanded ? "is-expanded" : ""}" data-slice-id="${esc(slice.id)}">
        <div class="slice-main">
          <div>
            <div class="slice-title-row">
              <span class="state-dot ${tone(slice.status)}"></span>
              <span class="slice-code">${String(slice.order).padStart(2, "0")} · ${esc(slice.id)}</span>
              <h2>${esc(slice.title)}</h2>
            </div>
            <p class="slice-outcome"><strong>Outcome:</strong> ${esc(slice.outcome)}</p>
            <div class="slice-meta">
              <span>Priority <strong>${esc(slice.priority)}</strong></span>
              <span>Revision <strong>${esc(slice.revision)}</strong></span>
              <span>Depends on <strong>${esc(dependencies)}</strong></span>
              ${blockers.length ? `<span class="task-blocked">${blockers.length} blocker${blockers.length > 1 ? "s" : ""}</span>` : ""}
            </div>
          </div>
          <div class="slice-side">
            <div class="slice-state-line">${badge(slice.status)}<span class="slice-code">${slice.progress}%</span></div>
            <div class="progress-line"><div class="progress-track"><i style="width:${Number(slice.progress)}%"></i></div><span>${slice.progress}%</span></div>
            <div class="slice-facts">
              <div class="slice-fact"><span>Stories</span><strong>${stories.length}</strong></div>
              <div class="slice-fact"><span>Tasks</span><strong>${doneTasks}/${tasks.length}</strong></div>
              <div class="slice-fact"><span>Tests</span><strong>${tests.passed}/${tests.total}</strong></div>
            </div>
          </div>
        </div>
        ${activeTaskRows(tasks)}
        <div class="slice-actions">
          <div class="slice-actions-left">Acceptance ${acceptance.passed}/${acceptance.total} · Contracts ${lockedContracts}/${contracts.length} locked</div>
          <div class="slice-actions-right">
            <button class="text-button" type="button" data-toggle-slice="${esc(slice.id)}"><span class="chevron">⌄</span>${expanded ? "Hide stories" : "Show stories"}</button>
            <button class="text-button primary" type="button" data-open-slice="${esc(slice.id)}">Open full details</button>
          </div>
        </div>
        ${storyDrawer(slice)}
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
      const toggle = event.target.closest("[data-toggle-slice]");
      if (toggle) {
        const id = toggle.dataset.toggleSlice;
        expandedSlices.has(id) ? expandedSlices.delete(id) : expandedSlices.add(id);
        renderSlices();
        return;
      }
      const open = event.target.closest("[data-open-slice]");
      if (open) openModal(open.dataset.openSlice);
    });
  }

  function renderDecisions() {
    $("#decision-list").innerHTML = data.decisions.map((decision) => `
      <article class="simple-item">
        <span class="simple-code">${esc(decision.id)} · r${esc(decision.revision)}</span>
        <div class="simple-copy"><h3>${esc(decision.title)}</h3><p>${esc(decision.summary)} · Affects ${esc(decision.affects.join(", "))}</p></div>
        ${badge(decision.status)}
      </article>`).join("");
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
    $("#activity-list").innerHTML = data.activity.map((item) => `
      <article class="simple-item">
        <span class="simple-code">${esc(time(item.at))}</span>
        <div class="simple-copy"><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></div>
        <span class="state-badge ${item.kind === "blocked" ? "blocked" : item.kind === "completed" ? "released" : "active"}">${esc(pretty(item.kind))}</span>
      </article>`).join("");
  }

  let modalSliceId = null;
  let modalReturnFocus = null;

  function nestedTask(task) {
    return `
      <article class="nested-task">
        <div class="nested-task-copy">
          <span class="simple-code">${esc(task.id)} · ${esc(pretty(task.area))}</span>
          <h4>${esc(task.title)}</h4>
          <p>${esc(task.blocker || task.description)}</p>
        </div>
        <div class="nested-task-meta">
          <span class="assignee"><i>${esc(task.ownerInitials)}</i>${esc(task.owner)}</span>
          <span>${task.tests.passed}/${task.tests.total} tests</span>
          ${badge(task.status)}
        </div>
      </article>`;
  }

  function storyHierarchy(story) {
    const tasks = story.workPackageIds
      .map((id) => data.workPackages.find((task) => task.id === id))
      .filter(Boolean);
    return `
      <article class="story-detail">
        <header class="story-detail-header">
          <div>
            <span class="simple-code">${esc(story.id)} · ${story.acceptance.passed}/${story.acceptance.total} acceptance checks</span>
            <h3>${esc(story.title)}</h3>
          </div>
          ${badge(story.status)}
        </header>
        <div class="story-detail-body">
          <div class="story-acceptance">
            <h4>Acceptance</h4>
            <ul>${(story.acceptanceCriteria || []).map((criterion) => `<li>${esc(criterion)}</li>`).join("") || "<li>See the canonical slice artifact.</li>"}</ul>
          </div>
          <div class="nested-tasks">
            <div class="nested-heading"><span>Tasks</span><strong>${tasks.length}</strong></div>
            ${tasks.length ? tasks.map(nestedTask).join("") : '<div class="empty-nested">Tasks have not been mobilized.</div>'}
          </div>
        </div>
      </article>`;
  }

  function modalHierarchy(slice) {
    const stories = sliceStories(slice.id);
    const tasks = sliceTasks(slice.id);
    const contracts = sliceContracts(slice.id);
    const tests = sliceTests(slice.id);
    const blockers = tasks.filter((task) => task.status === "BLOCKED");
    const activeAgents = [...new Set(tasks.filter((task) => task.status !== "DONE").map((task) => task.owner))];
    const passedTests = tests.filter((test) => test.status === "PASSED").length;

    return `
      <div class="slice-detail-stack">
        <section class="slice-detail-overview">
          <div class="slice-outcome-block">
            <span class="section-kicker">Slice detail</span>
            <h3>Capability outcome</h3>
            <p>${esc(slice.outcome)}</p>
          </div>
          <div class="slice-detail-facts">
            <div><span>State</span><strong>${esc(pretty(slice.status))}</strong></div>
            <div><span>Progress</span><strong>${esc(slice.progress)}%</strong></div>
            <div><span>Dependencies</span><strong>${esc(slice.dependencies.join(", ") || "None")}</strong></div>
            <div><span>Active agents</span><strong>${activeAgents.length}</strong></div>
            <div><span>Contracts</span><strong>${contracts.length}</strong></div>
            <div><span>Test cases</span><strong>${passedTests}/${tests.length} passed</strong></div>
          </div>
        </section>

        ${blockers.length ? `<section class="slice-blockers"><div>${badge("BLOCKED")}<strong>${blockers.length} blocked task${blockers.length > 1 ? "s" : ""}</strong></div><span>${esc(blockers.map((task) => `${task.id}: ${task.blocker || "Blocked"}`).join(" · "))}</span></section>` : ""}

        <section class="hierarchy-section">
          <header class="hierarchy-title">
            <div><span class="section-kicker">Delivery hierarchy</span><h2>User stories</h2></div>
            <span>${stories.length} stories · ${tasks.length} work packages</span>
          </header>
          <div class="story-hierarchy">
            ${stories.length ? stories.map(storyHierarchy).join("") : '<div class="empty-state">User stories have not been defined for this slice.</div>'}
          </div>
        </section>

        <section class="slice-evidence">
          <div class="evidence-column">
            <header><h3>Slice contracts</h3><span>${contracts.length}</span></header>
            ${contracts.length ? contracts.map((contract) => `<article><div><span class="simple-code">${esc(contract.id)} · ${esc(contract.version)}</span><strong>${esc(contract.name)}</strong><small>${esc(contract.type)} · ${esc(contract.owner)}</small></div>${badge(contract.status)}</article>`).join("") : '<div class="empty-nested">No contracts recorded.</div>'}
          </div>
          <div class="evidence-column">
            <header><h3>Test evidence</h3><span>${tests.length}</span></header>
            ${tests.length ? tests.map((test) => `<article><div><span class="simple-code">${esc(test.id)} · ${esc(test.type)}</span><strong>${esc(test.title)}</strong><small>${esc(test.owner)} · ${esc(test.evidence)}</small></div>${badge(test.status)}</article>`).join("") : '<div class="empty-nested">No test cases mapped.</div>'}
          </div>
        </section>
      </div>`;
  }

  function renderModal() {
    const slice = data.slices.find((item) => item.id === modalSliceId);
    if (!slice) return;
    setText("#modal-id", `${slice.id} · ${slice.priority} · revision ${slice.revision}`);
    setText("#modal-title", slice.title);
    $("#modal-state").innerHTML = `<span class="state-dot ${tone(slice.status)}"></span>`;
    $("#modal-content").innerHTML = modalHierarchy(slice);
  }

  function openModal(sliceId) {
    modalSliceId = sliceId;
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
    document.addEventListener("keydown", (event) => { if (event.key === "Escape" && $("#slice-modal").classList.contains("is-open")) closeModal(); });
  }

  renderHeader();
  renderSlices();
  renderDecisions();
  renderPrototype();
  renderActivity();
  bindTopTabs();
  bindSliceList();
  bindModal();
})();
