---
tags:
  - path/decisions
  - type/adr
  - scope/later
  - status/proposed
  - domain/content-pipeline
  - domain/story-vn
---
# ADR 030 — Story Event Graph Authoring (follow-up)

> **Scope: Optional feature** — not required for initial release.

**Status:** Proposed  
**Date:** 2026-05-25  
**Follows:** [ADR 028 — Story events (VN)](028-story-visual-novel-events.md) · [story-events.md](../docs/02-systems/story-events.md)  
**Does not block:** [game #87](https://github.com/miramocha/griddungeon-game/issues/87) (linear runner + S1 scenes)

## Context

[ADR 028](028-story-visual-novel-events.md) locks **launch** story delivery to a **linear step list** (`line`, `effect`) with **`choice` / branching deferred** but schema reserved (`gotoStep`, `branchId`). Runtime triggers stay in C# phase controllers ([#87](https://github.com/miramocha/griddungeon-game/issues/87)).

Design and narrative want **branching scenes** (player choices, flag-gated paths, optional beats) without hand-maintaining fragile step indices in YAML. A **graph-UI** editor (nodes + edges) is the usual visual-novel / quest-tool pattern for “if the player did X, go here.”

**Not in scope for this ADR**

- Replacing [ADR 028](028-story-visual-novel-events.md) runtime (`StoryEventRunner` still executes a **compiled step program**).
- **Campaign-wide** quest graphs spanning many floors (defer until scene count justifies it — same rationale as ADR 028 § rejected “full branching campaign graph framework”).
- **UVS** or Timeline owning story logic ([ADR 028](028-story-visual-novel-events.md) rejected; [uvs-phase-presentation.md](../docs/02-systems/uvs-phase-presentation.md) = presentation only).
- **Guided tutorial** coach graphs ([ADR 029](029-guided-tutorial.md)) — separate content type; may share editor shell later.

## Decision (proposed)

### 1. Authoring graph, runtime step list

| Layer | Owner | Role |
|-------|--------|------|
| **`StoryEventGraphAsset`** (editor) | Content / Editor | Visual graph per `storyEventId`: nodes = steps, edges = flow |
| **Compile** | Editor pipeline | Graph → ordered **`StoryEventDefinition`** (steps + `gotoStep` targets) |
| **Runtime** | `StoryEventRunner` ([ADR 028](028-story-visual-novel-events.md)) | Unchanged contract: advance steps, dispatch effects, `choice` when enabled |

**Rule:** The graph is **authoring-only**. Shipping builds consume **compiled** definitions (ScriptableObject or baked YAML under `Assets/Content/StoryEvents/`). No graph interpreter in player code at launch+.

### 2. Node kinds (editor palette)

Align with [story-events § Step kinds](../docs/02-systems/story-events.md#step-kinds-mvp1-minimum):

| Node | Maps to step | Notes |
|------|----------------|-------|
| **Line** | `line` | Speaker, `textKey`, optional emotion |
| **Effect** | `effect` | Side effects only |
| **Wait** | `wait` | Auto-advance |
| **Choice** | `choice` | N outputs → target node ids (compiled to `gotoStep`) |
| **Branch** (later) | implicit routing | **Condition** node: evaluate campaign flag / expression → pick edge |

**Entry** node: single start; **End** node: maps to `end_story_event` or runner `Complete()`.

### 3. Branching semantics

| Branch type | When | Compile target |
|-------------|------|----------------|
| **Player choice** | `choice` node | Per-option `gotoStep` index |
| **Flag branch** | `Branch` node with `if flag` edges | Ordered checks → first match `gotoStep`; default edge required |
| **Linear** | Single outgoing edge | Next step index |

Validation at compile time:

- No orphan nodes reachable from entry.
- All `choice` / branch edges resolve to valid step indices.
- Cycles allowed only where design intends (e.g. repeat prompt); warn in editor.
- Effects remain **idempotent** where replay could re-fire ([story-events](../docs/02-systems/story-events.md)).

### 4. Editor UX (target)

Unity **GraphView**-based custom Editor window (or embedded Inspector graph). **Alternative:** [ADR 031](031-floor-event-pin-condition-graph.md) proposes evaluating **[Unity Graph Toolkit](https://docs.unity3d.com/Packages/com.unity.graphtoolkit@0.4/manual/introduction.html)** as a shared editor shell for floor gating + story step graphs — decide before implementing either tool twice.

- One graph asset per `storyEventId` (matches [content index](../docs/03-content/story-events/README.md)).
- Preview compiled step list (read-only) for diff review.
- **Play-in-editor** hook (optional): invoke `StoryEventRunner.Play(id)` from DevBootstrap — not required for first editor ship.

**Rejected for v1 of this ADR**

- Third-party narrative middleware (Yarn/Ink) as **runtime** — adds dependency; compile-to-steps is enough if import is needed later.
- Storing only graph with **no** compiled artifact in repo — CI and [#87](https://github.com/miramocha/griddungeon-game/issues/87) tests need stable step arrays.

### 5. Milestones

| Milestone | Deliverable |
|-----------|-------------|
| **Launch ([#87](https://github.com/miramocha/griddungeon-game/issues/87))** | Hand-authored linear definitions (YAML or SO); **no graph editor required** |
| **Later — schema** | Enable `choice` in runner + content; S1 scenes stay linear unless redesign needs a branch |
| **Later — editor** | Graph asset + compile to `StoryEventDefinition`; migrate S1 drafts from markdown → graph export |
| **Later** | `Branch` condition nodes; shared shell with guided-tutorial graphs ([ADR 029](029-guided-tutorial.md)); import from markdown tables |

### 6. Implementation tracking (game repo)

When accepted, open a **game** issue (suggested title): *Editor: Story event graph compile pipeline* — depends on [#87](https://github.com/miramocha/griddungeon-game/issues/87) runner + step schema stable.

## Consequences

- **Design:** [story-events.md](../docs/02-systems/story-events.md) — add § Graph authoring (link this ADR); keep launch path linear.
- **ADR 028:** Stakeholder “branching deferred” = **runtime feature** deferred, not graph tooling forever.
- **Content:** Markdown drafts in `docs/03-content/story-events/` remain source of truth until editor lands; then graph is canonical, markdown optional export.
- **Tests:** Edit Mode tests continue to feed **compiled** step lists, not graph assets.

## Open questions

1. **Graph asset format** — nested SO per event vs one master “StoryEvents” graph with subgraphs per id.
2. **Condition language** — simple flag id + bool vs small expression DSL (keep minimal).
3. **Localization** — graph nodes edit `textKey` only; strings stay in string table ([ADR 028](028-story-visual-novel-events.md) recommendation).

## Related

- [ADR 031 — Floor event & pin condition graph](031-floor-event-pin-condition-graph.md) (placement / quest gating — orthogonal to step graphs)
- [ADR 028 — Story events (VN)](028-story-visual-novel-events.md)
- [ADR 029 — Guided tutorial](029-guided-tutorial.md)
- [story-events.md](../docs/02-systems/story-events.md)
- [Game #87 — StoryEventRunner + S1](https://github.com/miramocha/griddungeon-game/issues/87)
