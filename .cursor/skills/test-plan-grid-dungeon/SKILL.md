---
name: test-plan-grid-dungeon
description: >-
  Writes Grid Dungeon GitHub/PR test plans with consistent structure (automated
  Edit Mode paths, DevBootstrap manual tables, sign-off, N/A deferrals). Use when
  creating or updating test plans for issues, PRs, handoff, or ticket close-out.
---

# Grid Dungeon test plans

## When to use

- Opening or closing a **griddungeon-game** or **design-docs** issue tied to implementation
- User asks for a **test plan**, **manual QA steps**, or **verification checklist**
- Updating a plan after **user test feedback** (mark verified, N/A, defer to another issue)

Complements [.cursor/rules/ticket-test-documentation.mdc](../../rules/ticket-test-documentation.mdc) (always-on reminder). This skill owns **format and workflow**.

## Rules

1. **Do not invent results** — unchecked until the user or CI reports green.
2. **No Unity CLI batch tests** while the Editor may be open — ask the user to run Test Runner ([unity-no-cli-tests-while-editor-open.mdc](../../rules/unity-no-cli-tests-while-editor-open.mdc)).
3. **Post to GitHub issue comment** by default; mirror under `## Test plan` on the PR.
4. Mark steps **N/A** with reason + follow-up issue (e.g. instant enemy AI → #35), not as failures.
5. Use **tables** for manual steps: `| Step | Action | Expected |` with stable step numbers across edits.

## Workflow

1. Read the issue/PR scope and touched domains (`Combat`, `Exploration`, `Map`, `Foe`, `GameFlow`).
2. Pick a preset from [template.md](template.md) (full skeleton) or [examples.md](examples.md).
3. Fill **Setup**, **Automated** (Test Runner tree paths), **Manual** sections (A/B…), **Regressions**, **Spec/ADRs**.
4. Post via `gh issue comment` or edit existing test-plan comment (`gh api` PATCH).
5. After user feedback: update sign-off date, check boxes, add **Notes** for N/A/deferred.

## Defaults (unless the ticket overrides)

| Topic | Default |
|-------|---------|
| Scene | `DevBootstrap.unity` — regenerate **GridDungeon → Scenes → Create Dev Bootstrap** |
| Phase keys | **F1** Hub, **F2** Exploration, **F3** Combat, **F4** flee, **F6** party ready, **F7** stratum entry |
| Exploration timing | Normal: step **0.28s**, turn **0.26s** ([ADR 018](../../decisions/018-exploration-animation-speed.md)) |
| F3 dev roster | 2 cores + slime when party empty — [game README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/README.md) |
| Combat highlight | Core command pick → **party roster**, not AGI strip ([combat.md](../../docs/02-systems/combat.md#turn-order-strip-agi-queue-ui)) |
| Edit Mode tree | `Tests → <Domain> → <Fixture>` — [Assets/Tests/README.md](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md) |

## Section letters (manual primary)

Use one block per feature area; keep numbering **global** across the plan (e.g. A1 steps 1–6, A2 steps 7–10):

| Block | Typical scope |
|-------|----------------|
| **A1** | Phase visibility / HUD show-hide |
| **A2** | Domain-specific UI (strip, map, hub panel) |
| **A3** | Input / commands / keyboard parity |
| **A4** | Data display (HP, labels, save) |
| **A5–A6** | Placeholders, dev HUD coexist |
| **B** | Short cross-phase regressions (~5 min) |

## Sign-off block

Always end with a dated checklist (copy from [template.md](template.md)). Separate **verified** date from **pending** Edit Mode line.

## Resources

- Full copy-paste template: [template.md](template.md)
- Combat HUD example (issue #34 shape): [examples.md](examples.md)
