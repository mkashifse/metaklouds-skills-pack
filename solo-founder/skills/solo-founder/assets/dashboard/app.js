(() => {
  "use strict";

  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
  const pretty = (value) => String(value ?? "Unknown").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  const values = (value) => Array.isArray(value) ? value : value == null || value === "" ? [] : [value];
  const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#icon-${name}"></use></svg>`;

  let data = null;
  let currentView = "truth";
  let truthFilter = "all";
  let sliceFilter = "all";
  let workFilter = "active";
  let issueFilter = "open";
  let toastTimer = null;

  const terminalWork = new Set(["DONE", "CANCELLED"]);
  const completeStatuses = new Set(["APPROVED", "DONE", "RELEASED", "OUTCOME_VALIDATED", "PASSED", "CLOSED", "RESOLVED"]);
  const activeStatuses = new Set(["ACTIVE", "IN_PROGRESS", "IMPLEMENTATION", "EXECUTING"]);
  const reviewStatuses = new Set(["PROPOSED", "VERIFYING", "REWORK", "REVIEW", "HUMAN_APPROVAL_REQUIRED"]);
  const readyStatuses = new Set(["READY", "APPROVED_FOR_IMPLEMENTATION"]);
  const blockedStatuses = new Set(["BLOCKED", "FAILED", "AT_RISK"]);

  function tone(status) {
    const value = String(status || "UNKNOWN").toUpperCase();
    if (completeStatuses.has(value)) return "complete";
    if (activeStatuses.has(value)) return "active";
    if (reviewStatuses.has(value)) return "review";
    if (readyStatuses.has(value)) return "ready";
    if (blockedStatuses.has(value)) return "blocked";
    return "neutral";
  }

  function status(value) {
    return `<span class="status ${tone(value)}">${esc(pretty(value))}</span>`;
  }

  function dateTime(value) {
    if (!value) return "Time not recorded";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(date);
  }

  function listSection(title, entries, fallback = "None recorded") {
    const items = values(entries).filter((entry) => entry != null && String(entry).trim());
    return `<section><h3>${esc(title)}</h3>${items.length ? `<ul>${items.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>` : `<p>${esc(fallback)}</p>`}</section>`;
  }

  function textSection(title, value, fallback = "Not recorded") {
    return `<section><h3>${esc(title)}</h3><p>${esc(value || fallback)}</p></section>`;
  }

  function propertyRows(rows) {
    return `<aside class="property-panel"><h3>Properties</h3>${rows.map(([label, value]) => `<div class="property-row"><span>${esc(label)}</span><strong>${value}</strong></div>`).join("")}</aside>`;
  }

  function filterButtons(options, selected) {
    return options.map(([value, label, count]) => `<button class="filter-button ${selected === value ? "is-active" : ""}" type="button" data-filter="${esc(value)}">${esc(label)}${count == null ? "" : ` · ${esc(count)}`}</button>`).join("");
  }

  function emptyState(title, detail) {
    return `<div class="empty-state"><strong>${esc(title)}</strong><p>${esc(detail)}</p></div>`;
  }

  function truthItems() {
    return data.layers.flatMap((layer) => (data.truth.truth[layer] || []).map((item) => ({ ...item, layer }))).sort((left, right) => String(right.proposed_at || "").localeCompare(String(left.proposed_at || "")) || left.id.localeCompare(right.id));
  }

  function activeInitiative() {
    const id = data.ledger.current?.active_initiative_id;
    return (data.ledger.initiatives || []).find((item) => item.id === id) || null;
  }

  function handoffLabel(item) {
    if (item.execution !== "DELEGATED") return "PM direct";
    if (item.handoff_consumed_at) return `${pretty(item.handoff_type)} · consumed`;
    if (item.handoff_submitted_at) return `${pretty(item.handoff_type)} · awaiting PM`;
    return `${pretty(item.handoff_type)} · awaiting submission`;
  }

  function showToast(message, isError = false) {
    const toast = $("#toast");
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.classList.toggle("error", isError);
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 3200);
  }

  function renderHeader() {
    const truths = truthItems();
    $("#environment-badge").hidden = !data.demo;
    $("#truth-count").textContent = truths.length;
    $("#slice-count").textContent = data.slices.length;
    $("#work-count").textContent = data.counts.active_work;
    $("#issue-count").textContent = data.counts.issues;
    $("#projection-source").textContent = data.demo
      ? `Demo seed data · ${data.ledger.product?.title || "Sample product"}`
      : `Parsed ${dateTime(data.generated_at)} · ${data.ledger.product?.title || data.ledger.product?.id || "Product"}`;
  }

  function renderHealth() {
    const panel = $("#data-health");
    if (!data.diagnostics?.length) {
      panel.hidden = true;
      panel.innerHTML = "";
      return;
    }
    panel.hidden = false;
    panel.innerHTML = `<strong>${data.diagnostics.length} artifact ${data.diagnostics.length === 1 ? "issue" : "issues"}</strong><ul>${data.diagnostics.map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`;
  }

  function renderContext() {
    const current = data.ledger.current || {};
    const initiative = activeInitiative();
    const next = current.next_recommended_action || {};
    const affected = values(current.affected_layers).map(pretty).join(", ");
    $("#context-strip").innerHTML = `
      <div class="context-item"><small>Mode</small><strong>${esc(pretty(current.mode))}</strong><p>${esc(data.counts.proposed)} proposed Truth</p></div>
      <div class="context-item"><small>Current Layer</small><strong>${esc(pretty(current.layer))}</strong><p>${esc(affected || "No additional affected Layers")}</p></div>
      <div class="context-item"><small>Initiative</small><strong>${esc(initiative?.title || initiative?.id || "Not selected")}</strong><p>${esc(initiative ? pretty(initiative.status) : "No active initiative")}</p></div>
      <div class="context-item next-action"><small>Next Action</small><strong>${esc(next.title || "No next action recorded")}${next.human_approval_required ? '<span class="attention-mark">Human approval</span>' : ""}</strong><p>${esc(next.impact || "Product Ledger has no recommended impact recorded.")}</p></div>`;
  }

  function truthRow(item) {
    return `<details class="document-row">
      <summary>
        <span class="entity-icon">${icon("brain")}</span>
        <span class="row-copy"><span class="row-meta"><i class="state-dot ${tone(item.status)}"></i><span>${esc(item.id)} · ${esc(pretty(item.layer))} · ${esc(dateTime(item.proposed_at))}</span></span><h2>${esc(item.title)}</h2><p>${esc(item.statement)}</p></span>
        <span class="row-side">${status(item.status)}</span>
        <span class="chevron">${icon("chevron")}</span>
      </summary>
      <div class="row-body">
        <div class="body-main">
          ${textSection("Canonical statement", item.statement)}
          ${listSection("Evidence", item.evidence, "No evidence recorded")}
          ${item.status === "PROPOSED" ? data.demo
            ? `<button class="approval-button demo-only" type="button" disabled>${icon("check")}Demo — approval unavailable</button>`
            : `<button class="approval-button" type="button" data-approve-truth="${esc(item.id)}">${icon("check")}Approve as Canonical Truth</button>` : ""}
        </div>
        ${propertyRows([
          ["Status", status(item.status)],
          ["Layer", esc(pretty(item.layer))],
          ["Affected Layers", esc(values(item.affected_layers).map(pretty).join(", ") || "None")],
          ["Replaces", esc(item.replaces || "None")],
          ["Approved by", esc(item.approved_by || "Not approved")],
          ["Approval channel", esc(item.approved_via || "—")],
        ])}
      </div>
    </details>`;
  }

  function renderTruth() {
    const all = truthItems();
    const shown = all.filter((item) => truthFilter === "all" || item.status.toLowerCase() === truthFilter);
    $("#truth-filters").innerHTML = filterButtons([
      ["all", "All", all.length],
      ["proposed", "Proposed", data.counts.proposed],
      ["approved", "Approved", data.counts.approved],
    ], truthFilter);
    $("#truth-summary").innerHTML = `<span>Current Layer<strong>${esc(pretty(data.ledger.current?.layer))}</strong></span><span>Human review<strong>${esc(data.counts.proposed)}</strong></span>`;
    $("#truth-list").innerHTML = shown.length ? shown.map(truthRow).join("") : emptyState("No matching Truth", all.length ? "Change the status filter to see other Truth." : "Proposed and approved product decisions will appear here.");
  }

  function sliceIsOpen(item) {
    return !["DONE", "RELEASED", "OUTCOME_VALIDATED", "CANCELLED"].includes(item.status);
  }

  function sliceRow(item) {
    const linkedWork = data.ledger.work.filter((work) => values(work.linked_slice_ids).includes(item.id));
    return `<details class="document-row">
      <summary>
        <span class="entity-icon">${icon("layers")}</span>
        <span class="row-copy"><span class="row-meta"><i class="state-dot ${tone(item.status)}"></i><span>${esc(item.id)} · ${esc(item.priority)} priority · ${esc(item.capability_family || "Capability")}</span></span><h2>${esc(item.title)}</h2><p>${esc(item.outcome || "Capability outcome is not recorded.")}</p></span>
        <span class="row-side"><span>${esc(item.story_count)} stories · ${esc(linkedWork.length)} work</span>${status(item.status)}</span>
        <span class="chevron">${icon("chevron")}</span>
      </summary>
      <div class="row-body">
        <div class="body-main">
          ${textSection("Capability outcome", item.outcome)}
          ${listSection("Dependencies", item.dependencies)}
          ${linkedWork.length ? listSection("Linked work", linkedWork.map((work) => `${work.id} — ${work.title} [${pretty(work.status)}]`)) : ""}
        </div>
        ${propertyRows([
          ["Status", status(item.status)],
          ["Priority", esc(item.priority)],
          ["Stories", esc(item.story_count)],
          ["Tests", esc(item.test_count)],
          ["Prototype checkpoint", esc(item.prototype_checkpoint || "None")],
          ["Promotion map", esc(item.promotion_map || "None")],
          ["Source", `<code>${esc(`docs/solo-founder/slices/${item.file}`)}</code>`],
        ])}
      </div>
    </details>`;
  }

  function renderSlices() {
    const all = data.slices;
    const open = all.filter(sliceIsOpen);
    const done = all.filter((item) => !sliceIsOpen(item));
    const shown = all.filter((item) => sliceFilter === "all" || (sliceFilter === "open" ? sliceIsOpen(item) : !sliceIsOpen(item)));
    $("#slice-filters").innerHTML = filterButtons([["all", "All", all.length], ["open", "Open", open.length], ["done", "Complete", done.length]], sliceFilter);
    $("#slice-summary").innerHTML = `<span>Stories<strong>${esc(all.reduce((sum, item) => sum + item.story_count, 0))}</strong></span><span>Tests<strong>${esc(all.reduce((sum, item) => sum + item.test_count, 0))}</strong></span>`;
    $("#slice-list").innerHTML = shown.length ? shown.map(sliceRow).join("") : emptyState("No matching Slices", all.length ? "Change the filter to see other Slices." : "Human-approved Fat Slices will appear here when shaped.");
  }

  function workMatches(item) {
    if (workFilter === "all") return true;
    if (workFilter === "active") return !terminalWork.has(item.status);
    if (workFilter === "review") return ["VERIFYING", "REWORK"].includes(item.status);
    if (workFilter === "blocked") return item.status === "BLOCKED";
    return terminalWork.has(item.status);
  }

  function workRow(item) {
    return `<details class="document-row">
      <summary>
        <span class="entity-icon">${icon("list")}</span>
        <span class="row-copy"><span class="row-meta"><i class="state-dot ${tone(item.status)}"></i><span>${esc(item.id)} · ${esc(pretty(item.activity))} · ${esc(pretty(item.classification))} · ${esc(pretty(item.execution))}</span></span><h2>${esc(item.title)}</h2><p>${esc(item.expected_outcome || item.instruction || "Expected outcome is not recorded.")}</p></span>
        <span class="row-side"><span class="owner">${esc(item.owner)}</span>${status(item.status)}</span>
        <span class="chevron">${icon("chevron")}</span>
      </summary>
      <div class="row-body">
        <div class="body-main">
          ${textSection("Instruction", item.instruction)}
          ${textSection("Expected outcome", item.expected_outcome)}
          ${listSection("Acceptance criteria", item.acceptance_criteria)}
          ${item.result ? textSection("Result", item.result) : ""}
          ${values(item.evidence).length ? listSection("Evidence", item.evidence) : ""}
          ${item.blocker ? textSection("Blocker", item.blocker) : ""}
        </div>
        ${propertyRows([
          ["Status", status(item.status)],
          ["Execution", esc(pretty(item.execution))],
          ["Role", esc(pretty(item.role))],
          ["Owner", esc(item.owner)],
          ["Focus", esc(pretty(item.workstream))],
          ["Priority", esc(item.priority || "Unset")],
          ["Handoff", esc(handoffLabel(item))],
          ["Handoff path", item.handoff_path ? `<code>${esc(item.handoff_path)}</code>` : "None"],
        ])}
      </div>
    </details>`;
  }

  function renderWork() {
    const all = data.ledger.work || [];
    const shown = all.filter(workMatches);
    const review = all.filter((item) => ["VERIFYING", "REWORK"].includes(item.status)).length;
    const done = all.filter((item) => terminalWork.has(item.status)).length;
    $("#work-filters").innerHTML = filterButtons([
      ["active", "Active", data.counts.active_work],
      ["review", "PM Review", review],
      ["blocked", "Blocked", data.counts.blocked_work],
      ["done", "Complete", done],
      ["all", "All", all.length],
    ], workFilter);
    $("#work-summary").innerHTML = `<span>PM direct<strong>${esc(data.counts.direct_work)}</strong></span><span>Delegated<strong>${esc(data.counts.delegated_work)}</strong></span>`;
    $("#work-list").innerHTML = shown.length ? shown.map(workRow).join("") : emptyState("No matching Work Packages", all.length ? "Change the filter to see other work." : "Bounded PM and delegated work will appear here.");
  }

  function issueStatus(item) {
    return String(item.status || (item.resolved_at ? "RESOLVED" : "OPEN")).toUpperCase();
  }

  function issueIsOpen(item) {
    return !["DONE", "CLOSED", "RESOLVED", "CANCELLED"].includes(issueStatus(item));
  }

  function issueMatches(item) {
    if (issueFilter === "all") return true;
    if (issueFilter === "human") return Boolean(item.human_approval_required);
    if (issueFilter === "closed") return !issueIsOpen(item);
    return issueIsOpen(item);
  }

  function issueRow(item) {
    const itemStatus = issueStatus(item);
    const title = item.title || item.summary || `${pretty(item.kind)} ${item.id}`;
    const detail = item.description || item.detail || item.impact || item.blocker || "No issue detail recorded.";
    return `<details class="document-row">
      <summary>
        <span class="entity-icon">${icon("alert")}</span>
        <span class="row-copy"><span class="row-meta"><i class="state-dot ${tone(itemStatus === "OPEN" ? "BLOCKED" : itemStatus)}"></i><span>${esc(item.id)} · ${esc(pretty(item.kind))}${item.severity ? ` · ${esc(pretty(item.severity))}` : ""}</span></span><h2>${esc(title)}</h2><p>${esc(detail)}</p></span>
        <span class="row-side">${item.human_approval_required ? '<span class="status review">Human decision</span>' : ""}${status(itemStatus)}</span>
        <span class="chevron">${icon("chevron")}</span>
      </summary>
      <div class="row-body">
        <div class="body-main">${textSection("Detail", detail)}${item.recommendation ? textSection("Recommendation", item.recommendation) : ""}${listSection("Evidence", item.evidence)}</div>
        ${propertyRows([
          ["Kind", esc(pretty(item.kind))],
          ["Status", status(itemStatus)],
          ["Severity", esc(pretty(item.severity || "Not set"))],
          ["Human approval", item.human_approval_required ? "Required" : "Not required"],
          ["Linked work", esc(values(item.work_ids || item.linked_work_ids).join(", ") || "None")],
          ["Linked Truth", esc(values(item.truth_ids || item.linked_truth_ids).join(", ") || "None")],
        ])}
      </div>
    </details>`;
  }

  function renderIssues() {
    const all = data.ledger.issues || [];
    const open = all.filter(issueIsOpen);
    const human = all.filter((item) => item.human_approval_required);
    const shown = all.filter(issueMatches);
    $("#issue-filters").innerHTML = filterButtons([["open", "Open", open.length], ["human", "Human Attention", human.length], ["closed", "Closed", all.length - open.length], ["all", "All", all.length]], issueFilter);
    $("#issue-summary").innerHTML = `<span>Drift<strong>${esc(all.filter((item) => item.kind === "DRIFT").length)}</strong></span><span>Blockers<strong>${esc(all.filter((item) => item.kind === "BLOCKER").length)}</strong></span><span>Risks<strong>${esc(all.filter((item) => item.kind === "RISK").length)}</strong></span>`;
    $("#issue-list").innerHTML = shown.length ? shown.map(issueRow).join("") : emptyState("No matching Issues", all.length ? "Change the filter to see other issues." : "Drift, blockers, risks, and external dependencies will appear here.");
  }

  function renderAll() {
    renderHeader();
    renderHealth();
    renderContext();
    renderTruth();
    renderSlices();
    renderWork();
    renderIssues();
    selectView(currentView, false);
  }

  function selectView(view, updateHash = true) {
    if (!new Set(["truth", "slices", "work", "issues"]).has(view)) view = "truth";
    currentView = view;
    $$(".top-tab").forEach((button) => button.classList.toggle("is-active", button.dataset.view === view));
    $$(".view-panel").forEach((panel) => panel.classList.toggle("is-active", panel.dataset.panel === view));
    if (updateHash) history.replaceState(null, "", `#${view}`);
  }

  async function api(path, options) {
    const response = await fetch(path, options);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Dashboard request failed");
    return payload;
  }

  async function load() {
    const refresh = $("#refresh-button");
    refresh.classList.add("is-loading");
    try {
      if (location.protocol === "file:" && window.SOLO_FOUNDER_DEMO_STATE) {
        data = JSON.parse(JSON.stringify(window.SOLO_FOUNDER_DEMO_STATE));
      } else {
        data = await api("/api/state");
      }
      renderAll();
    } catch (error) {
      $("#data-health").hidden = false;
      $("#data-health").innerHTML = `<strong>Dashboard data is unavailable</strong><ul><li>${esc(error.message)}</li></ul>`;
      showToast(error.message, true);
    } finally {
      refresh.classList.remove("is-loading");
    }
  }

  async function approveTruth(id, button) {
    const item = truthItems().find((entry) => entry.id === id);
    if (!item) return;
    const confirmed = window.confirm(`Approve this as Canonical Truth?\n\nLayer: ${pretty(item.layer)}\nTruth: ${item.statement}\nReplaces: ${item.replaces || "none"}\nAffected Layers: ${values(item.affected_layers).map(pretty).join(", ") || "none"}`);
    if (!confirmed) return;
    button.disabled = true;
    try {
      await api("/api/truth/approve", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id, file_hash: data.file_hash }) });
      showToast(`${id} approved as Canonical Truth.`);
      await load();
    } catch (error) {
      showToast(error.message, true);
      await load();
    } finally {
      button.disabled = false;
    }
  }

  $$(".top-tab").forEach((button) => button.addEventListener("click", () => selectView(button.dataset.view)));
  $("#refresh-button").addEventListener("click", load);
  $("#truth-filters").addEventListener("click", (event) => { const button = event.target.closest("[data-filter]"); if (button) { truthFilter = button.dataset.filter; renderTruth(); } });
  $("#slice-filters").addEventListener("click", (event) => { const button = event.target.closest("[data-filter]"); if (button) { sliceFilter = button.dataset.filter; renderSlices(); } });
  $("#work-filters").addEventListener("click", (event) => { const button = event.target.closest("[data-filter]"); if (button) { workFilter = button.dataset.filter; renderWork(); } });
  $("#issue-filters").addEventListener("click", (event) => { const button = event.target.closest("[data-filter]"); if (button) { issueFilter = button.dataset.filter; renderIssues(); } });
  $("#truth-list").addEventListener("click", (event) => { const button = event.target.closest("[data-approve-truth]"); if (button) approveTruth(button.dataset.approveTruth, button); });
  window.addEventListener("hashchange", () => selectView(location.hash.slice(1), false));

  currentView = location.hash.slice(1) || "truth";
  load();
})();
