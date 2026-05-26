# ADR 025 — Campaign exploration target (per-stratum policy)

**Status:** Proposed (stub)  
**Date:** 2026-05-22  
**Triggers implementation:** Stratum 2+ hub entry, warp-gate spawn rules, or `ExplorationPhaseController` must stop calling `S1CampaignResolver` directly.

## Context

MVP1 exploration spawn and floor transitions are implemented in **`S1CampaignResolver`** and carried as **`S1ExplorationTarget`** (`stratumId`, `floorId`, `floorKey`, `spawnCell`, `spawnFacing`). The struct fields are already generic; the **`S1` prefix** marks **campaign policy** (intro spawn, gate → hub, tutorial gates, B1F↔B2F↔B3F stair pairing), not a lack of `stratumId` on the DTO.

Macro flow already anticipates **different hub → exploration rules per stratum**:

- [ADR 017](017-game-phase-controller.md) — S1 **B1F gate** after Act 2; **S2+ warp gate**; new game Act 1 intro on `s1_B1F`.
- [Hub & services — macro loop](../docs/02-systems/hub-and-services.md) — “spawn rule per stratum.”
- [ADR 014](014-mvp1-exploration-map.md) — `HubSaveData.UnlockedWarpGateStrata` for stratum warp gates.
- [Core assembly improvement plan](../docs/plans/core-assembly-improvement-plan.md) — add `Core/Campaign/S2/` (or similar); do not grow `S1CampaignResolver` with unrelated acts.

**Side dungeons** ([ADR 022](022-side-dungeons-mvp3.md)) use separate save keys and hub entry; they share **Exploration** phase but are **out of scope** for this ADR’s stratum resolver split.

## Decision (target shape — not locked until triggered)

### 1. Neutral spawn DTO (Core)

| Today (MVP1) | Target |
|--------------|--------|
| `S1ExplorationTarget` | Rename or alias to **`ExplorationTarget`** in `GridDungeon.Core` — same fields, no S1-specific members. |

`ExplorationPhaseController`, `MapSystem`, and save resume paths consume **`ExplorationTarget` only**; they do not embed stratum story rules.

### 2. Per-stratum policy (Core, grouped folders)

| Stratum / mode | Policy owner (proposed) | Examples |
|----------------|-------------------------|----------|
| S1 | `S1CampaignResolver` (existing) | Intro `(4,2)`, gate `(10,11)`, B2F tutorial gates, within-stratum stairs |
| S2+ | `S2CampaignResolver` or `Core/Campaign/S2/*` | Warp-gate spawn, stratum entry floor, Synchro on hub exit per content |
| Side dungeon (MVP3) | Separate resolver / `HubController.EnterSideDungeon` | Composite keys `sd##_F#`; hub-only exit ([ADR 022](022-side-dungeons-mvp3.md)) |

**Not** a single god `CampaignResolver` with `switch (stratumId)` spanning all acts — mirror [improvement plan §0.2](../docs/plans/core-assembly-improvement-plan.md).

### 3. Dispatch from exploration phase (Runtime)

`ExplorationPhaseController` (or `GameState`) resolves **active stratum / map kind**, then delegates:

- `ResolveExplorationTarget(save, fromPhase)`
- `CanDescendStairs` / `CanAscendStairs` / `TargetForStairsDown` / `TargetForStairsUp`
- `CanAscendToHub` (surface exit — S1 gate only today)
- Walkability / encounter-rate overrides (today: `S1ExplorationWalkability` + resolver helpers)

MVP1 may keep **direct `S1CampaignResolver` calls** until a second stratum ships; this ADR records the intended seam.

### 4. Optional interface (defer)

Introduce something like **`ICampaignExplorationPolicy`** (or stratum-keyed registry) **only when** two or more policies exist and tests need swapping — YAGNI for S1-only MVP1.

## MVP1 (unchanged)

- Keep **`S1ExplorationTarget`** + **`S1CampaignResolver`** names unless a rename ticket is explicitly scoped.
- No new abstraction layer required for Stratum 1 vertical slice ([#15](https://github.com/miramocha/griddungeon-game/issues/15)).
- Within-stratum stairs (e.g. B2F `stairsUp` → B1F) stay in `S1CampaignResolver`; B1F `stairsUp` → hub remains special-cased.

## Consequences (when implemented)

- [05 — Class design MVP1](../docs/05-class-design-mvp1.md) — update `ExplorationPhaseController` sketch and campaign types.
- [game phase](../docs/02-systems/game-phase.md) — hub → explore table references policy dispatch, not only S1.
- [improvement plan](../docs/plans/core-assembly-improvement-plan.md) — link this ADR from §0.2 / §1.1 audit row for `Core/Campaign/`.
- **Tests:** per-stratum fixtures under `Tests/GameFlow/` (e.g. `S1CampaignResolverTests`, future `S2CampaignResolverTests`).

## Open questions

- [ ] Single registry on `GameState` vs inject policy per active stratum at hub leave.
- [ ] Whether `ExplorationMapKind` (stratum vs side dungeon) lives on the DTO or parallel to `ExplorationStateSave` only ([ADR 022](022-side-dungeons-mvp3.md)).
- [ ] Shared stair-pairing helper vs duplicated constants per stratum floor graph.

## Related

- [ADR 017 — Game phase controller](017-game-phase-controller.md)
- [ADR 014 — MVP1 exploration & map](014-mvp1-exploration-map.md)
- [ADR 022 — Side dungeons MVP3](022-side-dungeons-mvp3.md)
- [Core assembly improvement plan](../docs/plans/core-assembly-improvement-plan.md)
- [Campaign S1 intro](../docs/03-content/campaign/s1-intro.md)
- [Hub & services](../docs/02-systems/hub-and-services.md)
