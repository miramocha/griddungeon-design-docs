# Launch — Stratum 1 floor layouts (draft archive)

**Status:** **Draft — not locked** (archived 2026-06-14)  
**Supersedes:** detailed per-floor ASCII blockouts that lived in [dungeons — launch §](../03-content/dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f)

Use this file as **design reference** while grids, spawns, and exit topology are iterated in **Floor Painter** and `Assets/Content/Floors/s1_B*n*F.asset`. Do **not** treat coordinates or ASCII rows as shipping authority until a layout lock ticket closes.

**Runtime authority during iteration:**

| Source | Role |
|--------|------|
| `Assets/Content/Floors/s1_B1F.asset` etc. (game) | Play Mode + tests read serialized tiles + `exitLinks[]` |
| Floor Painter **Apply** | Authoring path for custom / side-dungeon floors |
| `S1B*FLayoutBuilder` (game) | Dev reset / migration only — not spec authority |
| This archive | Historical blockouts + FOE YAML sketches |

**Campaign / entry rules** (hub gate, Act 1 vs Act 3, flags) stay in [s1-intro](../03-content/campaign/s1-intro.md) and [dungeons — stratum entry](../03-content/dungeons-and-encounters.md#stratum-entry--warp-gates-locked).

---

## `s1_B1F` — Outskirts gate (intro + gate)

**One asset, two modes.** Act 1 uses a **blocked subgraph** to the camp gate; Act 3 opens the full floor and enables `v` → B2F.

| Field | Act 1 (movement) | Act 3 (tutorial dive) |
|-------|------------------|------------------------|
| `partyEntryIntro` | `(4, 2)`, facing **N** | — |
| `partyEntryGate` | — | `(10, 11)` at gate `^`, facing **N** (hub **Enter Stratum 1**) |
| `baseEncounterRate` | `0` | `0.05` |
| `foeSpawns` | `[]` | `[]` (FOE from B2F) |
| `stairsUp` (gate `^`) | → **Hub** | → **Hub** |
| `stairsDown` `v` | **Blocked** (`X` / door flag) | Open → `s1_B2F` `(10, 2)` |
| Tutorial blockers `D`/`X` | **Closed** east/north shortcuts | **Open** |

**Random encounters (Act 3 only):**

```yaml
baseEncounterRate: 0.05   # 0 in Act 1
entries:
  - { groupId: grp_b1_chaff_hound, weight: 60 }
  - { groupId: grp_b1_chaff_mite,   weight: 40 }
```

**ASCII (20×20)** — `X` = blocked until Act 3; intro path E → ^ at gate; north cap at `(9–11, 17–18)` blocks west bypass to `v`:

```
####################
#........###.......#
#........#.#.......#
#......###.###.....#
#......#..v..#.....#
#......#.....#.....#
#......###X###.....#
#........#.#.......#
#....C...#.#...G...#
#........#.#.......#
#........#!#.......#
#........#.^.......#
#......###.###.....#
#......#.....#.....#
#......#.....#.....#
#......#######.....#
#..................#
#...E..............#
####################
```

- **E** `(4, 2)` — Act 1 intro spawn; funnel north/east to gate.
- **`!` `(10, 9)`** — gate camp threshold + Act 1 Event cell: **`s1_b1f_gate_briefing`** before first hub.
- **v** `(10, 17)` — to B2F; blocked in Act 1.
- **X** — tutorial blockers on shortcuts to `v` and wide loops.

---

## `s1_B2F` — Collapsed avenues (bind / poison + patrol FOE)

**Goals:** first **bind** and **poison** random fights; one **step-patrol** FOE; simple **loop** so map literacy matters.

| Field | Value |
|-------|-------|
| `baseEncounterRate` | `0.10` |
| `partyEntryPoint` | `(10, 2)`, facing **N** (from B1F `stairsDown`) |
| `stairsUp` | `(10, 2)` |
| `stairsDown` | `(10, 15)` |

**FOE (required) — Synchro tutorial (unbeatable, mid-fight unlock):**

```yaml
foeId: foe_alley_stalker
spawnCell: [12, 11]
patrolPath: [[12, 11], [11, 11], [10, 11], [9, 11], [8, 11], [7, 11], [6, 11], [7, 11], [8, 11], [9, 11], [10, 11], [11, 11]]
stepsPerMove: 4
tier: green
encounterGroup: grp_alley_stalker_tutorial
tutorialFirstFoe: true
noFlee: true
encounterTags: [tutorial_synchro, unbeatable]
synchroUnlockTrigger: after_core_turns_2
```

**Random encounters:**

```yaml
entries:
  - { groupId: grp_b2_chaff,        weight: 35 }
  - { groupId: grp_b2_shackle_rat, weight: 35 }
  - { groupId: grp_b2_venom_slime, weight: 30 }
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
#....###..####.....#
#.......#.#........#
#......#!#........#
#.......#F#........#
#....####.####.....#
#....#.......#.....#
#....#.......#.....#
#....#.......#.....#
#....#########.....#
####################
```

`^` and `v` at `(10, 2)` / `(10, 15)`. **`!` `(7, 11)`** — tutorial Event cell. FOE **F** patrol on east loop.

---

## `s1_B3F` — Flooded underpass (stratum boss)

| Field | Value |
|-------|-------|
| `baseEncounterRate` | `0.12` |
| `partyEntryPoint` | `(10, 2)`, facing **N** |
| `stairsUp` | `(10, 2)` |
| `stairsDown` | — (slice end) |

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
#....#########.....#
#........#.........#
#....C...#.........#
#........#.........#
#........#.........#
#........#.........#
#........#.........#
```

---

## Export checklist (draft — do not close the launch slice on this alone)

- [ ] `s1_B1F.asset` — grid, intro + gate, `exitLinks[]`, Act 1/3 blockers
- [ ] `s1_B2F.asset` — patrol path matches `foe_alley_stalker`
- [ ] `s1_B3F.asset` — boss `noFlee`
- [ ] Layout lock sign-off — promote coords from game assets back into [dungeons](../03-content/dungeons-and-encounters.md) or replace this archive
