# Dungeons & Encounters

Content structured like **Etrian Odyssey strata** — themed zones with multiple floors, FOE placements, and floor gimmicks.

## Stratum structure

```
Stratum 1: Fallen District (B1F–B5F) → Stratum boss
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
3. **Gather / fish nodes** — **MVP2** minigames → materials for synthesis ([gathering & fishing](../02-systems/gathering-and-fishing.md)).
4. **Safe-ish rooms** — lower encounter rate (not always zero).
5. **Landmarks** — unique art/audio cue; auto-mapped when visited.

## Example: Stratum 1 arc

| Floor | Theme | FOE teaching | Gimmick |
|-------|-------|--------------|---------|
| B1F | Outskirts gate | None / 1 weak stationary FOE | Tutorial walls + stairs |
| B2F | Collapsed avenues | 2 FOEs, green tier; 1 step-patrol (`stepsPerMove: 4`) | Key door loop |
| B3F | Flooded underpass | Yellow-tier patrol FOE, narrower paths | Damage floor tiles (post-MVP1) |
| B4F | Ruined plaza | Red-tier FOE guards chest | **MVP2:** salvage pile + flooded cistern |
| B5F | Civic fortress | Stratum boss FOE | Boss room, stairs to Stratum 2 |

## Encounter types

| Type | Trigger | Design notes |
|------|---------|--------------|
| **Random** | Per-step roll | Table per floor; no FOE sprite |
| **FOE** | Grid entity contact | Authored position; patrol path optional; flee → 1 cell back ([foe-encounters](../02-systems/foe-encounters.md)) |
| **Boss FOE** | Unique spawn | Stratum gate; higher rewards |
| **Event** | Tile script | Story fight, no flee |

## FOE authoring schema

```yaml
floor: B3F
foes:
  - id: alley_stalker
    cell: [12, 8]
    patrol: [[12,8], [12,9], [13,9]]
    stepsPerMove: 3
    tier: yellow
    group: [stalker]
  - id: rubble_guard
    cell: [4, 15]
    tier: red
    group: [rubble_guard, scrapling]
```

**Tier colors (EO-like):** green (easy), yellow (caution), red (avoid until ready).

## Random encounter table

```yaml
floor: B3F
rate: 0.12  # per step
entries:
  - weight: 50
    group: [stray_hound, stray_hound]
  - weight: 30
    group: [rust_mite]
  - weight: 20
    group: [gutter_crow, stray_hound]
```

## Traps & gathers

| Type | EO parallel | Scope |
|------|-------------|-------|
| Damage tile | Broken glass, exposed rebar | Post-MVP1 |
| Gather / mine / forage | Chopping/mining — **minigame** | **MVP2** |
| Fish | Pond/stream — **fishing minigame** | **MVP2** |
| Chest | Loot; auto-marks on map when opened | MVP1 |

Gather and fish nodes **respawn on hub return**; depleted during one dive. Details: [gathering & fishing](../02-systems/gathering-and-fishing.md).

## Boss checklist

- [ ] Visible on map approach (room scale telegraph)
- [ ] Weakness discovery via Codex or Analysis
- [ ] Drops unlock stratum or synthesis tier
- [x] FOE respawn on hub return ([ADR 008](../../decisions/008-campaign-defaults.md))

## FOE respawn (locked)

When the party **returns to hub** and later **re-enters** a floor:

- **FOEs respawn** to authored spawn positions and patrol indices (fresh floor state for FOEs).
- **Player map**, **open doors**, and **looted chests** persist; **FOEs reset** ([ADR 014](../../decisions/014-mvp1-exploration-map.md)).

Between fights on the same dive **without** hub visit: FOE positions **persist** (defeated FOEs stay down until respawn trigger above).

## Content pipeline

1. Node graph on paper (rooms, FOE gates, stairs)
2. Blockout grid + place FOE entities
3. Playtest: exploration time vs fight time, red FOE deaths
4. Tune random rate so mapping isn't constant interruption

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [ADR 003 — FOE step patrol](../../decisions/003-foe-step-patrol.md)
- [02 — Combat](../02-systems/combat.md)
