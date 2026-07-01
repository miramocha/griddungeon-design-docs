---
tags:
  - path/docs/04-dev
  - type/dev
  - scope/required
  - status/active
---
# Design doc format (design-docs)

Markdown shape for this vault. **Frontmatter tags** ([obsidian-tags](obsidian-tags.md)) own **scope** and **lifecycle**; this doc owns **section chrome** and **heading patterns**.

**Audit:** `.\scripts\audit-doc-format.ps1` — report only; fix in phased PRs (see [Maintenance backlog](#maintenance-backlog)).

---

## Principles

1. **One status source** — `status/*` in YAML frontmatter. Do not add body `**Status:**` on new or touched docs (remove when editing legacy files).
2. **Template = chrome, not outline** — combat keeps AGI sections; `map-reveal-save-format` keeps byte layout. Shared blocks: intro, scope line, related links.
3. **Authority lines up front** — what this file owns vs siblings (table or bullets) before deep rules.
4. **Related last** — `## Related` or `## Related docs` as final section on system, content, and dev docs.
5. **ADR filenames** may keep historical `mvp1` slugs; **link text** uses default / optional / required scope language.

---

## Profiles

### System (`docs/02-systems/`)

**Tags:** `type/system` + `path/docs/02-systems` + `scope/*` + `status/*` + `domain/*`

```markdown
---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/draft
  - domain/combat
---
# {Short name}

{One paragraph — what rules this doc owns.}

**Scope:** [Required](../00-release-scope.md#required-first-playable) | Optional | Later — one line
**ADR:** [NNN](../../decisions/…md) when locked (omit if none yet)
**Game issues:** [#nnn](url) when tracked (omit if N/A)

## {Domain sections — flexible}

## Consider / explore

Optional — open questions only; link ADRs/issues.

## Related docs

- [sibling](other.md)
```

| Section | Required? |
|---------|-----------|
| H1 title (no `02 —` prefix in body — README index carries numbers) | Yes |
| Scope line | Yes |
| `## Related` / `## Related docs` | Yes |
| `## Consider / explore` | When open questions exist |
| Body `**Status:**` | **No** — use frontmatter |

**Reference examples:** [foe-encounters](../02-systems/foe-encounters.md) (tight), [guided-tutorial](../02-systems/guided-tutorial.md) (rich links — migrate to scope line over time).

---

### Content (`docs/03-content/`)

**Tags:** `type/content` + `path/docs/03-content` + `domain/campaign/s1` etc.

```markdown
# {Content title}

**Tracking:** [design-docs #n](url) · **Implementation:** [game #n](url)

**Authority split:**

| Topic | Doc |
|-------|-----|
| … | … |

**Locked:** IDs / compositions — **Tunable:** numbers in data

---

## {Tables, beats, copy}
```

**Story event drafts** (`story-events/s1/*.md`):

```markdown
# Draft — `{storyEventId}`

**When:** … · **Prerequisite:** … · **Dismiss:** …
**Effects on final dismiss:** …

## Script (`textKey` + `textEn`)
```

Use `status/synced` in frontmatter when game asset matches.

---

### Dev / integrator (`docs/04-dev/`)

**Tags:** `type/dev` + `status/active` typical

```markdown
# {Name}

{Who reads this and when.}

**Implementation repo:** [griddungeon-game](https://github.com/miramocha/griddungeon-game) — `Assets/…` paths
**Related:** sibling dev docs + system spec links

## Problem

## Design

## Checklist / recipe

## Gotchas

## Related
```

Long guides may use `---` horizontal rules between major parts ([centralized-ui-services](centralized-ui-services.md)). Prefer `## Problem` over inline bold walls.

---

### ADR (`decisions/`)

**Tags:** `type/adr` + `path/decisions` + `status/accepted|proposed|deferred`

```markdown
---
tags: …
---
# ADR NNN — {Title}

**Status:** Accepted | Proposed | Deferred
**Date:** YYYY-MM-DD
**Triggers implementation:** (optional — when policy must land)

## Context

## Decision

## Consequences

## Related (optional)
```

Body `**Status:**` stays on ADRs — it is the human-readable lock line alongside `status/*` tag. Audit warns on **mismatch** only.

---

### Vision & loop (`docs/00-*`, `docs/01-*`)

**Tags:** `type/vision` or `type/loop`

Minimal chrome: H1, link [release scope](../00-release-scope.md), no `## Related` required.

---

### Plan (`docs/plans/`)

**Tags:** `type/plan`

H1, **Status** or goal paragraph, phased checklist, link ADRs/issues.

---

### Archive (`docs/archive/`)

**Tags:** `status/archived` + `type/archive`

```markdown
> **Archived** — Superseded by [release scope](../00-release-scope.md). Do not update.
```

No further edits except broken-link fixes.

---

### Reference (`docs/refs/`)

**Tags:** `type/ref` + `scope/later`

Scratchpad — no spec authority statement in [refs README](../refs/README.md).

---

## Title conventions

| Location | Pattern | Example |
|----------|---------|---------|
| System | `# {Name}` | `# Combat` |
| Content | `# {Name}` | `# Stratum 1 enemy roster` |
| ADR | `# ADR NNN — {Title}` | `# ADR 001 — Grid Movement Feel` |
| Story draft | `# Draft — \`id\`` | `# Draft — \`s1_b1f_gate_briefing\`` |
| README index | `02 — {Name}` in link text only | — |

---

## Encoding

UTF-8 without BOM. Use real em dashes (`—`), middle dots (` · `), arrows (`→`) — not `â€"`, `ï¿½`, or `Â·`. Audit script flags common mojibake.

---

## Maintenance backlog

| Phase | Work |
|-------|------|
| **A** | This doc + audit script (**done**) |
| **B** | Run audit; triage report |
| **C** | Normalize tier-1: `combat`, `game-phase`, `mapping`, `hub-and-services`, `story-events`, `centralized-ui-services` |
| **D** | Wave `02-systems/` remainder |
| **E** | Content + dev; remove duplicate body `**Status:**` |

Track format debt on GitHub when audit findings are non-trivial.

---

## Tooling

| Script | Purpose |
|--------|---------|
| [audit-doc-format.ps1](../../scripts/audit-doc-format.ps1) | Lint markdown; JSON report |
| [apply-obsidian-tags.ps1](../../scripts/apply-obsidian-tags.ps1) | Apply tag registry |
| [obsidian-tag-registry.json](../../scripts/obsidian-tag-registry.json) | Per-file tags |

Add new docs: registry row → tags script → match profile above → README index row.
