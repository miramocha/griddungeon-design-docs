# 02 — Dungeon Navigation

## Camera & presentation

- **First-person** blobber view (EO-style static or lightly animated corridor art per cell).
- **Facing:** four cardinals. **Move:** forward, backward, **strafe left**, **strafe right**, turn left, turn right.
- **Map visible** during exploration (side panel); fullscreen read-only view optional.

## Grid model

| Property | Value |
|----------|-------|
| Cell size | 1 unit = 1 cell |
| Coordinates | `(x, y, level)` + `facing` (N/E/S/W) — `level` is walkable height band in the floor ([ADR 019](../decisions/019-floor-verticality.md)) |
| Stratum floors | `B1F`, `B2F`, … per stratum (dungeon floor id, not height `level`) |
| Doors | Edge or cell flag; player marks on map when found |
| Special | Stairs (stratum / height), **jump pads**, chests, gather points, stratum boss room |

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
- Rate varies by floor; **Suppress** skills/items optional later.
- Distinct from FOE fights (different drop tables / XP).

## Interactables

- Doors, keys, one-way passages
- Chests (**MVP1**); gather / fish nodes (**MVP2** minigame → materials — [gathering & fishing](02-systems/gathering-and-fishing.md))
- Stairs up/down (stratum transitions)
- **Return thread** item — teleport party to hub once (consumable, EO Ariadne analogue)

## Party on the grid

- Party moves as **one anchor**; six **core** members are abstract until combat (summons/guests combat-only).
- Combat uses **3+3 core** plus **+1+1 aux** (summon/guest); see [summons & guests](02-systems/summons-and-guests.md).

## Feel & animation

- Short step lerp (~0.28s at **Normal** speed) via **DOTween**; logic commits at step start ([ADR 001](../decisions/001-grid-movement.md), [ADR 018](../decisions/018-exploration-animation-speed.md)).
- **Hold-to-repeat:** holding a displacement key walks one cell per lerp cycle; holding a turn key rotates 90° per turn lerp; no new commit while a step, turn, or bump lerp is in progress ([ADR 001](../decisions/001-grid-movement.md)).
- Bump feedback when movement blocked — **auto-stamp wall** on that edge ([mapping](02-systems/mapping.md)).

## Input

PC defaults: `W/S/A/D` move, `Q/E` turn, `Space` interact — see [input bindings](02-systems/input-bindings.md).

## Related docs

- [Input bindings](02-systems/input-bindings.md)
- [Mapping](02-systems/mapping.md)
- [ADR 001](../decisions/001-grid-movement.md)
- [ADR 019](../decisions/019-floor-verticality.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
- [03 — Dungeons & encounters](03-content/dungeons-and-encounters.md)
