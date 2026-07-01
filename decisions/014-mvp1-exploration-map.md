---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - status/accepted
  - domain/exploration
  - domain/map
---
# ADR 014 — Exploration & Map

**Status:** Accepted  
**Date:** 2026-05-20

## Decisions

1. **Wall reveal:** On **bump**, stamp wall on the blocked edge. On **enter cell** or **in-place turn**, reveal **floor** + solid wall edges for cells in a **depth-1 facing cone** ahead of the party: at forward step `f`, lateral offsets `|L| ≤ f`; each column walks forward from `f = |L|` until a non-walkable cell (blocker included, then stop). Features (stairs, gather) stamp only on the party cell. No full-room auto-fill without walking.
2. **Map UI:** Side panel always available in exploration; **fullscreen** map (`M`) — **movement keys pass through** (party can still step while map open); pan/zoom mouse on map panel; `M` or `Esc` closes.
3. **Gather nodes At launch:** **One-click instant loot** from node (no minigame). Marks node depleted for dive; full gather **minigame** in **Optional**. Node icon on map when visited.
4. **Hub-return persistence** ([ADR 008](008-campaign-defaults.md) extended):
   - **Keep:** revealed map, open doors, looted chests, quest flags, **warp gate unlock** per stratum (`HubSaveData.UnlockedWarpGateStrata`).
   - **Reset:** FOE positions/patrol ([ADR 008](008-campaign-defaults.md)).
   - **Gather/fish nodes:** reset depleted state on hub return (MVP2 behavior; at launch stubs unchanged).
5. **Traps:** Out of at launch (no damage tiles).
6. **Encounter suppress:** Out of at launch.
7. **Return to hub (exploration):** Only via **in-world triggers** — scripted **events**, **items** (e.g. Return thread), **exits / gates** (warp gates, side-dungeon exits), **stairs** (gate `stairsUp` on stratum first floor), or **defeat** (party wipe → hub load). **Not** from exploration pause (`Esc` opens Resume / **Quit to title** only; see [input bindings](../docs/02-systems/input-bindings.md)). **Quit to title** does **not** write save data — progress since the last **inn save** is lost (hub and other designated save spots only; launch slice).

## Related

- [release scope](../docs/00-release-scope.md)
- [Mapping](../docs/02-systems/mapping.md)
- [Exploration UI](../docs/02-systems/exploration-ui.md) — `MapView` / pause bind lifecycle
- [ADR 002](002-mapping-model.md)
