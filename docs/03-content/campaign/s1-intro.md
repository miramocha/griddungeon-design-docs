# Stratum 1 — Campaign intro (MVP1)

**Tracking:** [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1)  
**Floor layouts (ASCII, FOE YAML):** [dungeons — MVP1 §](../dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) — do not duplicate grids here.  
**Hub services (Act 2):** [hub — S1 intro](../../02-systems/hub-and-services.md#stratum-1-intro)  
**Synchro tutorial FOE:** [synchro — S1 gating](../../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe) · [B2F FOE](../dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)

Terminology: **campaign intro** = this doc (Acts 1–3). **Event** (future) = tile scripts / one-off story cells — see [campaign README](README.md).

---

## Three acts (same `s1_B1F` map)

Act 1 and Act 3 use **one** `s1_B1F` asset; behavior differs by save flags and tutorial blockers on the floor.

| Act | Phase | Map | Enemies | Paths / spawns |
|-----|-------|-----|---------|----------------|
| **1 — Movement** | Exploration | `s1_B1F` | **Off** — `baseEncounterRate: 0`, `foeSpawns: []` | **Intro spawn** `(4, 2)`; **blockers** funnel to mouth; **`v` to B2F blocked** |
| **2 — Party** | **Hub** (no grid) | — | Off | Guild + Navigator: build **6 core** roster |
| **3 — Tutorial dive** | Exploration | `s1_B1F` → B3F | On per floor; Synchro taught on B2F | **Mouth spawn** `(10, 2)` from hub; blockers **cleared**; mandatory tutorial FOE |

**Act 1 beats:** move from intro cell → wall bump / optional **G** / **C** on route → mouth **stairs up** → hub.

**Act 3 beats:** hub **Enter Stratum 1** at mouth → B1F (optional chaff) → B2F **`foe_alley_stalker`** (unbeatable, mid-fight Synchro + forced `protocol_strike`) → B3F boss.

---

## Save flags (campaign)

| Flag | Set when |
|------|----------|
| `s1_intro_movement_complete` | Act 1: first `stairsUp` → hub at mouth |
| `s1_party_ready` | Act 2: guild party requirement met |
| `s1_tutorial_dive_started` | Act 3: first **Enter Stratum 1** after Act 2 |
| `s1_synchro_unlocked` | Mid-fight during `foe_alley_stalker` tutorial |
| `s1_synchro_protocol_tutorial_done` | Forced `protocol_strike` completed in that fight |
| `s1_first_foe_tutorial_complete` | Tutorial encounter ended; **B3F** unblocked |

---

## Stratum 1 entry rules (locked)

| Rule | Detail |
|------|--------|
| **Warp gate** | **None** on any `s1_*` floor |
| **New game** | Cold start Act 1 on B1F intro spawn — not hub first |
| **After Act 1** | No hub teleport back to intro cell |
| **Act 3 entry** | Always **B1F mouth** `(10, 2)` — not wilderness intro, not resume-deepest (first dive) |
| **Mouth `stairsUp`** | → Hub only (no previous stratum) |
| **Synchro on hub exit** | **0%** / locked until mid–first FOE; **100%** after tutorial complete |
| **Repeat dives** | Resume policy TBD post-MVP1 ([dungeons — entry table](../dungeons-and-encounters.md#stratum-entry--first-floor-stairs-locked)) |

Stratum **2+** use warp gates and mouth stairs → hub **or** previous stratum deepest — see dungeons entry table.

---

## Progression gates (MVP1)

- **`v` B1F → B2F:** blocked until Act 3 (`s1_tutorial_dive_started`).
- **B3F / north path:** blocked until `s1_first_foe_tutorial_complete` (tutorial FOE on B2F).
- **Win:** defeat `foe_s1_warden` on B3F ([mvp1-spec §3](../../mvp1-spec.md#3-content-slice-stratum-1-mvp1)).

---

## Related

- [mvp1-spec §1](../../mvp1-spec.md#1-player-facing-loop-mvp1) — player-facing loop
- [01 — Core loop](../../01-core-loop.md)
- [game-phase](../../02-systems/game-phase.md) — new game bootstrap, `LeaveHub`
- [foe-encounters — tutorial FOE](../../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker)
