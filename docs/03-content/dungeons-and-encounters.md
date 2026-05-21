# Dungeons & Encounters

Content structured like **Etrian Odyssey strata** — themed zones with multiple floors, FOE placements, and floor gimmicks.

## Stratum structure

```
Stratum 1: Emerald Grove (B1F–B5F) → Stratum boss
Stratum 2: Sand Ruins (B6F–B10F) → …
```

Each floor data file:

```
stratum_id, floor_id (B1F), theme_art, music, encounter_table,
foe_spawns[], trap_table, gather_nodes[], stairs, quests
```

## Floor design principles (EO)

1. **Looping paths** — shortcuts behind keys/FOE gates reward map literacy.
2. **FOE as puzzles** — block shortest route until party ready or map route around patrol.
3. **Gather nodes** — materials for synthesis on later floors.
4. **Safe-ish rooms** — lower encounter rate (not always zero).
5. **Landmarks** — unique art/audio cue; auto-mapped when visited.

## Example: Stratum 1 arc

| Floor | Theme | FOE teaching | Gimmick |
|-------|-------|--------------|---------|
| B1F | Forest entrance | None / 1 weak stationary FOE | Tutorial walls + stairs |
| B2F | Dense thicket | 2 FOEs, green tier | Key door loop |
| B3F | Stream crossing | First step-patrol FOE (`stepsPerMove: 4`) | Damage floor tiles optional |
| B4F | Old growth | Red-tier FOE guards chest | Gather: wood |
| B5F | Guardian hall | Stratum boss FOE | Boss room, stairs to Stratum 2 |

## Encounter types

| Type | Trigger | Design notes |
|------|---------|--------------|
| **Random** | Per-step roll | Table per floor; no FOE sprite |
| **FOE** | Grid entity contact | Authored position; patrol path optional |
| **Boss FOE** | Unique spawn | Stratum gate; higher rewards |
| **Event** | Tile script | Story fight, no flee |

## FOE authoring schema

```yaml
floor: B3F
foes:
  - id: forest_stalker
    cell: [12, 8]
    patrol: [[12,8], [12,9], [13,9]]
    stepsPerMove: 3
    tier: yellow
    group: [stalker]
  - id: ent_guard
    cell: [4, 15]
    tier: red
    group: [ent, sapling]
```

**Tier colors (EO-like):** green (easy), yellow (caution), red (avoid until ready).

## Random encounter table

```yaml
floor: B3F
rate: 0.12  # per step
entries:
  - weight: 50
    group: [forest_rabbit, forest_rabbit]
  - weight: 30
    group: [venomfly]
  - weight: 20
    group: [wood_owl, forest_rabbit]
```

## Traps & gathers

| Type | EO parallel |
|------|-------------|
| Damage tile | Slip roots, thorns |
| Gather | Chopping/mining points — respawn on return to hub |
| Chest | Loot; auto-marks on map when opened |

## Boss checklist

- [ ] Visible on map approach (room scale telegraph)
- [ ] Weakness discovery via Codex or Analysis
- [ ] Drops unlock stratum or synthesis tier
- [ ] FOE does not respawn until stratum reset rule defined

## FOE respawn rules (TBD)

| Model | Feel |
|-------|------|
| Respawn on hub return | EO-like farming control |
| One-time per save | More puzzle-like |
| Timer respawn | High grind |

**Proposal:** respawn when returning to hub and re-entering floor (EO common pattern).

## Content pipeline

1. Node graph on paper (rooms, FOE gates, stairs)
2. Blockout grid + place FOE entities
3. Playtest: exploration time vs fight time, red FOE deaths
4. Tune random rate so mapping isn't constant interruption

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [ADR 003 — FOE step patrol](../../decisions/003-foe-step-patrol.md)
- [02 — Combat](../02-systems/combat.md)
