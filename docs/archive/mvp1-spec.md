---
tags:
  - path/docs/archive
  - type/archive
  - scope/required
  - status/archived
---
> **Archived** — Superseded by [release scope](../00-release-scope.md) and the [project board](https://github.com/users/miramocha/projects/3). **MVP1/MVP2/MVP3** in filenames and ADRs mean **required/optional** at decision time.

# MVP1 implementation spec (archive)

This checklist was the single source for the **first playable** (2025–2026). **Do not update** for new work.

## Use instead

| Need | Doc |
|------|-----|
| Required / optional / later scope | [00 — Release scope](../00-release-scope.md) |
| Issue status and priority | [Codename: GridDungeon (project #3)](https://github.com/users/miramocha/projects/3) — `required` / `optional` labels |
| System rules | `docs/02-systems/*` |
| Content (S1, enemies, skills) | `docs/03-content/*` |
| Locked exploration rules | [ADR 014](../../decisions/014-mvp1-exploration-map.md) |
| Locked combat rules | [ADR 015](../../decisions/015-mvp1-combat.md) |
| Player-facing loop | [01 — Core loop](../01-core-loop.md), [S1 intro](../03-content/campaign/s1-intro.md) |
| Tuning constants (data-only) | [Release scope — Tuning](../00-release-scope.md#tuning-locked-structure) |

## Historical snapshots

- [S1 floor layouts (draft)](mvp1-s1-floor-layouts-draft.md) — ASCII blockouts; game `ExplorationFloor` assets are iteration authority until lock
- Pull wave labels **``pull-w01`–`pull-w08`** — legacy implementation sequencing; see git history before 2026-06-14 for the full wave table

Full checklist text preserved in git history (commit before this stub on `docs/drop-mvp1-terminology`).
