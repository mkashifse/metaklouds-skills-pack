(function () {
  "use strict";

  const data = window.META_PDS_DASHBOARD_DATA;

  if (!data) {
    document.body.innerHTML =
      '<main style="padding:32px;color:#eee;background:#151515;min-height:100vh">' +
      "<h1>Dashboard data unavailable</h1>" +
      "<p>Ensure dashboard-data.js is present beside index.html.</p>" +
      "</main>";
    return;
  }

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  const pretty = (value) =>
    String(value ?? "")
      .replaceAll("_", " ")
      .toLowerCase()
      .replace(/\b\w/g, (character) => character.toUpperCase());

  const time = (value) =>
    new Intl.DateTimeFormat("en", {
      hour: "numeric",
      minute: "2-digit"
    }).format(new Date(value));

  const dateTime = (value) =>
    new Intl.DateTimeFormat("en", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit"
    }).format(new Date(value));

  const statusTone = (status) => {
    const tones = {
      ON_TRACK: "on-track",
      RELEASED: "released",
      OUTCOME_VALIDATED: "released",
      DONE: "done",
      LOCKED: "locked",
      PASSED: "passed",
      HUMAN_REVIEW: "review",
      IN_PROGRESS: "in-progress",
      VERIFYING: "verifying",
      TESTING: "testing",
      READY: "ready",
      READY_FOR_DEVELOPMENT: "ready",
      EXECUTION_READY: "ready",
      PROPOSED: "proposed",
      NOT_READY: "not-ready",
      PLANNING_REVIEW: "planning",
      BLOCKED: "blocked",
      REWORK_REQUIRED: "blocked",
      REVERIFY_REQUIRED: "blocked",
      FAILED: "failed",
      DRAFT: "draft",
      SUPERSEDED: "superseded",
      PAUSED: "paused"
    };
    return tones[status] || "draft";
  };

  const pill = (status, label = pretty(status)) =>
    `<span class="status-pill status-${statusTone(status)}">${esc(label)}</span>`;

  const percentage = (passed, total) => (total ? Math.round((passed / total) * 100) : 0);

  const setText = (selector, value) => {
    const element = $(selector);
    if (element) element.textContent = value;
  };

  function renderShell() {
    const { initiative, projection } = data;
    setText("#sidebar-initiative", initiative.shortName || initiative.name);
    setText("#sidebar-initiative-id", initiative.id);
    setText("#initiative-id", initiative.id);
    setText("#initiative-name", initiative.name);
    setText("#initiative-phase", pretty(initiative.phase));
    setText("#initiative-objective", initiative.objective);
    setText("#initiative-progress", `${initiative.progress}%`);
    setText("#next-action-title", initiative.nextAction.title);
    setText("#next-action-detail", initiative.nextAction.detail);
    setText("#next-action-owner", initiative.nextAction.owner);
    setText("#next-action-impact", initiative.nextAction.impact);
    setText("#topbar-updated", `Updated ${dateTime(projection.generatedAt)}`);
    setText("#sidebar-updated", `Updated ${dateTime(projection.generatedAt)}`);
    setText("#footer-source", `${projection.source} · schema v${data.schemaVersion}`);

    const health = $("#initiative-health");
    health.textContent = pretty(initiative.health);
    health.className = `status-pill status-${statusTone(initiative.health)}`;

    $("#progress-ring").style.setProperty("--progress", initiative.progress);
    setText("#nav-prototype-count", data.prototype ? 1 : 0);
    setText("#nav-slice-count", data.slices.length);

    const activePackages = data.workPackages.filter(
      (item) => !["DONE", "PAUSED"].includes(item.status)
    );
    const blockers = data.workPackages.filter((item) => item.status === "BLOCKED");
    const completeSlices = data.slices.filter((slice) =>
      ["RELEASED", "OUTCOME_VALIDATED"].includes(slice.status)
    );

    setText("#nav-active-count", activePackages.length);
    setText("#metric-slices", `${completeSlices.length} / ${data.slices.length}`);
    setText("#metric-active", activePackages.length);
    setText("#metric-attention", data.attention.length);
    setText("#metric-coverage", `${data.quality.evidenceCoverage}%`);
    setText("#metric-blockers", blockers.length);
  }

  function renderAttention() {
    setText("#attention-count", data.attention.length);
    $("#attention-list").innerHTML = data.attention
      .map(
        (item) => `
          <article class="attention-item">
            <span class="attention-marker ${esc(item.kind)}"></span>
            <div>
              <h3>${esc(item.title)}</h3>
              <p>${esc(item.detail)}</p>
            </div>
            <small>${esc(item.age)}</small>
          </article>
        `
      )
      .join("");
  }

  function renderPrototype() {
    const prototype = data.prototype;
    setText("#prototype-name", prototype.name);
    setText("#prototype-description", prototype.description);

    const status = $("#prototype-status");
    status.textContent = pretty(prototype.status);
    status.className = `status-pill status-${statusTone(prototype.status)}`;

    $("#prototype-stats").innerHTML = [
      `${prototype.journeys.reviewed}/${prototype.journeys.total} journeys reviewed`,
      `${prototype.assumptionsTested} assumptions tested`,
      `${prototype.openQuestions} open questions`,
      prototype.persistence
    ]
      .map((value) => `<span class="prototype-stat">${esc(value)}</span>`)
      .join("");

    $("#prototype-checkpoint").innerHTML = `
      <span><strong>${esc(prototype.checkpoint)}</strong> · ${esc(prototype.manualReview)}</span>
      <span>${esc(time(prototype.checkpointAt))}</span>
    `;
  }

  let decisionFilter = "ALL";

  function renderDecisionFilters() {
    const statuses = ["ALL", "LOCKED", "TESTING", "PROPOSED", "SUPERSEDED"];
    $("#decision-filters").innerHTML = statuses
      .map((status) => {
        const count =
          status === "ALL"
            ? data.decisions.length
            : data.decisions.filter((decision) => decision.status === status).length;
        return `<button class="segment-button ${status === decisionFilter ? "is-active" : ""}" type="button" data-decision-filter="${status}">${pretty(status)} ${count}</button>`;
      })
      .join("");

    $$('[data-decision-filter]').forEach((button) => {
      button.addEventListener("click", () => {
        decisionFilter = button.dataset.decisionFilter;
        renderDecisionFilters();
        renderDecisions();
      });
    });
  }

  function renderDecisions() {
    const decisions = data.decisions.filter(
      (decision) => decisionFilter === "ALL" || decision.status === decisionFilter
    );
    $("#decision-list").innerHTML = decisions
      .map(
        (decision) => `
          <article class="decision-card">
            <div class="decision-card-top">
              <span class="decision-id">${esc(decision.id)} · r${esc(decision.revision)}</span>
              ${pill(decision.status)}
            </div>
            <h3>${esc(decision.title)}</h3>
            <p>${esc(decision.summary)}</p>
            <footer>
              <span>${esc(decision.affects.join(", "))}</span>
              <span>${esc(time(decision.updatedAt))}</span>
            </footer>
          </article>
        `
      )
      .join("");
  }

  function renderRoadmap() {
    $("#roadmap-list").innerHTML = data.slices
      .map(
        (slice) => `
          <article class="roadmap-card ${slice.active ? "is-active" : ""}">
            <div class="roadmap-order">
              <span>${String(slice.order).padStart(2, "0")} · ${esc(slice.id)}</span>
              <span>${esc(slice.priority)}</span>
            </div>
            <h3>${esc(slice.title)}</h3>
            <p>${esc(slice.outcome)}</p>
            <div class="roadmap-progress"><i style="width:${Number(slice.progress)}%"></i></div>
            <div class="roadmap-footer">
              <span>${esc(slice.progress)}%</span>
              <span>r${esc(slice.revision)} · ${esc(slice.stories)} stories</span>
            </div>
            <div style="margin-top:11px">${pill(slice.status)}</div>
          </article>
        `
      )
      .join("");
  }

  const kanbanColumns = ["BLOCKED", "READY", "IN_PROGRESS", "VERIFYING", "DONE"];
  let selectedSlice = "ALL";
  let selectedArea = "ALL";

  function renderWorkFilters() {
    const slices = ["ALL", ...new Set(data.workPackages.map((item) => item.sliceId))];
    const areas = ["ALL", ...new Set(data.workPackages.map((item) => item.area))];

    $("#slice-filter").innerHTML = slices
      .map((value) => `<option value="${esc(value)}">${value === "ALL" ? "All slices" : esc(value)}</option>`)
      .join("");
    $("#area-filter").innerHTML = areas
      .map((value) => `<option value="${esc(value)}">${value === "ALL" ? "All areas" : esc(pretty(value))}</option>`)
      .join("");

    $("#slice-filter").value = selectedSlice;
    $("#area-filter").value = selectedArea;

    $("#slice-filter").addEventListener("change", (event) => {
      selectedSlice = event.target.value;
      renderKanban();
    });
    $("#area-filter").addEventListener("change", (event) => {
      selectedArea = event.target.value;
      renderKanban();
    });
  }

  function workCard(item) {
    const testPercent = percentage(item.tests.passed, item.tests.total);
    return `
      <article class="work-card ${item.critical ? "is-critical" : ""}" title="${esc(item.blocker || item.description)}">
        <div class="work-card-top">
          <span class="work-id">${esc(item.id)} · ${esc(item.sliceId)}</span>
          <span class="area-label">${esc(item.area)}</span>
        </div>
        <h3>${esc(item.title)}</h3>
        <p>${esc(item.blocker || item.description)}</p>
        <div class="work-card-footer">
          <span class="owner-badge"><i>${esc(item.ownerInitials)}</i>${esc(item.owner)}</span>
          <span>${testPercent}% tests</span>
        </div>
      </article>
    `;
  }

  function renderKanban() {
    const filtered = data.workPackages.filter(
      (item) =>
        (selectedSlice === "ALL" || item.sliceId === selectedSlice) &&
        (selectedArea === "ALL" || item.area === selectedArea)
    );

    $("#kanban-board").innerHTML = kanbanColumns
      .map((status) => {
        const items = filtered.filter((item) => item.status === status);
        return `
          <section class="kanban-column" aria-label="${esc(pretty(status))}">
            <div class="kanban-column-header"><span>${esc(pretty(status))}</span><span>${items.length}</span></div>
            <div class="kanban-items">
              ${items.length ? items.map(workCard).join("") : '<div class="empty-column">No work in this state</div>'}
            </div>
          </section>
        `;
      })
      .join("");
  }

  function renderTraceability() {
    setText("#traceability-summary", `${data.stories.length} stories · acceptance mapped`);
    $("#traceability-body").innerHTML = data.stories
      .map((story) => {
        const acceptancePercent = percentage(story.acceptance.passed, story.acceptance.total);
        return `
          <tr>
            <td class="story-title"><strong>${esc(story.title)}</strong><span>${esc(story.id)}</span></td>
            <td>${esc(story.sliceId)}</td>
            <td><div class="package-links">${story.workPackageIds
              .map((id) => `<span class="package-link">${esc(id)}</span>`)
              .join("")}</div></td>
            <td class="acceptance-cell">
              <div class="acceptance-row"><span>${story.acceptance.passed}/${story.acceptance.total}</span><span>${acceptancePercent}%</span></div>
              <div class="micro-progress"><i style="width:${acceptancePercent}%"></i></div>
            </td>
            <td>${pill(story.status)}</td>
          </tr>
        `;
      })
      .join("");
  }

  function renderDependencies() {
    const dependency = data.dependencies;
    setText("#dependency-risk", `${pretty(dependency.risk)} risk`);
    $("#dependency-view").innerHTML = `
      <div class="critical-path" aria-label="Critical path">
        ${dependency.criticalPath
          .map(
            (node, index) =>
              `${index ? '<span class="path-arrow">→</span>' : ""}<span class="path-node ${node === dependency.currentNode ? "current" : ""}">${esc(node)}</span>`
          )
          .join("")}
      </div>
      <div class="detail-list">
        <div class="detail-row"><span>Execution wave</span><strong>${esc(dependency.executionWave)}</strong></div>
        <div class="detail-row"><span>Ready packages</span><strong>${esc(dependency.readyPackages)}</strong></div>
        <div class="detail-row"><span>Blocked packages</span><strong>${esc(dependency.blockedPackages)}</strong></div>
        <div class="detail-row"><span>Next unblock</span><strong>${esc(dependency.nextUnblock)}</strong></div>
      </div>
    `;
  }

  function renderQuality() {
    setText("#quality-score", `${data.quality.evidenceCoverage}%`);
    $("#quality-view").innerHTML = data.quality.suites
      .map((suite) => {
        const score = percentage(suite.passed, suite.total);
        return `
          <div class="suite-row">
            <div class="suite-meta"><strong>${esc(suite.name)}</strong><span>${suite.passed}/${suite.total} · ${score}%</span></div>
            <div class="micro-progress"><i style="width:${score}%"></i></div>
          </div>
        `;
      })
      .join("");
  }

  function renderRelease() {
    const release = data.release;
    const status = $("#release-status");
    status.textContent = pretty(release.status);
    status.className = `status-pill status-${statusTone(release.status)}`;
    $("#release-view").innerHTML = `
      <div class="release-gates">
        ${release.gates
          .map(
            (gate) => `
              <div class="gate-row">
                <span class="gate-icon ${gate.status === "PASSED" ? "passed" : ""}">${gate.status === "PASSED" ? "✓" : ""}</span>
                <span>${esc(gate.name)}</span>
                ${pill(gate.status)}
              </div>
            `
          )
          .join("")}
      </div>
      <div class="detail-list" style="margin-top:17px">
        <div class="detail-row"><span>Feature flag</span><strong>${esc(release.featureFlag)}</strong></div>
        <div class="detail-row"><span>Rollback</span><strong>${esc(release.rollback)}</strong></div>
      </div>
    `;
  }

  function renderDrift() {
    setText("#drift-count", data.drift.length);
    $("#drift-list").innerHTML = data.drift
      .map(
        (item) => `
          <article class="drift-item">
            <span class="drift-icon ${esc(item.severity)}">${item.severity === "high" ? "!" : item.severity === "info" ? "i" : "~"}</span>
            <div><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></div>
            <span>${esc(item.affects)}</span>
          </article>
        `
      )
      .join("");
  }

  function renderActivity() {
    $("#activity-list").innerHTML = data.activity
      .map(
        (item) => `
          <article class="activity-item">
            <span class="activity-time">${esc(time(item.at))}</span>
            <span class="timeline-mark ${esc(item.kind)}"></span>
            <div class="activity-copy"><h3>${esc(item.title)}</h3><p>${esc(item.detail)}</p></div>
          </article>
        `
      )
      .join("");
  }

  function bindNavigation() {
    $(".mobile-menu").addEventListener("click", () => {
      document.body.classList.toggle("menu-open");
    });

    $$(".nav-item").forEach((item) => {
      item.addEventListener("click", () => document.body.classList.remove("menu-open"));
    });

    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        $$(".nav-item").forEach((item) => {
          item.classList.toggle("is-active", item.dataset.section === visible.target.id);
        });
      },
      { rootMargin: "-18% 0px -68% 0px", threshold: [0.01, 0.25] }
    );
    $$(".section-anchor").forEach((section) => observer.observe(section));
  }

  renderShell();
  renderAttention();
  renderPrototype();
  renderDecisionFilters();
  renderDecisions();
  renderRoadmap();
  renderWorkFilters();
  renderKanban();
  renderTraceability();
  renderDependencies();
  renderQuality();
  renderRelease();
  renderDrift();
  renderActivity();
  bindNavigation();
})();
