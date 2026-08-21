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
  let modalView = "overview";
  let modalReturnFocus = null;

  function modalOverview(slice) {
    const stories = sliceStories(slice.id);
    const tasks = sliceTasks(slice.id);
    const contracts = sliceContracts(slice.id);
    const tests = sliceTests(slice.id);
    const activeAgents = [...new Set(tasks.filter((task) => task.status !== "DONE").map((task) => task.owner))];
    const blockers = tasks.filter((task) => task.status === "BLOCKED");
    return `
      <div class="modal-grid">
        <div>
          <section class="detail-card"><header class="detail-card-header"><h3>Capability outcome</h3></header><div class="detail-card-body"><p class="outcome-text">${esc(slice.outcome)}</p></div></section>
          <section class="detail-card"><header class="detail-card-header"><h3>Current development work</h3><span class="simple-code">${tasks.length} packages</span></header>
            ${tasks.length ? `<table class="detail-table"><thead><tr><th>Task</th><th>Area</th><th>Assignee</th><th>Dependencies</th><th>Status</th></tr></thead><tbody>${tasks.map((task) => `<tr><td><strong>${esc(task.id)} · ${esc(task.title)}</strong><small>${esc(task.description)}</small></td><td>${esc(pretty(task.area))}</td><td>${esc(task.owner)}</td><td>${esc(task.dependsOn.join(", ") || "None")}</td><td>${badge(task.status)}</td></tr>`).join("")}</tbody></table>` : '<div class="empty-state">Execution has not been mobilized.</div>'}
          </section>
        </div>
        <aside>
          <section class="detail-card"><header class="detail-card-header"><h3>Slice state</h3></header><div class="detail-card-body detail-rows">
            <div class="detail-row"><span>State</span><span>${esc(pretty(slice.status))}</span></div>
            <div class="detail-row"><span>Priority / revision</span><span>${esc(slice.priority)} / r${esc(slice.revision)}</span></div>
            <div class="detail-row"><span>Dependencies</span><span>${esc(slice.dependencies.join(", ") || "None")}</span></div>
            <div class="detail-row"><span>Progress</span><span>${esc(slice.progress)}%</span></div>
            <div class="detail-row"><span>Stories</span><span>${stories.length}</span></div>
            <div class="detail-row"><span>Contracts</span><span>${contracts.length}</span></div>
            <div class="detail-row"><span>Test cases</span><span>${tests.length}</span></div>
          </div></section>
          <section class="detail-card"><header class="detail-card-header"><h3>Active agents</h3></header><div class="detail-card-body">${activeAgents.length ? activeAgents.map((agent) => `<div class="detail-row"><span>Assigned</span><span>${esc(agent)}</span></div>`).join("") : '<p class="simple-code">No agent currently assigned.</p>'}</div></section>
          ${blockers.length ? `<section class="detail-card"><header class="detail-card-header"><h3>Blockers</h3>${badge("BLOCKED")}</header><div class="detail-card-body">${blockers.map((task) => `<div class="detail-row"><span>${esc(task.id)}</span><span>${esc(task.blocker || "Blocked")}</span></div>`).join("")}</div></section>` : ""}
        </aside>
      </div>`;
  }

  function modalStories(slice) {
    const stories = sliceStories(slice.id);
    if (!stories.length) return '<div class="empty-state">No user stories have been defined.</div>';
    return `<section class="detail-card"><table class="detail-table"><thead><tr><th>Story</th><th>Acceptance criteria</th><th>Packages</th><th>Evidence</th><th>Status</th></tr></thead><tbody>${stories.map((story) => `
      <tr>
        <td><strong>${esc(story.id)} · ${esc(story.title)}</strong><small>${story.acceptance.passed}/${story.acceptance.total} accepted</small></td>
        <td><ul class="acceptance-list">${(story.acceptanceCriteria || []).map((criterion) => `<li>${esc(criterion)}</li>`).join("") || "<li>Criteria are recorded in the canonical slice artifact.</li>"}</ul></td>
        <td><span class="mini-packages">${story.workPackageIds.map((id) => `<i class="mini-package">${esc(id)}</i>`).join("")}</span></td>
        <td>${percent(story.acceptance.passed, story.acceptance.total)}%</td>
        <td>${badge(story.status)}</td>
      </tr>`).join("")}</tbody></table></section>`;
  }

  function modalTasks(slice) {
    const tasks = sliceTasks(slice.id);
    if (!tasks.length) return '<div class="empty-state">Development work has not been mobilized.</div>';
    return `<section class="detail-card"><table class="detail-table"><thead><tr><th>Work package</th><th>Code area</th><th>Assignee</th><th>Stories</th><th>Dependencies</th><th>Tests</th><th>Status</th></tr></thead><tbody>${tasks.map((task) => `
      <tr>
        <td><strong>${esc(task.id)} · ${esc(task.title)}</strong><small>${esc(task.blocker || task.description)}</small></td>
        <td>${esc(pretty(task.area))}</td><td>${esc(task.owner)}</td><td>${esc(task.storyIds.join(", "))}</td><td>${esc(task.dependsOn.join(", ") || "None")}</td>
        <td>${task.tests.passed}/${task.tests.total}</td><td>${badge(task.status)}</td>
      </tr>`).join("")}</tbody></table></section>`;
  }

  function modalEvidence(slice) {
    const contracts = sliceContracts(slice.id);
    const tests = sliceTests(slice.id);
    return `<div class="modal-grid"><div>
      <section class="detail-card"><header class="detail-card-header"><h3>Contracts</h3><span class="simple-code">${contracts.length} records</span></header>
        ${contracts.length ? contracts.map((contract) => `<article class="contract-card"><span>${esc(contract.id)} · ${esc(contract.version)}</span><div><h3>${esc(contract.name)}</h3><p>${esc(contract.type)} · Owner: ${esc(contract.owner)} · ${esc(contract.path)}</p></div>${badge(contract.status)}</article>`).join("") : '<div class="empty-state">No contracts recorded.</div>'}
      </section></div><div>
      <section class="detail-card"><header class="detail-card-header"><h3>Test cases and evidence</h3><span class="simple-code">${tests.length} cases</span></header>
        ${tests.length ? tests.map((test) => `<article class="contract-card"><span>${esc(test.id)}</span><div><h3>${esc(test.title)}</h3><p>${esc(test.type)} · ${esc(test.owner)} · ${esc(test.evidence)}</p></div>${badge(test.status)}</article>`).join("") : '<div class="empty-state">Test cases have not been mapped.</div>'}
      </section></div></div>`;
  }

  function renderModal() {
    const slice = data.slices.find((item) => item.id === modalSliceId);
    if (!slice) return;
    setText("#modal-id", `${slice.id} · ${slice.priority} · revision ${slice.revision}`);
    setText("#modal-title", slice.title);
    $("#modal-state").innerHTML = `<span class="state-dot ${tone(slice.status)}"></span>`;
    $$(".modal-tab").forEach((tab) => tab.classList.toggle("is-active", tab.dataset.modalView === modalView));
    const renderers = { overview: modalOverview, stories: modalStories, tasks: modalTasks, evidence: modalEvidence };
    $("#modal-content").innerHTML = renderers[modalView](slice);
  }

  function openModal(sliceId) {
    modalSliceId = sliceId;
    modalView = "overview";
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
    $$(".modal-tab").forEach((tab) => tab.addEventListener("click", () => { modalView = tab.dataset.modalView; renderModal(); }));
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
