---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
---
# Obsidian tags (design-docs)

Authority: [doc-format.md](doc-format.md) (section chrome) · this file (tags only).

Tag convention for this vault. Tags live in YAML **frontmatter** (`tags:` list) so Obsidian **Properties** and **Tag pane** stay in sync.

**Do not** duplicate tags as inline `#hashtags` in body text unless you need a one-off graph edge.

---

## Taxonomy

### Path (folder mirror)

| Tag | Folder |
|-----|--------|
| `#path/root` | `README.md` |
| `#path/docs` | `docs/*.md` (top-level only) |
| `#path/docs/02-systems` | `docs/02-systems/` |
| `#path/docs/03-content` | `docs/03-content/` |
| `#path/docs/04-dev` | `docs/04-dev/` |
| `#path/docs/archive` | `docs/archive/` |
| `#path/docs/plans` | `docs/plans/` |
| `#path/docs/refs` | `docs/refs/` |
| `#path/decisions` | `decisions/` |

### Type

| Tag | Use |
|-----|-----|
| `#type/vision` | Pillars, references, release scope |
| `#type/loop` | Core player loop |
| `#type/system` | Rules engines, mechanics |
| `#type/content` | Strata, roster, story copy, encounters |
| `#type/dev` | Integrator / UITK / implementation notes |
| `#type/adr` | Architecture decision records |
| `#type/plan` | Improvement plans |
| `#type/ref` | Scratchpads — not spec authority |
| `#type/archive` | Historical snapshots |

### Release scope (board labels)

| Tag | Meaning |
|-----|---------|
| `#scope/required` | First playable / default build |
| `#scope/optional` | Shippable later; does not block required slice |
| `#scope/later` | Deferred polish or content |

Authority: [00 — Release scope](../00-release-scope.md).

### Status

| Tag | Meaning |
|-----|---------|
| `#status/draft` | Spec in flux |
| `#status/active` | Maintained integrator doc |
| `#status/accepted` | Locked design / ADR accepted |
| `#status/proposed` | ADR or idea not locked |
| `#status/deferred` | Explicitly out of default build |
| `#status/shipped` | Implemented in game repo (may still get tuning) |
| `#status/synced` | Story draft matches game asset |
| `#status/archived` | Do not update; pointer only |

### Domain (cross-cutting)

Use 1—3 per note. Omit when type/path is enough.

| Tag | Topics |
|-----|--------|
| `#domain/combat` | AGI, skills, status, battle arena |
| `#domain/exploration` | Grid move, map, FPV, floor art |
| `#domain/hub` | Guild services, save, synthesis |
| `#domain/ui` | UITK, HUD, pickers, input hints |
| `#domain/campaign/s1` | Stratum 1 content and flags |
| `#domain/story-vn` | Visual novel events, tutorials |
| `#domain/map` | Auto-reveal, cell art, save format |
| `#domain/foe` | Patrol, contact, flee, chain join |
| `#domain/synchro` | Synchro Charge, Protocol, Navigator |
| `#domain/phase` | Hub / exploration / combat macro flow |
| `#domain/content-pipeline` | Floor editor, story authoring graphs |

---

## Frontmatter template

```yaml
---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/accepted
  - domain/combat
---
```

**ADR example:**

```yaml
---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/exploration
---
```

**Story event draft:**

```yaml
---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/synced
  - domain/campaign/s1
  - domain/story-vn
---
```

---

## Apply / refresh tags

Registry: [`scripts/obsidian-tag-registry.json`](../../scripts/obsidian-tag-registry.json)  
Script: `.\scripts\apply-obsidian-tags.ps1` (idempotent — skips files that already have `tags:` frontmatter)

Format lint: `.\scripts\audit-doc-format.ps1` → `Logs/doc-format-audit.json`

When adding a new doc:

1. Add a row to the registry JSON.
2. Run the script (or paste frontmatter manually).
3. Link from [README](../../README.md) or [04-dev README](README.md) if player-facing or integrator-critical.

---

## Graph tips

- Prefer wikilinks with readable alias: `[[decisions/014-mvp1-exploration-map|ADR 014 — default exploration map]]` (link text avoids legacy MVP wording).
- Filter graph: `tag:#scope/required` + `tag:#type/system`.
- Archive notes: always `#status/archived` + `#path/docs/archive`.

---

## Maintenance backlog (audit 2026-07)

See audit in repo chat / issues. Summary:

| Priority | Action |
|----------|--------|
| P0 | Fix broken relative links under `docs/03-content/story-events/s1/` |
| P1 | Reconcile Protocol Deploy/Transform in release scope vs ADR 023/024 |
| P1 | Extend root README index (missing ADRs 019, 028—033, 036, 042—043; key system docs) |
| P2 | MVP2/MVP3 â†’ optional/required wording in body (filenames unchanged) |
| P2 | UTF-8 cleanup (mojibake in `04-tech-notes.md`, `dungeons-and-encounters.md`) |
| P3 | Move `docs/04-dev/github-drafts/` to archive after issue close confirm |
| P3 | Keep `docs/archive/mvp1-s1-floor-layouts-draft.md` until layout lock |
