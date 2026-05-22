# ADR 014 — MVP1 Exploration & Map

**Status:** Accepted  
**Date:** 2026-05-20

## Decisions (MVP1)

1. **Wall reveal:** On **bump**, stamp wall on the blocked edge. On **enter cell**, reveal **floor** + wall segments on any side of that cell that is solid (perimeter reveal). No full-room auto-fill without walking.
2. **Map UI:** Side panel always available in exploration; **fullscreen** map (`M`) — **movement keys pass through** (party can still step while map open); pan/zoom mouse on map panel; `M` or `Esc` closes.
3. **Gather nodes (MVP1):** **One-click instant loot** from node (no minigame). Marks node depleted for dive; full gather **minigame** in **MVP2**. Node icon on map when visited.
4. **Hub-return persistence** ([ADR 008](008-campaign-defaults.md) extended):
   - **Keep:** revealed map, open doors, looted chests, quest flags, **warp gate unlock** per stratum (`HubSaveData.UnlockedWarpGateStrata`).
   - **Reset:** FOE positions/patrol ([ADR 008](008-campaign-defaults.md)).
   - **Gather/fish nodes:** reset depleted state on hub return (MVP2 behavior; MVP1 stubs unchanged).
5. **Traps:** Out of MVP1 (no damage tiles).
6. **Encounter suppress:** Out of MVP1.
7. **Return to hub (exploration):** Only via **in-world triggers** — scripted **events**, **items** (e.g. Return thread), **exits / gates** (warp gates, side-dungeon exits), **stairs** (mouth `stairsUp` on stratum first floor), or **defeat** (party wipe → hub load). **Not** from exploration pause (`Esc` opens Resume / **Quit to title** only; see [input bindings](../docs/02-systems/input-bindings.md)). **Quit to title** does **not** write save data — progress since the last **inn save** is lost (hub and other designated save spots only; MVP1).

## Related

- [MVP1 spec](../docs/mvp1-spec.md)
- [Mapping](../docs/02-systems/mapping.md)
- [ADR 002](002-mapping-model.md)
