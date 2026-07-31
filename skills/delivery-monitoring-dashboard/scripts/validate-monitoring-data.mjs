#!/usr/bin/env node

import { access, readFile } from "node:fs/promises";
import { isAbsolute, resolve } from "node:path";
import process from "node:process";

const [, , jsonArgument, rootArgument] = process.argv;

if (!jsonArgument) {
  console.error(
    "Usage: node validate-monitoring-data.mjs <monitoring-data.json> [repository-root]",
  );
  process.exit(2);
}

const jsonPath = resolve(jsonArgument);
const repositoryRoot = rootArgument ? resolve(rootArgument) : null;
const errors = [];
const warnings = [];

const allowed = {
  initiative: new Set([
    "draft",
    "in_review",
    "approved",
    "in_progress",
    "blocked",
    "paused",
    "complete",
    "abandoned",
    "unknown",
  ]),
  planning: new Set([
    "pending",
    "in_progress",
    "blocked",
    "completed",
    "deferred",
    "unknown",
  ]),
  pendingDecision: new Set(["pending", "blocked", "deferred", "unknown"]),
  lockedDecision: new Set(["locked", "superseded", "unknown"]),
  slice: new Set([
    "pending",
    "in_progress",
    "blocked",
    "validation_ready",
    "released",
    "completed",
    "deferred",
    "abandoned",
    "unknown",
  ]),
  story: new Set([
    "pending",
    "in_progress",
    "blocked",
    "validation_ready",
    "done",
    "released",
    "deferred",
    "abandoned",
    "unknown",
  ]),
};

const secretKeyPattern =
  /(^|_)(api[_-]?key|authorization|connection[_-]?string|password|private[_-]?key|secret|token)($|_)/i;

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function requireObject(value, path) {
  if (!isObject(value)) {
    errors.push(`${path} must be an object`);
    return {};
  }
  return value;
}

function requireArray(value, path) {
  if (!Array.isArray(value)) {
    errors.push(`${path} must be an array`);
    return [];
  }
  return value;
}

function requireText(value, path, { allowEmpty = false } = {}) {
  if (
    typeof value !== "string" ||
    (!allowEmpty && value.trim().length === 0)
  ) {
    errors.push(`${path} must be ${allowEmpty ? "a string" : "a non-empty string"}`);
    return "";
  }
  return value;
}

function validateStatus(value, path, vocabulary) {
  requireText(value, path);
  if (typeof value === "string" && !vocabulary.has(value)) {
    errors.push(`${path} has unsupported status "${value}"`);
  }
}

function findSecretKeys(value, path = "$") {
  if (Array.isArray(value)) {
    value.forEach((item, index) => findSecretKeys(item, `${path}[${index}]`));
    return;
  }
  if (!isObject(value)) return;
  for (const [key, child] of Object.entries(value)) {
    if (secretKeyPattern.test(key)) {
      errors.push(`${path}.${key} looks like a secret-bearing field`);
    }
    findSecretKeys(child, `${path}.${key}`);
  }
}

function validateItems(items, path, vocabulary, seenIds) {
  for (const [index, rawItem] of items.entries()) {
    const itemPath = `${path}[${index}]`;
    const item = requireObject(rawItem, itemPath);
    const id = requireText(item.id, `${itemPath}.id`);
    requireText(item.title, `${itemPath}.title`);
    validateStatus(item.status, `${itemPath}.status`, vocabulary);
    if (id) {
      if (seenIds.has(id)) errors.push(`${itemPath}.id duplicates "${id}"`);
      seenIds.add(id);
    }
    if (!("source" in item) && !("evidence" in item)) {
      errors.push(`${itemPath} must include source or evidence provenance`);
    }
  }
}

let data;
try {
  data = JSON.parse(await readFile(jsonPath, "utf8"));
} catch (error) {
  console.error(`Invalid monitoring JSON: ${error.message}`);
  process.exit(1);
}

const root = requireObject(data, "$");
const schemaVersion = requireText(root.schemaVersion, "$.schemaVersion");
if (schemaVersion && !/^2\.\d+\.\d+$/.test(schemaVersion)) {
  errors.push("$.schemaVersion must use semantic version 2.x");
}

const generatedAt = requireText(root.generatedAt, "$.generatedAt");
if (generatedAt && Number.isNaN(Date.parse(generatedAt))) {
  errors.push("$.generatedAt must be an ISO-compatible date-time");
}

const source = requireObject(root.source, "$.source");
requireText(source.kind, "$.source.kind");
requireText(source.truthBoundary, "$.source.truthBoundary");
const documents = requireArray(source.documents, "$.source.documents");
for (const [index, rawDocument] of documents.entries()) {
  const document = requireObject(rawDocument, `$.source.documents[${index}]`);
  const sourcePath = requireText(
    document.path,
    `$.source.documents[${index}].path`,
  );
  if (sourcePath && isAbsolute(sourcePath)) {
    errors.push(`$.source.documents[${index}].path must be repository-relative`);
  }
  if ("sections" in document) {
    requireArray(document.sections, `$.source.documents[${index}].sections`);
  }
  if (repositoryRoot && sourcePath && !isAbsolute(sourcePath)) {
    try {
      await access(resolve(repositoryRoot, sourcePath));
    } catch {
      warnings.push(`declared source does not exist: ${sourcePath}`);
    }
  }
}

const initiative = requireObject(root.initiative, "$.initiative");
requireText(initiative.id, "$.initiative.id");
requireText(initiative.productName, "$.initiative.productName");
validateStatus(initiative.status, "$.initiative.status", allowed.initiative);
requireText(initiative.currentStage, "$.initiative.currentStage");
requireText(initiative.summary, "$.initiative.summary");

const planning = requireObject(root.planning, "$.planning");
const pendingDecisions = requireArray(
  planning.pendingDecisions,
  "$.planning.pendingDecisions",
);
const lockedDecisions = requireArray(
  planning.lockedDecisions,
  "$.planning.lockedDecisions",
);
const planningItems = requireArray(planning.items, "$.planning.items");
const slices = requireArray(root.verticalSlices, "$.verticalSlices");
const stories = requireArray(root.userStories, "$.userStories");

const seenIds = new Set();
validateItems(
  pendingDecisions,
  "$.planning.pendingDecisions",
  allowed.pendingDecision,
  seenIds,
);
validateItems(
  lockedDecisions,
  "$.planning.lockedDecisions",
  allowed.lockedDecision,
  seenIds,
);
validateItems(planningItems, "$.planning.items", allowed.planning, seenIds);
validateItems(slices, "$.verticalSlices", allowed.slice, seenIds);
validateItems(stories, "$.userStories", allowed.story, seenIds);

const sliceIds = new Set(slices.map((slice) => slice.id).filter(Boolean));
for (const [index, slice] of slices.entries()) {
  if (
    typeof slice.progress !== "number" ||
    slice.progress < 0 ||
    slice.progress > 100
  ) {
    errors.push(`$.verticalSlices[${index}].progress must be from 0 through 100`);
  }
}

for (const [index, story] of stories.entries()) {
  const sliceId = requireText(story.sliceId, `$.userStories[${index}].sliceId`);
  if (sliceId && !sliceIds.has(sliceId)) {
    errors.push(`$.userStories[${index}].sliceId references missing "${sliceId}"`);
  }
}

if (
  initiative.currentSliceId &&
  !sliceIds.has(initiative.currentSliceId)
) {
  errors.push(
    `$.initiative.currentSliceId references missing "${initiative.currentSliceId}"`,
  );
}

findSecretKeys(root);

const counts = {
  pending_decisions: pendingDecisions.length,
  locked_decisions: lockedDecisions.length,
  planning_items: planningItems.length,
  slices: slices.length,
  stories: stories.length,
};

if (errors.length > 0) {
  console.error(`Monitoring data failed validation (${errors.length} errors).`);
  errors.forEach((error) => console.error(`- ${error}`));
  warnings.forEach((warning) => console.error(`- warning: ${warning}`));
  process.exit(1);
}

console.log(
  `Monitoring data valid: ${JSON.stringify(counts)}${warnings.length ? `; ${warnings.length} warning(s)` : ""}`,
);
warnings.forEach((warning) => console.log(`Warning: ${warning}`));
