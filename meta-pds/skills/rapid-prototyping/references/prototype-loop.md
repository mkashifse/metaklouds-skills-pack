# Rapid Prototype Loop

## Input quality

Start when one journey or decision is clear enough to make visible. Do not wait
for a complete initiative. If the assignment is contradictory, return one
recommended clarification instead of guessing.

## Seed strategy

Keep fixtures close to the prototype and easy to understand:

```text
prototype/
├── data/ or fixtures/
│   ├── default.json
│   ├── empty.json
│   ├── failure.json
│   └── permission-denied.json
└── state reset or scenario selector
```

When `localStorage` is used:

- namespace keys by initiative or prototype;
- include a seed/schema version;
- provide one reset action;
- avoid retaining secrets or personal data;
- ensure a stale seed can be replaced predictably.

## Human review packet

Give the Product Manager a compact packet to show the Human:

```text
Prototype update:
Decisions demonstrated:
How to start:
Routes to open:
Seeded scenarios:
Reset method:
Questions this round should answer:
Known limitations:
```

Human observations become `LOCKED`, `TESTING`, or `SUPERSEDED` decisions only
when the Product Manager records them. Prototype code never becomes authority.
