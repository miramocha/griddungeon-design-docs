# Autopilot

**Scope:** Optional — [release scope](../00-release-scope.md).

> **Scope: Optional feature** � not required for initial release.

**Autopilot** pathfinds and walks the party along **already discovered** floor tiles so players skip manual stepping on routes they mapped earlier. EO uses **drawn paths**; Grid Dungeon uses **auto-reveal only** ([ADR 002](../../decisions/002-mapping-model.md)) � autopilot replaces drawn paths with routing on **revealed walkable** cells.

## Design goals

| Goal | How |
|------|-----|
| **Backtracking relief** | Click a destination on the map ? party walks the shortest safe path over known ground |
| **Explored areas only** | Path nodes = **revealed floor** the party has charted; never route through fog/unrevealed cells |
| **No map drawing** | Destination pick + path overlay; no player-authored lines ([ADR 002](../../decisions/002-mapping-model.md)) |
| **Same step rules** | Each step on the path is a normal party step (FOE patrol, encounters, reveal) |
| **Fair stops** | Combat, blocked path, or cancel � not silent teleport |
| **Launch unchanged** | Manual grid + hold-to-repeat only ([ADR 001](../../decisions/001-grid-movement.md)) |

---

## Core flow (optional)

```
Player opens map (side or fullscreen)
  ? LMB on revealed walkable cell (destination)
  ? AutopilotController pathfinds on current floor `level`
      nodes = revealed walkable cells; edges = cardinal, respecting walls/doors
  ? Preview path overlay on map (dashed)
  ? Party walks path one displacement at a time (lerp per ADR 001)
  ? Arrive at destination OR stop condition ? clear overlay, manual control
```

---

## Pathfinding rules

| Rule | Detail |
|------|--------|
| **Graph** | Cells where `MapSystem` reports **revealed floor** and walkable on current `level` ([mapping](mapping.md)) |
| **Edges** | Cardinal adjacency; block on solid walls; **closed doors** block until opened (revealed open door = passable) |
| **Algorithm** | Shortest path (BFS or A*) on the subgraph above � implementation choice |
| **Start** | Party anchor cell |
| **Goal** | Clicked cell; must be revealed walkable; reject clicks on walls, fog, FOE icon-only, wrong `level` |
| **Multi-level** | MVP2: **same `level` only** � no path across stairs/jump pads (player walks vertical links manually) |
| **Repath** | If reveal changes mid-walk (new wall, door closes), **stop** with message; do not cut through newly invalid cells |
| **FOE cells** | Route **may** include cells that currently show a FOE icon � stepping there triggers contact as today (player accepts risk) |

**Not in scope:** routing through unrevealed tiles, teleport, or skipping step events.

---

## Movement along the path

For each path segment:

1. If next cell requires **facing change**, play **turn lerp** (no step events) then step.
2. Otherwise **displacement** (forward/strafe relative to facing) into next cell � one lerp, full step events.
3. Wait for lerp end before next segment ([ADR 001](../../decisions/001-grid-movement.md)).

Corners and �junctions� on the precomputed path are **not** stop points � only stops below apply.

---

## Stop conditions

| Condition | Behavior |
|-----------|----------|
| **Reached destination** | Stop; clear autopilot state |
| **Path no longer valid** | Wall/door block on planned next cell ? stop + toast |
| **FOE contact** | Stop autopilot; enter FOE fight |
| **Random encounter** | Stop autopilot; enter fight |
| **Interactable on next cell** (not destination) | Stop **before** entering (chest, closed door, gather node, etc.) � player chooses `Space` |
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

**Turns** on path corners: turn lerp only � no FOE tick, no encounter ([ADR 001](../../decisions/001-grid-movement.md)).

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

## Input (optional)

| Action | Default | Notes |
|--------|---------|-------|
| **Set autopilot destination** | `LMB` on map (revealed walkable) | Side panel or fullscreen map |
| **Cancel autopilot** | `Esc`, any move/turn/interact, or `LMB` on party cell | Immediate |

PC defaults: [ADR 021](../../decisions/021-autopilot-mvp2.md). Rebind when settings UI ships.

---

## Implementation ownership (planned)

| Piece | Owner |
|-------|--------|
| Path graph + A*/BFS | Split across Core + Runtime � see **Implementation (shipped)** below |
| Step commit + lerp | `DungeonExplorer` |
| Map click ? goal | `ExplorationMapCoordinator` ? `AutopilotController` |
| Overlay | `MapGridPaintController` (BEM path/cursor/destination classes) |

---

## Implementation (shipped)

**Game repo:** merged [#248](https://github.com/miramocha/griddungeon-game/pull/248) ([`MapPathfinder`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/Core/Simulators/MapPathfinder.cs), [`ExplorationPathGraph`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/Runtime/Map/ExplorationPathGraph.cs), [`AutopilotPathWalker`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/Core/Exploration/AutopilotPathWalker.cs), [`AutopilotController`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/Runtime/Exploration/AutopilotController.cs)).

**Developer deep dive:** [04 � Dev: Autopilot pathfinding](../04-dev/autopilot-pathfinding.md).

### Type ownership

| Type | Assembly | Responsibility |
|------|----------|----------------|
| **`MapPathfinder`** | `GridDungeon.Core` | Generic **A\*** on a cardinal grid: injectable node/edge predicates, Manhattan heuristic, uniform step cost, binary min-heap open set. No `MapSystem` / floor knowledge. |
| **`ExplorationPathGraph`** | `GridDungeon.Runtime` | Builds exploration predicates from `MapSystem` + `ExplorationFloor` + campaign save (`S1ExplorationWalkability`, walls, doors) and calls `MapPathfinder.TryFindPath`. |
| **`AutopilotPathWalker`** | `GridDungeon.Core` | Given a path + `pathIndex`, returns the next **turn** or **step** action (`AutopilotWalkerAction`) for `DungeonExplorer` � shortest arc (left vs right). |
| **`AutopilotController`** | `GridDungeon.Runtime` | State machine (`Idle` ? `Selecting` ? `Walking` / `Suspended`), destination validation, pathfind orchestration, overlay events, combat suspend/resume, walker dispatch on animation complete. |

UI wiring (not pathfinding): `ExplorationMapCoordinator` owns `AutopilotController`; `ExpandedMapDestinationSelection` handles expanded-map pointer + arrow cursor; `MapGridPaintController.SetAutopilotOverlay` paints path/cursor/destination.

### A* algorithm (`MapPathfinder`)

| Detail | Shipped behavior |
|--------|------------------|
| **Neighborhood** | 4 cardinal offsets only |
| **Edge cost** | Uniform **1** per step (`gScore`) |
| **Heuristic** | **Manhattan** distance to goal (`|?x| + |?y|`) � admissible on cardinal grid |
| **Open set** | **Binary min-heap** keyed by `f = g + h`; tie-break by `h`, then `X`, then `Y` |
| **Closed set** | `HashSet<GridPosition>`; stale heap entries skipped on pop |
| **Predicates** | `Func<GridPosition, bool> isNodePassable`; `Func<GridPosition, GridPosition, bool> canTraverseEdge(from, to)` |
| **Output** | `IReadOnlyList<GridPosition>` from **start** (index 0) through **goal** (last index), inclusive |
| **Trivial path** | `start == goal` ? single-cell path (destination pick rejects party cell before walk) |

### Graph rules (`ExplorationPathGraph`)

| Layer | Rule |
|-------|------|
| **Nodes** | `map.IsVisited(cell)` **and** `S1ExplorationWalkability.IsWalkable(floor, cell, campaign, floorKey)` (tutorial gates, campaign flags) |
| **Edges** | Cardinal step only; reject if `ExplorationFloorLayout.IsSolidEdge(floor, from, side)` |
| **Revealed walls** | Block when `map.GetWalls(from)` includes the step-facing `WallMask` |
| **Doors** | **Closed** door on **either** endpoint blocks the edge (`FeatureType.Door` + `!IsInteracted`); opened door is passable |
| **FOE / encounters** | Not in graph � routed cells may contain FOE icons; contact runs normal step pipeline |

Same-level only; no stairs/jump-pad edges in the path graph (matches MVP2 spec).

### Path index semantics (`AutopilotPathWalker` + `AutopilotController`)

The path list is **inclusive** of start and goal. Walking does **not** re-path each step.

| Moment | `pathIndex` | Meaning |
|--------|-------------|---------|
| After `TryConfirmDestination` | `1` when `path.Count > 1`, else `0` | Next cell to enter is `path[pathIndex]` (index `0` is current party cell at confirm time) |
| Each `OnExplorerAnimationCompleted` while `Walking` | Increment when `m_explorer.Cell == path[pathIndex]` | Party has **arrived** on the indexed waypoint |
| `GetNextAction(path, pathIndex, cell, facing)` | Reads `path[pathIndex]` | Returns `TurnLeft` / `TurnRight` / `StepForward` toward that cell, or `Done` if already there / invalid gap |
| Walk complete | � | `pathIndex >= path.Count` **or** `m_explorer.Cell == m_savedDestination` ? `Idle`, overlay cleared |

Turns use `DungeonExplorer.TryTurnLeft` / `TryTurnRight`; steps use `TryStepForward`. `MovementAcceptance.Ignored` **cancels** autopilot (no toast yet).

### Shipped UX vs MVP2 spec (deviations)

| MVP2 spec | Shipped (expanded-map slice) |
|-----------|------------------------------|
| `LMB` destination on **side or fullscreen** map | **Expanded map only** � **Z** arms path mode (`TabbedPickerRailHints.ExplorationMapAutopilotSelect`); arrow keys move cursor; **Z Confirm** or **click** sets destination. Side minimap has no autopilot pick yet. |
| Cancel on **combat** | **Suspend + resume** � `SuspendForCombat` saves destination; `TryResumeAfterCombat` re-paths from post-fight cell (or `Cancel` if unreachable / already at goal). FOE/random encounter still stops walk via combat entry. |
| Stop toasts (`Arrived`, `Blocked`, �) | **Not shipped** � silent cancel or idle on complete |
| Stop **before** interactable on path (not destination) | **Not shipped** � walker steps into chests / gather nodes unless movement is blocked |
| **Avoid FOE cells** setting | **Not shipped** � shortest revealed path may cross FOE tiles |
| Mid-walk **repath** when map changes | **Not shipped** � blocked next step cancels; no replan or message |
| `AUTOPILOT` HUD label / pulse | Overlay classes on map cells only (`MapAutopilotCellClasses`) |

### Automated tests

Edit Mode fixtures ([game `Assets/Tests/README.md`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Tests/README.md)):

| Fixture | Domain | Covers |
|---------|--------|--------|
| `MapPathfinderTests` | `Map` | Open grid shortest path, wall detour, unreachable goal |
| `ExplorationPathGraphTests` | `Map` | Unrevealed shortcut skipped, closed vs open door, B1F tutorial blocker + campaign flag |
| `AutopilotPathWalkerTests` | `Exploration` | Step when aligned; shorter turn arc |
| `AutopilotControllerTests` | `Exploration` | Select toggle, confirm ? walk, combat suspend/resume, manual cancel |
| `ExpandedMapDestinationSelectionTests` | `UI` | Expanded-map cursor move + confirm |
| `ExplorationMapCoordinatorTests` | `UI` | M-toggle minimap retract; pause menu minimap retract |
| `ExplorationInputActionsTests` | `UI` | `Pause` stays enabled while pause menu open (Esc dismiss) |
| `HeldInputRepeatTests` | `UI` | Hold-repeat pulse / timer drivers |

---

## Launch vs optional

| Item | Launch | MVP2 |
|------|------|------|
| Manual WASD + hold-to-repeat | Yes | Yes |
| Map click ? pathfind to discovered tile | No | **Yes** |
| Path overlay on map | No | Yes |
| Teleport / unrevealed routing | No | No |

---

## Related

- [04 � Dev: Autopilot pathfinding](../04-dev/autopilot-pathfinding.md) � A*, graph rules, API, tests
- [02 � Dungeon navigation](../02-dungeon-navigation.md)
- [02 � Mapping](mapping.md)
- [Input bindings](input-bindings.md)
- [ADR 001 � Grid movement](../../decisions/001-grid-movement.md)
- [ADR 002 � Mapping model](../../decisions/002-mapping-model.md)
- [ADR 021 � Autopilot MVP2](../../decisions/021-autopilot-mvp2.md)
- [Release scope](../00-release-scope.md)
