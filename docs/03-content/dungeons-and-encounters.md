# Dungeons & Encounters

Content structured like **Etrian Odyssey strata** � themed zones with multiple floors, FOE placements, and floor gimmicks.

**Non-strata maps (optional):** **side dungeons** (`sd01`, �) � full grid explore + combat, hub **Side expedition** menu only. Not part of stratum progression � [side dungeons](../02-systems/side-dungeons.md), [ADR 022](../../decisions/022-side-dungeons-mvp3.md).

## Stratum structure

```
Stratum 1: Fallen District (B1F�B5F full arc; **required slice: B1F�B3F** + boss on B3F) ? Stratum boss
Stratum 2: Sand Ruins (B6F�B10F) ? �
```

Each floor data file:

```
stratum_id, floor_id (B1F), theme_art, music, encounter_table,
foe_spawns[], trap_table, gather_nodes[], stairs, quests
```

## Floor design principles (EO)

1. **Looping paths** � shortcuts behind keys/FOE gates reward map literacy.
2. **FOE as puzzles** � block shortest route until party ready or map route around patrol.
3. **Gather / fish nodes** � **optional** minigames ? materials for synthesis ([gathering & fishing](../02-systems/gathering-and-fishing.md)).
4. **Safe-ish rooms** � lower encounter rate (not always zero).
5. **Landmarks** � unique art/audio cue; auto-mapped when visited.

## Example: Stratum 1 arc

| Floor | Theme | FOE teaching | Gimmick |
|-------|-------|--------------|---------|
| B1F | Outskirts gate | None on B1F; FOE from B2F | S1 intro: blocked path ? hub; shared map Acts 1 & 3 |
| B2F | Collapsed avenues | 2 FOEs, green tier; 1 step-patrol (`stepsPerMove: 4`) | Key door loop |
| B3F | Flooded underpass | Yellow-tier patrol FOE, narrower paths | Damage floor tiles (later) |
| B4F | Ruined plaza | Red-tier FOE guards chest | **Optional:** salvage pile + flooded cistern |
| B5F | Civic fortress | Stratum boss FOE | Boss room, stairs to Stratum 2 |

**Required vertical slice** stops at **B3F** with the stratum boss and win condition ([release scope](../00-release-scope.md#required-first-playable), [S1 intro](campaign/s1-intro.md)). B4F–B5F stay in the full-game arc table above; do not block the required slice on them. 

**Floor grids (B1F�B3F) are draft � not locked.** Per-floor ASCII, spawn tables, and export checklists live in [archive — S1 floor layouts (draft)](../archive/mvp1-s1-floor-layouts-draft.md). During iteration, **game `ExplorationFloor` assets** + Floor Editor Apply are runtime authority; design-docs blockouts are reference only.

---

## Stratum 1 (B1F–B3F) — required slice

**Tracking:** [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1)  
**Asset keys:** `s1` + [`s1_B1F`, `s1_B2F`, `s1_B3F`](../05-class-design.md#content-ids-locked) (save/map/FOE state)  
**Grid:** **20�20**, flat `level = 0` ([ADR 019](../../decisions/019-floor-verticality.md) � no jump pads in required slice)  
**Implementation:** `ExplorationFloor` assets under `Assets/Content/Floors/` ([ADR 002](../../decisions/002-mapping-model.md), [Floor Editor](../02-systems/floor-editor.md)). **Layouts are draft** � see [archive draft layouts](../archive/mvp1-s1-floor-layouts-draft.md); game assets + Floor Editor Apply are iteration authority until lock.

### Stratum entry & warp gates (locked)

| Stratum | **Warp gate on floor** | **Hub ? labyrinth** | **Hub unlock** | **First-floor `stairsUp`** |
|---------|------------------------|----------------------|----------------|---------------------------|
| **`s1` (required slice)** | **None** | Act 1: cold start on B1F intro; Act 3+: **Enter Stratum 1** ? **B1F gate** (stratum beginning) | Act 2 party ready (`s1_party_ready`) � not a warp-gate tile | ? **Hub** |
| **`s2`+** | Yes � authored gate cell on **entrance floor** | **Enter Stratum** *N* only if gate unlocked ? warp to gate (beginning) | Discover / story-unlock warp gate in prior stratum | ? **Hub** |

**Rule:** every hub dive starts at the stratum **beginning** (gate or warp gate on entrance floor). No resume at deepest floor, no gate stairs to a prior stratum�s depth.

**Within-stratum floors:** `stairsDown` / `stairsUp` on **B2F+** link only to the adjacent floor in the **same** stratum (paired cells).

**First floor of each stratum** = stratum **gate**. Gate `stairsUp` returns to **hub** only ([05 � Class design](../05-class-design.md#content-definitions-runtime-scriptableobjects)).

**Return thread** ([dungeon navigation](../02-dungeon-navigation.md#interactables)) still instant-jumps to hub; it does not replace gate stairs.

### Stratum 1 campaign intro

**Authority:** [campaign/s1-intro.md](campaign/s1-intro.md) � three acts, save flags, entry rules, progression gates. This file owns **encounter IDs, stratum rules, and floor summary**; per-floor ASCII is [archived (draft)](../archive/mvp1-s1-floor-layouts-draft.md).

Summary: Act 1 movement on `s1_B1F` (no combat) ? hub party setup ? Act 3 from **B1F gate** ? B2F tutorial FOE ? B3F boss.

### Required slice floor summary

| Floor ID | Theme | Spawns | Stairs (gate / links) | FOEs | Random encounters |
|----------|-------|--------|------------------------|------|-------------------|
| `s1_B1F` | Outskirts gate | Intro `(4,2)` / gate `(10,11)` | Gate `^` ? **hub**; `v` `(10,17)` ? B2F (blocked Act 1) | **0** | Act 1: **0**; Act 3: **0.05** � `grp_b1_chaff_*` |
| `s1_B2F` | Collapsed avenues | `(10, 2)` from B1F `v` | `^` / `v` at `(10,2)` / `(10,15)` � **same stratum only** | **1** � `foe_alley_stalker` ? `grp_alley_stalker_tutorial` | **0.10** � `grp_b2_chaff` / `shackle_rat` / `venom_slime` |
| `s1_B3F` | Flooded underpass | `(10, 2)` from B2F | `^` at `(10, 2)`; boss north | **1** � `foe_s1_warden` ? `grp_s1_warden` | **0.12** � `grp_b3_mix_hounds` / `rubble_pair` / `control` |

**Win condition:** defeat `foe_s1_warden` on B3F. **Stratum 2** warp-gate hub entry is out of required-slice scope.

### Map legend (ASCII blockouts)

| Symbol | Meaning | Runtime map ([map-cell-art](../02-systems/map-cell-art.md)) |
|--------|---------|--------------------------------------------------------------|
| `#` | Non-walkable (perimeter / room wall) | Solid block � `map-view__cell--wall` |
| `.` | Walkable floor | Floor `�` when revealed |
| `E` | Intro spawn � Act 1 only (`partyEntryIntro`) | Spawn only � not a map icon |
| `M` | Gate landing fiction `(10, 10)`; hub spawn at `^` `(10, 11)` (`partyEntryGate`) | `M` not a map icon |
| `^` | `stairsUp` � gate: ? **hub** (all strata) | Stairs up icon / `^` |
| `v` | `stairsDown` � next floor **in same stratum** | Stairs down icon / `v` |
| `F` | FOE spawn | FOE marker when in LOS |
| `!` | **Event** tile � story script on enter ([story events � S1](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)) | Overlay when wired; S1 B2F tutorial briefing |
| `C` | **Chest** � **non-walkable**; loot via **Interact** from adjacent cell while **facing** chest ([#105](https://github.com/miramocha/griddungeon-game/issues/105)); `ChestItemId` on tile | Solid block when visited; chest **overlay** when wired ([#38](https://github.com/miramocha/griddungeon-game/issues/38)) |
| `G` | **Gather** � walkable; instant loot on interact ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) | Gather **overlay** when cell visited (`MapGatherMarkersPresenter`) |
| `D` | Door / **tutorial blocker** (closed until `s1_tutorial_dive_started`) | Door overlay + tint; campaign may also gate **walk** without icon ([#33](https://github.com/miramocha/griddungeon-game/issues/33)) |
| `X` | Blocked passage (Act 1 � opens Act 3) | Solid/gate tint � not edge wall |

**Coordinates:** `(x, y)` with **x** west?east `0�19`, **y** south?north `0�19`. ASCII rows: **first line = y 19 (north)**, last line = y 0 (south). Facing **N** = toward increasing **y**.

Internal walls are **`SolidEdges`** on walkable `FloorTileData`, not separate tile types; ASCII shows room shells only � runtime paints **0�4 edge segments** per cell from `WallMask` after reveal (bump + perimeter, [ADR 014](../../decisions/014-mvp1-exploration-map.md)). Three or more edges on one floor cell ? alcove fill (`�` glyph today), still walkable � distinct from impassable `#`.

### Launch enemy & encounter IDs (locked names)

**Stats, skills, group slot layouts, FOE mapping:** [enemy-roster.md](enemy-roster.md) ([design-docs #2](https://github.com/miramocha/griddungeon-design-docs/issues/2)). IDs also listed in [05 � Class design](../05-class-design.md#content-ids-locked).

| Enemy ID | Role | Status teaching |
|----------|------|----------------------|
| `stray_hound` | Chaff melee | � |
| `rust_mite` | Chaff weak | � |
| `gutter_crow` | Chaff flyer | � |
| `scrapling` | Chaff swarm | � |
| `shackle_rat` | Control | `bind_arm` |
| `venom_slime` | DoT | `poison` |
| `alley_thug` | Mid bruiser | � |
| `rubble_guard` | FOE escort | � |
| `s1_warden` | **Stratum boss** | `bind_head`, `poison` (immune; scripted opens in fight) |

**Encounter groups** (full compositions in roster doc):

| Group ID | Use |
|----------|-----|
| `grp_alley_stalker`, `grp_alley_stalker_tutorial`, `grp_s1_warden` | FOE / boss |
| `grp_b1_chaff_hound`, `grp_b1_chaff_mite` | B1F random (Act 3) |
| `grp_b2_chaff`, `grp_b2_shackle_rat`, `grp_b2_venom_slime` | B2F random |
| `grp_b3_mix_hounds`, `grp_b3_rubble_pair`, `grp_b3_control` | B3F random |

### Per-floor grids & export (draft � archived)

**Not locked.** ASCII blockouts, per-floor YAML, spawn coordinates, and the `ExplorationFloor` export checklist moved to **[archive — S1 floor layouts (draft)](../archive/mvp1-s1-floor-layouts-draft.md)** so this page stays campaign + encounter IDs + stratum rules.

When layouts lock, promote coords from game `s1_B*n*F.asset` back here or replace the archive with a locked snapshot.

**Act beats (unchanged):** B1F intro/gate � [guided hints](campaign/s1-guided-tutorials.md#act-1--movement-b1f), [gate briefing](story-events/s1/s1_b1f_gate_briefing.md). B2F tutorial FOE � [story events � S1 flow](../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker), [synchro � S1 gating](../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe).

## Encounter types

| Type | Trigger | Design notes |
|------|---------|--------------|
| **Random** | Per-step roll | Shared table SO per floor (`randomEncounterTableId`); no FOE sprite |
| **FOE** | Grid entity contact | Authored position; patrol path optional; flee ? 1 cell back ([foe-encounters](../02-systems/foe-encounters.md)) |
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

**Shipped model ([game #288](https://github.com/miramocha/griddungeon-game/pull/288)):** reusable **`RandomEncounterTableDefinition`** SOs under `Assets/Content/RandomEncounterTables/`. Each floor stores **`randomEncounterTableId`** only on `ExplorationFloor`; rate and weighted groups live on the table asset. Author in Floor Editor **Random Encounters** mode or open the table inspector directly ([floor painter](02-systems/floor-editor.md)).

| Floor key | Table id | Base rate | Weighted groups (design) |
|-----------|----------|-----------|--------------------------|
| `s1_B1F` | `enc_s1_b1_chaff` | **0.05** Act 3 (Act 1 forced **0** by `S1CampaignResolver`) | `grp_b1_chaff_hound` / `grp_b1_chaff_mite` |
| `s1_B2F` | `enc_s1_act2_mid` | **0.10** | `grp_b2_chaff` / `grp_b2_shackle_rat` / `grp_b2_venom_slime` |
| `s1_B3F` | `enc_s1_act3_deep` | **0.12** | `grp_b3_mix_hounds` / `grp_b3_rubble_pair` / `grp_b3_control` |

**Example table shape** (YAML sketch — runtime uses SO + `EncounterTable` DTO):

```yaml
tableId: enc_s1_act3_deep
baseEncounterRate: 0.12
entries:
  - weight: 45
    groupId: grp_b3_mix_hounds
  - weight: 35
    groupId: grp_b3_rubble_pair
  - weight: 20
    groupId: grp_b3_control
```

Legacy inline floor `EncounterTable` fields are removed — floors reference shared tables only.

## Traps & gathers

| Type | EO parallel | Scope |
|------|-------------|-------|
| Damage tile | Broken glass, exposed rebar | Later |
| Gather / mine / forage | Chopping/mining � **minigame** | **optional** |
| Fish | Pond/stream � **fishing minigame** | **optional** |
| Chest | Loot; auto-marks on map when opened | Required slice |

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

- [Stratum 1 enemy roster](enemy-roster.md) � stats, skills, encounter groups ([#2](https://github.com/miramocha/griddungeon-design-docs/issues/2))
- [02 � Dungeon navigation](../02-dungeon-navigation.md)
- [ADR 003 � FOE step patrol](../../decisions/003-foe-step-patrol.md)
- [02 � Combat](../02-systems/combat.md)
