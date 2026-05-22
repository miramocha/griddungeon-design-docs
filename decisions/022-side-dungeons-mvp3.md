# ADR 022 — Side dungeons (MVP3)

**Status:** Accepted (MVP3 scope)  
**Date:** 2026-05-21

## Context

The EO-style loop uses **strata** as the main campaign vertical slice ([dungeons & encounters](../docs/03-content/dungeons-and-encounters.md)). Design needs **optional grid zones** outside stratum progression — full exploration and combat, entered from the **hub menu**, without warp gates or inter-stratum mouth stairs.

## Decision

1. **Macro phases unchanged** — side dungeons use existing **Exploration** and **Combat** phases ([ADR 017](017-game-phase-controller.md)); no fourth game phase.
2. **Separate hub entry** — `HubController.EnterSideDungeon(locationId, floorId)`; **do not** overload `LeaveHub(stratumId, floorId)` for side content.
3. **Save / map keys** — composite key `{locationId}_{floorId}` (e.g. `sd01_F1`), distinct from stratum keys (`s1_B1F`). `ExplorationStateSave` records `ExplorationMapKind` + `locationId` + `floorId`.
4. **Exit target** — in-dungeon `stairsUp` / exit features return to **Hub only** (no `PreviousStratumDeepest`).
5. **Unlock** — quest / story flag / milestone; **not** `HubSaveData.UnlockedFloors` (stratum-only).
6. **Authoring** — reuse floor tile/FOE/encounter data shape from `StratumFloor`; MVP3 may add `ExplorationMapKind` or `SideDungeonDefinition` in `ContentDatabase` without changing MVP1 locked IDs.
7. **FOE / map persistence** — same as labyrinth: map reveal persists; FOEs respawn on hub return + re-entry ([ADR 008](008-campaign-defaults.md)).

## Consequences

- [Side dungeons](../docs/02-systems/side-dungeons.md) is the rules authority.
- [Hub & services](../docs/02-systems/hub-and-services.md), [game phase](../docs/02-systems/game-phase.md), [01 — Core loop](../docs/01-core-loop.md) gain MVP3 cross-links.
- [05 — Class design MVP1](../docs/05-class-design-mvp1.md) appendix sketches API/save only — MVP1 implementation unchanged.
- `griddungeon-game`: implement in MVP3 milestone after MVP2 material loop.

## Related

- [Release scope — MVP3](../docs/00-release-scope.md)
- [ADR 017 — Game phase controller](017-game-phase-controller.md)
- [ADR 008 — Campaign defaults](008-campaign-defaults.md)
