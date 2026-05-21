# Dungeons & Encounters

Content structured like **Etrian Odyssey strata** — themed zones with multiple floors, FOE placements, and floor gimmicks.

## Stratum structure

```
Stratum 1: Fallen District (B1F–B5F full arc; **MVP1: B1F–B3F** + boss on B3F) → Stratum boss
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
| B1F | Outskirts gate | None on B1F; FOE from B2F | S1 intro: blocked path → hub; shared map Acts 1 & 3 |
| B2F | Collapsed avenues | 2 FOEs, green tier; 1 step-patrol (`stepsPerMove: 4`) | Key door loop |
| B3F | Flooded underpass | Yellow-tier patrol FOE, narrower paths | Damage floor tiles (post-MVP1) |
| B4F | Ruined plaza | Red-tier FOE guards chest | **MVP2:** salvage pile + flooded cistern |
| B5F | Civic fortress | Stratum boss FOE | Boss room, stairs to Stratum 2 |

**MVP1 vertical slice** stops at **B3F** with the stratum boss and win condition ([mvp1-spec §3](../mvp1-spec.md#3-content-slice-stratum-1-mvp1)). B4F–B5F stay in the full-game arc table above; do not block MVP1 on them. Authoritative MVP1 layouts: [§ MVP1 — Stratum 1 (B1F–B3F)](#mvp1--stratum-1-b1fb3f).

---

## MVP1 — Stratum 1 (B1F–B3F)

**Tracking:** [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1)  
**Asset keys:** `s1` + [`s1_B1F`, `s1_B2F`, `s1_B3F`](../05-class-design-mvp1.md#mvp1-content-ids-locked) (save/map/FOE state)  
**Grid:** **20×20**, flat `level = 0` ([ADR 019](../../decisions/019-floor-verticality.md) — no jump pads in MVP1 slice)  
**Implementation:** hand-fill `StratumFloor` ScriptableObjects until the floor painter ships ([ADR 002](../../decisions/002-mapping-model.md)); game path `Assets/Content/Floors/s1_B1F.asset` etc. ([04 — Tech notes](../04-tech-notes.md#map-system))

### Stratum entry & first-floor stairs (locked)

| Stratum | **Warp gate** | **Hub → labyrinth** | **First-floor `stairsUp`** |
|---------|---------------|----------------------|----------------------------|
| **`s1` (MVP1)** | **None** | Act 1: cold start on B1F; Act 3+: **Enter Stratum 1** → **B1F mouth** only (no warp) | **Hub only** (no previous stratum) |
| **`s2`+** | Yes — hub teleports to authored gate cell on entrance floor | Warp to gate, then explore | **Hub** or **deepest unlocked floor of previous stratum** |

**Within-stratum floors:** `stairsDown` / `stairsUp` on **B2F+** link only to the adjacent floor in the **same** stratum (paired cells).

**First floor of each stratum** = stratum **mouth**. `stairsUp` at the mouth is how the party **returns to camp** (→ Hub phase) or **climbs back** to the previous stratum’s deepest saved floor. Visually this is “exit stairs” — one feature, multiple targets ([05 — Class design](../05-class-design-mvp1.md#floors--stratum)).

**Return thread** ([dungeon navigation](../02-dungeon-navigation.md#interactables)) still instant-jumps to hub; it does not replace mouth stairs.

### Stratum 1 campaign intro

**Authority:** [campaign/s1-intro.md](campaign/s1-intro.md) — three acts, save flags, entry rules, progression gates. This file owns **grids and FOE placement** only.

Summary: Act 1 movement on `s1_B1F` (no combat) → hub party setup → Act 3 from **B1F mouth** → B2F tutorial FOE → B3F boss.

### MVP1 floor summary

| Floor ID | Theme | Spawns | Stairs (mouth / links) | FOEs | Random encounters |
|----------|-------|--------|------------------------|------|-------------------|
| `s1_B1F` | Outskirts gate | Intro `(4,2)` / mouth `(10,2)` | Mouth `^` → **hub**; `v` `(10,17)` → B2F (blocked Act 1) | **0** (Act 1 & B1F layout) | Act 1: **0**; Act 3: low chaff |
| `s1_B2F` | Collapsed avenues | `(10, 2)` from B1F `v` | `^` / `v` at `(10,2)` / `(10,17)` — **same stratum only** | **1** patrol FOE — **first FOE / Synchro gate** | Bind + poison |
| `s1_B3F` | Flooded underpass | `(10, 2)` from B2F | `^` at `(10, 2)`; boss north | **1** boss FOE | Mixed |

**Win condition (MVP1):** defeat `foe_s1_warden` on B3F. **Stratum 2** warp gates and inter-stratum mouth stairs are out of MVP1 scope.

### Map legend (ASCII blockouts)

| Symbol | Meaning |
|--------|---------|
| `#` | Non-walkable (perimeter / room wall) |
| `.` | Walkable floor |
| `E` | Intro spawn — Act 1 only (`partyEntryIntro`) |
| `M` | Mouth spawn — hub re-entry / Act 3 (`partyEntryMouth`) |
| `^` | `stairsUp` — mouth: hub (S1) or hub **or** prev-stratum deepest (S2+) |
| `v` | `stairsDown` — next floor **in same stratum** |
| `F` | FOE spawn |
| `C` | Chest |
| `G` | Gather node — instant loot ([ADR 014](../../decisions/014-mvp1-exploration-map.md)) |
| `D` | Door / **tutorial blocker** (closed until `s1_tutorial_dive_started`) |
| `X` | Blocked passage (Act 1 — opens Act 3) |

**Coordinates:** `(x, y)` with **x** west→east `0…19`, **y** south→north `0…19`. ASCII rows: **first line = y 19 (north)**, last line = y 0 (south). Facing **N** = toward increasing **y**.

Internal walls are **edge walls** on `FloorTileData.SolidEdges`, not separate tile types; ASCII shows room shells only—implementation fills north/east/south/west bits per cell.

### MVP1 enemy & encounter IDs (locked names)

Locked in [05 — Class design](../05-class-design-mvp1.md#mvp1-content-ids-locked): **floors + status** (`bind_head`, `bind_arm`, `poison`). Enemy and group IDs below are **locked for MVP1 content** ([mvp1-spec](../mvp1-spec.md) “8 types + 1 boss”); add rows to the class-design table when enemy SOs land in the game repo.

| Enemy ID | Role | MVP1 status teaching |
|----------|------|----------------------|
| `stray_hound` | Chaff melee | — |
| `rust_mite` | Chaff weak | — |
| `gutter_crow` | Chaff flyer | — |
| `scrapling` | Chaff swarm | — |
| `shackle_rat` | Control | `bind_arm` |
| `venom_slime` | DoT | `poison` |
| `alley_thug` | Mid bruiser | — |
| `rubble_guard` | FOE escort | — |
| `s1_warden` | **Stratum boss** | `bind_head`, `poison` (scripted opens) |

**Encounter groups** (referenced by FOE + random tables):

| Group ID | Slots |
|----------|-------|
| `grp_alley_stalker` | `alley_thug`, `scrapling` |
| `grp_alley_stalker_tutorial` | `alley_thug` (tutorialUnbeatable) — first FOE only |
| `grp_s1_warden` | `s1_warden` (boss; front row) |
| `grp_b2_bind_poison` | mix entries below |

### `s1_B1F` — Outskirts gate (intro + mouth)

**One asset, two modes.** Act 1 uses a **blocked subgraph** to the camp mouth; Act 3 opens the full floor and enables `v` → B2F.

| Field | Act 1 (movement) | Act 3 (tutorial dive) |
|-------|------------------|------------------------|
| `partyEntryIntro` | `(4, 2)`, facing **N** | — |
| `partyEntryMouth` | — | `(10, 2)`, facing **N** (hub **Enter Stratum 1**) |
| `baseEncounterRate` | `0` | `0.05` |
| `foeSpawns` | `[]` | `[]` (FOE from B2F) |
| `stairsUp` (mouth `^`) | → **Hub** | → **Hub** |
| `stairsDown` `v` | **Blocked** (`X` / door flag) | Open → `s1_B2F` `(10, 2)` |
| Tutorial blockers `D`/`X` | **Closed** east/north shortcuts | **Open** |

**Random encounters (Act 3 only):**

```yaml
baseEncounterRate: 0.05   # 0 in Act 1
entries:
  - { groupId: grp_b1_chaff_hound, weight: 60 }
  - { groupId: grp_b1_chaff_mite,   weight: 40 }
```

**ASCII (20×20)** — `X` = blocked until Act 3; intro path E → ^ at mouth:

```
####################
#..................#
#..................#
#......#######.....#
#......#..v..#.....#
#......#.....#.....#
#......###X###.....#
#........#.#.......#
#....C...#.#...G...#
#........#.#.......#
#........#M#.......#
#........#.^.......#
#......###.###.....#
#......#.....#.....#
#......#.....#.....#
#......#######.....#
#..................#
#...E..............#
####################
```

- **E** `(4, 2)` — Act 1 intro spawn; funnel north/east to mouth.
- **M** `(10, 10)` — mouth landing (fiction: camp threshold); pair with **^** `(10, 11)` → hub.
- **v** `(10, 17)` — to B2F; blocked in Act 1.
- **X** — tutorial blockers on shortcuts to `v` and wide loops.

**Act 1 beats:** move from **E** → bump walls on side alcoves → **G** / **C** on route → **^** → hub (sets `s1_intro_movement_complete`).

**Act 3 beats:** hub party ready → spawn **M** → clear blockers → optional B1F chaff fights → **v** → B2F FOE tutorial ([`s1_B2F`](#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)).

---

### `s1_B2F` — Collapsed avenues (bind / poison + patrol FOE)

**Goals:** first **bind** and **poison** random fights; one **step-patrol** FOE ([ADR 003](../../decisions/003-foe-step-patrol.md)); simple **loop** so map literacy matters.

| Field | Value |
|-------|-------|
| `baseEncounterRate` | `0.10` |
| `partyEntryPoint` | `(10, 2)`, facing **N** (from B1F `stairsDown`) |
| `stairsUp` | `(10, 2)` |
| `stairsDown` | `(10, 17)` |

**FOE (required) — Synchro tutorial (unbeatable, mid-fight unlock):**

```yaml
foeId: foe_alley_stalker
spawnCell: [14, 11]
patrolPath: [[14, 11], [14, 12], [15, 12], [15, 11]]
stepsPerMove: 4
tier: green
encounterGroup: grp_alley_stalker_tutorial   # tutorial variant; enemies tutorialUnbeatable
tutorialFirstFoe: true
noFlee: true
encounterTags: [tutorial_synchro, unbeatable]
synchroUnlockTrigger: after_core_turns_2      # or on_first_party_damage — tune in data
```

- **Unbeatable:** encounter enemies cannot die; HP floors at 1 (or damage ignored at 0). Fight ends only after forced **`protocol_strike`** ([synchro § S1 gating](../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe)).
- **Synchro:** locked at fight start; **unlocks mid-fight** at trigger → bar **100%** → forced Protocol on next core turn → scripted FOE retreat / victory.
- **Progression:** path to `s1_B3F` blocked until `s1_first_foe_tutorial_complete`.
- Prior combats (B1F random): Synchro still locked.

Patrol blocks the **shortcut** from east loop to north stairs until the party times a gap or fights. Main safe route: west loop `(4–6, *)` → north → east only after FOE clears.

**Random encounters (bind / poison teaching):**

```yaml
entries:
  - { groupId: grp_b2_chaff,        weight: 35 }  # stray_hound | gutter_crow
  - { groupId: grp_b2_shackle_rat, weight: 35 }  # shackle_rat (+ optional scrapling)
  - { groupId: grp_b2_venom_slime, weight: 30 }  # venom_slime
```

**ASCII (20×20):**

```
####################
#..................#
#..................#
#......#######.....#
#......#..v..#.....#
#......#.....#.....#
#......#.....#.....#
#....####.####.....#
#....#.......#.....#
#....#..C....#.....#
#....#.......#.....#
#....###...####.....#
#.......#.#........#
#.......#F#........#
#.......#.#........#
#....####.####.....#
#....#.......#.....#
#....#.......#.....#
#....#.......#.....#
#....####^####.....#
####################
```

`^` and `v` share column **10**; entry from B1F lands on **^** cell. East loop `(14–16, 10–13)` intersects FOE patrol.

---

### `s1_B3F` — Flooded underpass (stratum boss)

**Goals:** MVP1 **win** fight; boss room telegraph; narrower paths; no damage-floor tiles (post-MVP1 gimmick from full-game B3F row).

| Field | Value |
|-------|-------|
| `baseEncounterRate` | `0.12` |
| `partyEntryPoint` | `(10, 2)`, facing **N** |
| `stairsUp` | `(10, 2)` |
| `stairsDown` | — (slice end; placeholder wall north of boss) |

**Boss FOE:**

```yaml
foeId: foe_s1_warden
spawnCell: [10, 16]
patrolPath: [[10, 16]]
stepsPerMove: 0
tier: red
encounterGroup: grp_s1_warden
noFlee: true
```

Boss room: cells `(8–12, 15–18)` with single **south** entrance at `(10, 14)` — party sees room on map before commit. Optional pre-boss **C** at `(4, 10)` (reward, not gating).

**Random encounters:**

```yaml
entries:
  - { groupId: grp_b3_mix_hounds, weight: 45 }
  - { groupId: grp_b3_rubble_pair, weight: 35 }  # rubble_guard + scrapling
  - { groupId: grp_b3_control,     weight: 20 }  # shackle_rat | venom_slime
```

**ASCII (20×20):**

```
####################
#..................#
#......#####.......#
#......#...#.......#
#......# F #.......#
#......#...#.......#
#......#####.......#
#........#.........#
#........#.........#
#....#########.....#
#....#.......#.....#
#....#.......#.....#
#....#.......#.....#
#....####^####.....#
#........#.........#
#....C...#.........#
#........#.........#
#........#.........#
#........#.........#
#........#.........#
####################
```

Boss **F** at `(10, 16)`; approach corridor `(10, 3–14)` is width-1 with wall cheeks — teaches FOE routing from B2F.

**Post-boss (MVP1):** set stratum-1-cleared flag; return via mouth **stairs up** → hub or **Return thread**. Do not require `stairsDown` on B3F for MVP1 completion.

---

### MVP1 `StratumFloor` export checklist

- [ ] `s1_B1F.asset` — grid 20×20, intro + mouth spawns, mouth `stairsUp`→hub, tutorial blockers, Act 1/3 flags
- [ ] `s1_B2F.asset` — patrol path indices match `foe_alley_stalker` YAML
- [ ] `s1_B3F.asset` — boss `noFlee` on encounter group / fight tag
- [ ] `EncounterGroup` + `EnemyDefinition` SOs for provisional IDs (game repo)
- [ ] Playtest: B1F tutorial ≤ 8 min; B2F FOE gap or fight; B3F boss wipe rate target 1–3 attempts at level 5–8
- [ ] `foe_alley_stalker`: tutorial unbeatable FOE, mid-fight Synchro unlock, forced `protocol_strike` in-fight, B3F block until `s1_first_foe_tutorial_complete`

---

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
