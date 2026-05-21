# 02 — Dungeon Navigation

## Camera & presentation

- **First-person** blobber view (EO-style static or lightly animated corridor art per cell).
- **Facing:** four cardinals. **Move:** forward, backward, **strafe left**, **strafe right**, turn left, turn right.
- **Map visible** during exploration (side panel); fullscreen read-only view optional.

## Grid model

| Property | Value |
|----------|-------|
| Cell size | 1 unit = 1 cell |
| Coordinates | `(x, y)` + `facing` (N/E/S/W) |
| Floors | `B1F`, `B2F`, … per stratum |
| Doors | Edge or cell flag; player marks on map when found |
| Special | Stairs, chests, gather points, stratum boss room |

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
- **Contact** with FOE cell → combat (EO: fight or be caught).
- **Strength cue** — color/icon tier vs average party level.
- **Patrol** — FOEs advance every N **party steps** (any displacement: forward, back, strafe); see [ADR 003](../decisions/003-foe-step-patrol.md). Stationary FOE = single-cell path.

Player tactics: wait for patrol gap, bait FOE to empty cells, or fight for XP/loot.

**Optional later:** During combat, FOEs may still move **1 grid per combat round** on the labyrinth ([ADR 005](../decisions/005-foe-combat-patrol.md)). Party cell is frozen until the fight ends; no mid-battle FOE join unless chain battles are added later.

## Random encounters

- Rolled per step on eligible tiles (not in safe rooms if any).
- Rate varies by floor; **Suppress** skills/items optional later.
- Distinct from FOE fights (different drop tables / XP).

## Interactables

- Doors, keys, one-way passages
- Chests, mining/gather nodes (materials for synthesis)
- Stairs up/down (stratum transitions)
- **Return thread** item — teleport party to hub once (consumable, EO Ariadne analogue)

## Party on the grid

- Party moves as **one anchor**; six **core** members are abstract until combat (summons/guests combat-only).
- Combat uses **3+3 core** plus **+1+1 aux** (summon/guest); see [summons & guests](02-systems/summons-and-guests.md).

## Feel & animation

- Short step lerp (~0.2s); logic commits at step start ([ADR 001](../decisions/001-grid-movement.md)).
- Bump feedback when movement blocked — **auto-stamp wall** on that edge ([mapping](02-systems/mapping.md)).

## Related docs

- [Mapping](02-systems/mapping.md)
- [ADR 001](../decisions/001-grid-movement.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
- [03 — Dungeons & encounters](03-content/dungeons-and-encounters.md)
