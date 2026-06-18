# 02 — Dungeon Navigation

## Camera & presentation

- **First-person** blobber view (EO-style static or lightly animated corridor art per cell).
- **Facing:** four cardinals. **Move:** forward, backward, **strafe left**, **strafe right**, turn left, turn right.
- **Map visible** during exploration (side panel); fullscreen read-only view optional.

## Grid model

| Property | Value |
|----------|-------|
| Logic grid | **1 cell** = one walkable tile in `ExplorationFloor` (indices 0…19 per axis on launch floors) |
| World scale (FPV) | **`10` Unity units** per logic cell on XZ (`ExplorationGridMetrics.WorldUnitsPerCell`); see [floor art FPV](02-systems/floor-art-fpv.md#summary) |
| Coordinates | `(x, y, level)` + `facing` (N/E/S/W) — `level` is walkable height band in the floor ([ADR 019](../decisions/019-floor-verticality.md)) |
| Stratum floors | `B1F`, `B2F`, … per stratum (dungeon floor id, not height `level`) |
| Doors | Edge or cell flag; player marks on map when found |
| Special | Stairs (stratum / height), **jump pads**, chests, gather points, stratum boss room |

Authoring uses the same `(x, y)` axes as [dungeons & encounters — map legend](03-content/dungeons-and-encounters.md#map-legend-ascii-blockouts) (x west→east, y south→north; **N** = +y).

### Party pose vs grid coordinates

Exploration keeps **two layers**: grid state (rules, map, FOEs, encounters) and a **scene transform** (FPV camera / blobber motion). They must stay aligned; only the transform may lag during DOTween lerps ([ADR 001](../decisions/001-grid-movement.md)).

| Layer | Owner | What it stores |
|-------|--------|----------------|
| **Grid (authority)** | `DungeonExplorer` | `GridPosition Cell`, `FacingDirection Facing` — committed at **step/turn start** |
| **World pose (presentation)** | `Transform` on **`PartyPose`** (dev bootstrap) wired to `DungeonExplorer.m_poseRoot` | Unity position + Y rotation; tweened between committed grid states |

`PartyPose` is a **scene object name** for the pose root, not a separate game type. If `m_poseRoot` is unset, the explorer falls back to its own `Transform`.

**Grid → world**

| Grid | World (Unity) |
|------|----------------|
| `Cell.X` | `position.x` |
| `Cell.Y` | `position.z` (horizontal plane; grid **y** is not Unity **Y**) |
| `level` (when [ADR 019](../decisions/019-floor-verticality.md) lands) | Walkable **height band** for collision/map — distinct from per-cell **elevation steps** below |
| `cellElevationSteps` + `elevationStepUnits` | `DungeonExplorer.BindElevationY` sets `position.y` from authored floor steps ([floor editor § Elevation](02-systems/floor-editor.md)); `RefreshPose()` re-snaps after spawn, floor transition, and floor-art load |
| — | Flat floors: `position.y` = **0** when no elevation query is bound |

Mapping uses **integer cell indices** and a **corner anchor** (south-west corner of the cell on the floor plane) — **no half-cell centering offset**:

```
world.x = origin.x + cell.X * WorldUnitsPerCell
world.z = origin.z + cell.Y * WorldUnitsPerCell
```

launch default: `WorldUnitsPerCell = 10`, `origin = (0, 0, 0)` → cell `(3, 4)` is world `(30, 0, 40)`. Movement step distance is **10** units per forward/strafe cell ([ADR 001](../decisions/001-grid-movement.md), [ADR 018](../decisions/018-exploration-animation-speed.md) — Normal **0.32s** `OutQuad` step lerp).

**Facing → rotation**

| `FacingDirection` | Grid step (logic) | `m_poseRoot` Y rotation |
|-------------------|-------------------|-------------------------|
| North | +Y | 0° (toward +Z) |
| East | +X | 90° |
| South | −Y | 180° |
| West | −X | 270° |

Bump nudges use the same XZ axes as displacement (`dx` → world X, `dy` → world Z).

**During animation**

- Displacement: `Cell` updates **before** the step tween; `OnPartyEnteredCell` / FOE / encounter logic run at commit time.
- Turn: `Facing` updates **before** the turn tween; no step events.
- While `IsAnimating`, `m_poseRoot` may differ from `Cell`/`Facing`; input does not commit another action until the tween completes.

**Not pose-driven**

- `MapSystem`, `FoeSystem`, save, and combat entry use **`GridPosition`**, not `Transform.position`.
- Combat arena uses **slot transforms**, not grid world coords ([combat scene](02-systems/combat-scene.md)).

Runtime: `ExplorationWorldSpace.CellCornerToWorld` + `DungeonExplorer` pose tweens in `griddungeon-game` (`ExplorationWorldSpace.cs`, `DungeonExplorer.cs`, `ExplorationGridMetrics.cs` in Core).

### Verticality (Doom-style)

- Multiple **levels** can share the same `(x, y)`; each is a distinct cell.
- Party moves on one **walkable surface** at a time; **cannot walk under** upper floors / overhangs.
- **Level changes** only via stairs, ramps, jump pads, or explicit pits — not by normal strafe/forward into “empty air under a bridge.”
- Example jump pad: **+2 cells forward** (relative to facing), **+1 level up** — one landing step for FOE/encounter rules.

## Movement rules

1. **Forward** — Enter cell ahead; facing unchanged.
2. **Backward** — Enter cell behind; facing unchanged.
3. **Strafe left / right** — Enter adjacent cell to the left or right of current facing; facing unchanged. Same step rules as forward/back.
4. **Turn** — Rotate 90° in place; **no step events** (no encounter roll, no FOE step tick).
5. **Interact** — Open door, chest, gather, switch; may require facing.

All **displacement** moves (forward, back, strafe) count as one **party step** for FOE patrol and random encounters when entering a new cell.

## Step events (order)

On entering a **new cell** via forward, backward, or strafe:

1. **Auto-map** — chart floor tile ([mapping](02-systems/mapping.md)).
2. **FOE patrol** — increment floor step count; moving FOEs advance per [ADR 003](../decisions/003-foe-step-patrol.md); check collision.
3. **Trap** check.
4. **Random encounter** roll (stratum/floor table).
5. **Tile script** (message, teleport, etc.).

Turns in place skip steps 2–4 (no step counter increment).

## FOEs on the grid

- FOEs appear as **visible entities** in the dungeon (sprite/mesh) and on the map when in sight.
- **Contact** with FOE cell → FOE combat ([foe-encounters](02-systems/foe-encounters.md)); fight plays on **battle arena**, not in FPV cell ([combat scene](02-systems/combat-scene.md)).
- **Flee** from FOE fight: allowed if **1 cell back** (opposite facing) is walkable; **disabled** if backed to a wall ([ADR 011](../decisions/011-foe-flee-retreat.md)).
- **Strength cue** — color/icon tier vs average party level.
- **Patrol** — FOEs advance every N **party steps** (any displacement: forward, back, strafe); see [ADR 003](../decisions/003-foe-step-patrol.md). Stationary FOE = single-cell path.

Player tactics: wait for patrol gap, bait FOE to empty cells, or fight for XP/loot.

**Optional later:** FOEs move **1 grid per combat round** during fights ([ADR 005](../decisions/005-foe-combat-patrol.md)); may **[join the battle](02-systems/chain-foe-battle.md)** one at a time if they reach the party cell ([ADR 010](../decisions/010-chain-foe-battle.md)).

## Random encounters

- Rolled per step on eligible tiles (not in safe rooms if any).
- Rate from floor's **`RandomEncounterTableDefinition`** (`baseEncounterRate`); campaign may zero rate (e.g. S1 Act 1 B1F tutorial).
- Weighted rows pick an **`EncounterGroup`** id — not inline enemy lists.
- **Suppress** skills/items optional later.
- Distinct from FOE fights (different drop tables / XP).

## Interactables

- Doors, keys, one-way passages
- Chests (**launch**); gather / fish nodes (**optional** minigame → materials — [gathering & fishing](02-systems/gathering-and-fishing.md))
- **Stairs down (`v`)** — next floor in the **same stratum** (paired `stairsUp` on floor below).
- **Stairs up (`^`) on first floor of stratum (gate)** — not the same as mid-stratum stairs:
  - → **Hub** only (Exploration → Hub phase; EO “return to camp”).
- **Stairs up on B2F+** — previous floor in same stratum only.
- **Stratum 1:** no warp gate; new game starts on B1F intro path before hub ([campaign S1 intro](03-content/campaign/s1-intro.md)).
- **Return thread** item — instant hub once (consumable); does not replace gate stairs.
- **Hub return paths (locked):** events, items (Return thread), exits/gates, gate stairs, party **defeat** — not exploration pause ([ADR 014](../decisions/014-mvp1-exploration-map.md) §7, [input bindings](02-systems/input-bindings.md)).

## Party on the grid

- Party moves as **one anchor**; six **core** members are abstract until combat (summons/guests combat-only).
- Combat uses **3+3 core** plus **+1+1 aux** (summon/guest); see [summons & guests](02-systems/summons-and-guests.md).

## Feel & animation

- Short step lerp (~0.32s at **Normal** speed) via **DOTween**; logic commits at step start ([ADR 001](../decisions/001-grid-movement.md), [ADR 018](../decisions/018-exploration-animation-speed.md)).
- **Hold-to-repeat:** holding a displacement key walks one cell per lerp cycle; holding a turn key rotates 90° per turn lerp; no new commit while a step, turn, or bump lerp is in progress ([ADR 001](../decisions/001-grid-movement.md)).
- **Autopilot (optional):** map click → pathfind over **discovered** walkable tiles → auto-walk path; same step events as manual ([autopilot](02-systems/autopilot.md), [ADR 021](../decisions/021-autopilot-mvp2.md)).
- Bump feedback when movement blocked — **auto-stamp wall** on that edge ([mapping](02-systems/mapping.md)).

## Input

PC defaults: `W/S` forward/back, `A/D` strafe, `Q/E` turn, `Z` interact — see [input bindings](02-systems/input-bindings.md).

## Related docs

- [Input bindings](02-systems/input-bindings.md)
- [Mapping](02-systems/mapping.md)
- [ADR 001](../decisions/001-grid-movement.md)
- [ADR 019](../decisions/019-floor-verticality.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
- [Autopilot (optional)](02-systems/autopilot.md)
- [ADR 021](../decisions/021-autopilot-mvp2.md)
- [03 — Dungeons & encounters](03-content/dungeons-and-encounters.md)
