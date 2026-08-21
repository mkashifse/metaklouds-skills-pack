(async function () {
  "use strict";

  const safeError = (value) => String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
  let data;
  try {
    if (location.protocol === "file:") throw new Error("Launch the Meta PDS dashboard service from the product root; direct file access cannot read canonical artifacts.");
    const response = await fetch("/api/dashboard", { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Canonical artifact parsing failed.");
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
  const dateTime = (value) => new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));
  const setText = (selector, value) => { const node = $(selector); if (node) node.textContent = value; };
  const icon = (name, className = "") => `<svg class="lucide-icon ${esc(className)}" aria-hidden="true" focusable="false"><use href="#icon-${esc(name)}"></use></svg>`;

  function tone(status) {
    if (["RELEASED", "OUTCOME_VALIDATED", "DONE", "LOCKED", "PASSED", "ON_TRACK"].includes(status)) return "released";
    if (["IN_PROGRESS", "VERIFYING", "HUMAN_REVIEW", "TESTING"].includes(status)) return "active";
    if (["BLOCKED", "REWORK_REQUIRED", "REVERIFY_REQUIRED", "FAILED", "AT_RISK", "OFF_TRACK"].includes(status)) return "blocked";
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
    return stories.reduce((result, story) => ({
      verified: result.verified + (story.acceptance.evidenceStatus === "VERIFIED" ? 1 : 0),
      stories: result.stories + 1,
      criteria: result.criteria + story.acceptance.total
    }), { verified: 0, stories: 0, criteria: 0 });
  }

  function acceptanceLabel(story) {
    if (story.acceptance.evidenceStatus === "VERIFIED") return `${story.acceptance.total}/${story.acceptance.total} verified`;
    return `${story.acceptance.total} criteria`;
  }

  function renderHeader() {
    const initiative = data.initiative;
    setText("#initiative-name", initiative.name);
    setText("#initiative-id", initiative.id);
    setText("#initiative-phase", pretty(initiative.phase));
    setText("#initiative-health", pretty(initiative.health));
    $("#initiative-health").className = `state-badge ${tone(initiative.health)}`;
    setText("#updated-at", `Updated ${dateTime(data.projection.generatedAt)}`);
    setText("#source-kind", data.projection.kind === "live-canonical" ? "Live files" : "Example files");
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
              <span>${esc(acceptanceLabel(story))}</span>
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
          <div class="slice-actions-left">Acceptance ${acceptance.criteria} criteria · ${acceptance.verified}/${acceptance.stories} stories verified · Contracts ${lockedContracts}/${contracts.length} locked</div>
          <div class="slice-actions-right">
            <button class="text-button" type="button" data-toggle-slice="${esc(slice.id)}"><span class="chevron">${icon("chevron-down")}</span>${expanded ? "Hide stories" : "Show stories"}</button>
            <button class="text-button primary" type="button" data-open-slice="${esc(slice.id)}">${icon("external-link", "button-icon")}Open full details</button>
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
    $("#decision-list").innerHTML = data.decisions.length ? data.decisions.map((decision) => `
      <article class="simple-item">
        <span class="simple-code">${esc(decision.id)} · r${esc(decision.revision)}</span>
        <div class="simple-copy"><h3>${esc(decision.title)}</h3><p>${esc(decision.summary)} · Affects ${esc(decision.affects.join(", "))}</p></div>
        ${badge(decision.status)}
      </article>`).join("") : '<div class="empty-state">No decisions are recorded.</div>';
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
    $("#activity-list").innerHTML = data.activity.length ? data.activity.map((item) => `
      <article class="simple-item">
        <span class="simple-code">${esc(time(item.at))}</span>
        <div class="simple-copy"><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></div>
        <span class="state-badge ${item.kind === "blocked" ? "blocked" : item.kind === "completed" ? "released" : "active"}">${esc(pretty(item.kind))}</span>
      </article>`).join("") : '<div class="empty-state">No durable delivery events are recorded.</div>';
  }

  let modalSliceId = null;
  let modalTaskId = null;
  let modalEntity = "slice";
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
      const heading = line.match(/^(#{2,4})\s+(.+)$/);
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

  function sliceEvidenceMarkdown(slice) {
    const contracts = sliceContracts(slice.id);
    const tests = sliceTests(slice.id);
    return [
      "## Dependencies",
      `- Upstream slices: ${slice.dependencies.join(", ") || "None"}`,
      `- Source artifact: \`${slice.artifactPath || `docs/meta-pds/slices/${slice.id}.md`}\``,
      "## Contracts",
      ...(contracts.length ? contracts.map((contract) => `- **${contract.id}** — ${contract.name} · ${contract.version} · ${pretty(contract.status)}`) : ["- No contracts recorded."]),
      "## Test cases",
      ...(tests.length ? tests.map((test) => `- **${test.id}** — ${test.title} · ${test.type} · ${pretty(test.status)}`) : ["- No test cases recorded."])
    ].join("\n\n");
  }

  function storyAccordion(story) {
    const criteria = story.acceptanceCriteria || [];
    return `
      <details class="story-accordion-item">
        <summary>
          <span class="story-accordion-dot"><i class="state-dot ${tone(story.status)}"></i></span>
          <span class="story-accordion-copy"><small>${esc(story.id)} · ${esc(pretty(story.status))}</small><strong>${esc(story.title)}</strong></span>
          <span class="story-accordion-count">${esc(acceptanceLabel(story))}</span>
          <span class="story-accordion-chevron">${icon("chevron-down")}</span>
        </summary>
        <div class="story-accordion-body">
          ${story.description ? `<p>${esc(story.description)}</p>` : ""}
          <h4>Acceptance criteria</h4>
          <ul>${criteria.length ? criteria.map((criterion) => `<li>${esc(criterion)}</li>`).join("") : "<li>See the canonical slice artifact.</li>"}</ul>
        </div>
      </details>`;
  }

  function taskMarkdown(task) {
    const linkedStories = task.storyIds
      .map((id) => data.stories.find((story) => story.id === id))
      .filter(Boolean);
    return [
      "## Description",
      task.description,
      task.blocker ? `## Current blocker\n${task.blocker}` : "",
      "## Supports",
      ...linkedStories.map((story) => `- ${story.id} — ${story.title}`),
      "## Dependencies",
      ...(task.dependsOn.length ? task.dependsOn.map((id) => `- ${id}`) : ["- None"]),
      "## Completion evidence",
      `- Required test progress: ${task.tests.passed}/${task.tests.total}`,
      `- Preserve the parent slice's locked contracts and assigned ${pretty(task.area)} boundary.`,
      "- Record changed paths, local commit, CLI test evidence, risks, and remaining work before handoff."
    ].filter(Boolean).join("\n\n");
  }

  function propertyRow(label, value) {
    return `<div class="property-row"><span>${esc(label)}</span><strong>${value}</strong></div>`;
  }

  function sliceProperties(slice) {
    const stories = sliceStories(slice.id);
    const tasks = sliceTasks(slice.id);
    const contracts = sliceContracts(slice.id);
    const tests = sliceTests(slice.id);
    const activeAgents = [...new Set(tasks.filter((task) => task.status !== "DONE").map((task) => task.owner))];
    return `
      <aside class="issue-properties">
        <section><h3>Properties</h3>
          ${propertyRow("Status", badge(slice.status))}
          ${propertyRow("Priority", esc(slice.priority))}
          ${propertyRow("Revision", `r${esc(slice.revision)}`)}
          ${propertyRow("Progress", `${esc(slice.progress)}%`)}
          ${propertyRow("Dependencies", esc(slice.dependencies.join(", ") || "None"))}
        </section>
        <section><h3>Delivery</h3>
          ${propertyRow("Stories", stories.length)}
          ${propertyRow("Tasks", tasks.length)}
          ${propertyRow("Active agents", activeAgents.length)}
          ${propertyRow("Contracts", contracts.length)}
          ${propertyRow("Test cases", tests.length)}
        </section>
        <section><h3>Source</h3><code class="property-code">${esc(slice.artifactPath || `docs/meta-pds/slices/${slice.id}.md`)}</code></section>
      </aside>`;
  }

  function childTask(task) {
    return `
      <button class="child-task" type="button" data-open-task="${esc(task.id)}">
        <span class="child-task-status"><i class="state-dot ${tone(task.status)}"></i></span>
        <span class="child-task-copy"><small>${esc(task.id)} · ${esc(pretty(task.area))}</small><strong>${esc(task.title)}</strong></span>
        <span class="child-task-owner"><i>${esc(task.ownerInitials)}</i>${esc(task.owner)}</span>
        <span class="child-task-tests">${task.tests.passed}/${task.tests.total} tests</span>
        ${badge(task.status)}
        <span class="child-task-arrow">${icon("chevron-right")}</span>
      </button>`;
  }

  function sliceIssueDetail(slice) {
    const tasks = sliceTasks(slice.id);
    const stories = sliceStories(slice.id);
    return `
      <div class="issue-layout">
        <div class="issue-main">
          <section class="issue-section">
            <header><h3>Description</h3><span>Markdown</span></header>
            <div class="markdown-body">${renderMarkdown(sliceIntroMarkdown(slice))}</div>
            <section class="story-accordion">
              <header><div><h2>User stories and acceptance</h2><span>${stories.length} stories</span></div><span>Click a story to expand</span></header>
              <div class="story-accordion-list">${stories.length ? stories.map(storyAccordion).join("") : '<div class="empty-state">No stories are defined.</div>'}</div>
            </section>
            <div class="markdown-body supporting-markdown">${renderMarkdown(sliceEvidenceMarkdown(slice))}</div>
          </section>
          <section class="issue-section child-section">
            <header><h3>Tasks</h3><span>${tasks.length}</span></header>
            <div class="child-task-list">${tasks.length ? tasks.map(childTask).join("") : '<div class="empty-state">No tasks have been mobilized.</div>'}</div>
          </section>
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

  function renderModal() {
    const slice = data.slices.find((item) => item.id === modalSliceId);
    if (!slice) return;
    const task = modalEntity === "task" ? data.workPackages.find((item) => item.id === modalTaskId) : null;
    if (task) {
      setText("#modal-id", `${task.id} · ${pretty(task.area)}`);
      setText("#modal-title", task.title);
      $("#modal-state").innerHTML = `<span class="state-dot ${tone(task.status)}"></span>`;
      $("#modal-breadcrumbs").innerHTML = `<button type="button" data-modal-root>Slices</button>${icon("chevron-right", "breadcrumb-icon")}<button type="button" data-modal-slice>${esc(slice.title)}</button>${icon("chevron-right", "breadcrumb-icon")}<strong>${esc(task.id)}</strong>`;
      $("#modal-content").innerHTML = taskIssueDetail(task, slice);
    } else {
      modalEntity = "slice";
      modalTaskId = null;
      setText("#modal-id", `${slice.id} · ${slice.priority} · revision ${slice.revision}`);
      setText("#modal-title", slice.title);
      $("#modal-state").innerHTML = `<span class="state-dot ${tone(slice.status)}"></span>`;
      $("#modal-breadcrumbs").innerHTML = `<button type="button" data-modal-root>Slices</button>${icon("chevron-right", "breadcrumb-icon")}<strong>${esc(slice.title)}</strong>`;
      $("#modal-content").innerHTML = sliceIssueDetail(slice);
    }
    $("#modal-content").scrollTop = 0;
  }

  function openModal(sliceId) {
    modalSliceId = sliceId;
    modalTaskId = null;
    modalEntity = "slice";
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
      if (task) { modalTaskId = task.dataset.openTask; modalEntity = "task"; renderModal(); return; }
      if (event.target.closest("[data-modal-slice]")) { modalTaskId = null; modalEntity = "slice"; renderModal(); return; }
      if (event.target.closest("[data-modal-root]")) closeModal();
    });
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
