# Autopilot (MVP2)

**Scope:** MVP2 — not required for first playable ([release scope](../00-release-scope.md)).

> **Scope: Optional feature** — not required for initial release.

**Autopilot** pathfinds and walks the party along **already discovered** floor tiles so players skip manual stepping on routes they mapped earlier. EO uses **drawn paths**; Grid Dungeon uses **auto-reveal only** ([ADR 002](../../decisions/002-mapping-model.md)) — autopilot replaces drawn paths with routing on **revealed walkable** cells.

## Design goals

| Goal | How |
|------|-----|
| **Backtracking relief** | Click a destination on the map → party walks the shortest safe path over known ground |
| **Explored areas only** | Path nodes = **revealed floor** the party has charted; never route through fog/unrevealed cells |
| **No map drawing** | Destination pick + path overlay; no player-authored lines ([ADR 002](../../decisions/002-mapping-model.md)) |
| **Same step rules** | Each step on the path is a normal party step (FOE patrol, encounters, reveal) |
| **Fair stops** | Combat, blocked path, or cancel — not silent teleport |
| **MVP1 unchanged** | Manual grid + hold-to-repeat only ([ADR 001](../../decisions/001-grid-movement.md)) |

---

## Core flow (MVP2)

```
Player opens map (side or fullscreen)
  → LMB on revealed walkable cell (destination)
  → AutopilotController pathfinds on current floor `level`
      nodes = revealed walkable cells; edges = cardinal, respecting walls/doors
  → Preview path overlay on map (dashed)
  → Party walks path one displacement at a time (lerp per ADR 001)
  → Arrive at destination OR stop condition → clear overlay, manual control
```

---

## Pathfinding rules

| Rule | Detail |
|------|--------|
| **Graph** | Cells where `MapSystem` reports **revealed floor** and walkable on current `level` ([mapping](mapping.md)) |
| **Edges** | Cardinal adjacency; block on solid walls; **closed doors** block until opened (revealed open door = passable) |
| **Algorithm** | Shortest path (BFS or A*) on the subgraph above — implementation choice |
| **Start** | Party anchor cell |
| **Goal** | Clicked cell; must be revealed walkable; reject clicks on walls, fog, FOE icon-only, wrong `level` |
| **Multi-level** | MVP2: **same `level` only** — no path across stairs/jump pads (player walks vertical links manually) |
| **Repath** | If reveal changes mid-walk (new wall, door closes), **stop** with message; do not cut through newly invalid cells |
| **FOE cells** | Route **may** include cells that currently show a FOE icon — stepping there triggers contact as today (player accepts risk) |

**Not in scope:** routing through unrevealed tiles, teleport, or skipping step events.

---

## Movement along the path

For each path segment:

1. If next cell requires **facing change**, play **turn lerp** (no step events) then step.
2. Otherwise **displacement** (forward/strafe relative to facing) into next cell — one lerp, full step events.
3. Wait for lerp end before next segment ([ADR 001](../../decisions/001-grid-movement.md)).

Corners and “junctions” on the precomputed path are **not** stop points — only stops below apply.

---

## Stop conditions

| Condition | Behavior |
|-----------|----------|
| **Reached destination** | Stop; clear autopilot state |
| **Path no longer valid** | Wall/door block on planned next cell → stop + toast |
| **FOE contact** | Stop autopilot; enter FOE fight |
| **Random encounter** | Stop autopilot; enter fight |
| **Interactable on next cell** (not destination) | Stop **before** entering (chest, closed door, gather node, etc.) — player chooses `Space` |
| **Destination is interactable** | Stop **on** cell; player interacts manually |
| **Combat / hub / minigame** | Autopilot inactive; cancel if phase changes |
| Player **manual move/turn/interact**, new map click, **pause** | Cancel autopilot |
| `Esc` or **Cancel autopilot** | Cancel immediately |

---

## Step events

Every **displacement** on the path runs the normal exploration pipeline:

1. Auto-map reveal (may extend chart at path edge)  
2. FOE patrol ([ADR 003](../../decisions/003-foe-step-patrol.md))  
3. Trap (when traps ship)  
4. Random encounter  
5. Tile script  

**Turns** on path corners: turn lerp only — no FOE tick, no encounter ([ADR 001](../../decisions/001-grid-movement.md)).

---

## UI & feedback

| Element | Rule |
|---------|------|
| **Set destination** | `LMB` on revealed walkable cell while map visible (side or fullscreen) |
| **Path preview** | Dashed/highlight overlay on map for planned route before first step |
| **HUD** | `AUTOPILOT` label while walking; pulse on stop |
| **Stop reason** | Toast: `Arrived`, `Blocked`, `FOE!`, `Encounter`, `Interactable`, `Cancelled` |
| **Invalid click** | Brief hint: `Unknown tile` / `Not walkable` |
| **Settings (later)** | Optional: **avoid FOE cells** when pathfinding (reroute or refuse start) |

Map fullscreen still allows movement pass-through per [ADR 014](../../decisions/014-mvp1-exploration-map.md); autopilot cancel keys still work.

---

## Input (MVP2)

| Action | Default | Notes |
|--------|---------|-------|
| **Set autopilot destination** | `LMB` on map (revealed walkable) | Side panel or fullscreen map |
| **Cancel autopilot** | `Esc`, any move/turn/interact, or `LMB` on party cell | Immediate |

PC defaults: [ADR 021](../../decisions/021-autopilot-mvp2.md). Rebind when settings UI ships.

---

## Implementation ownership

| Piece | Owner |
|-------|--------|
| Path graph + A*/BFS | `AutopilotController` (Runtime) or Core helper fed by `MapReveal` snapshot |
| Step commit + lerp | `DungeonExplorer` |
| Map click → goal | `MapView` / exploration presenter → `AutopilotController` |
| Overlay | `MapView` |

Add class sketch to [05 — Class design MVP1](../05-class-design.md) when implementing.

---

## MVP1 vs MVP2

| Item | MVP1 | MVP2 |
|------|------|------|
| Manual WASD + hold-to-repeat | Yes | Yes |
| Map click → pathfind to discovered tile | No | **Yes** |
| Path overlay on map | No | Yes |
| Teleport / unrevealed routing | No | No |

---

## Related

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [02 — Mapping](mapping.md)
- [Input bindings](input-bindings.md)
- [ADR 001 — Grid movement](../../decisions/001-grid-movement.md)
- [ADR 002 — Mapping model](../../decisions/002-mapping-model.md)
- [ADR 021 — Autopilot MVP2](../../decisions/021-autopilot-mvp2.md)
- [Release scope](../00-release-scope.md)
