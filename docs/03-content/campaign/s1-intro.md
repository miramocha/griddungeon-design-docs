# Stratum 1 — Campaign intro (MVP1)

**Tracking:** [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1)  
**Floor layouts (ASCII, FOE YAML):** [dungeons — MVP1 §](../dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) — do not duplicate grids here.  
**Enemy stats / encounter groups:** [mvp1-enemy-roster](../mvp1-enemy-roster.md).  
**Hub services (Act 2):** [hub — S1 intro](../../02-systems/hub-and-services.md#stratum-1-intro)  
**Guided tutorials (S1):** [s1-guided-tutorials](s1-guided-tutorials.md) · [system](../../02-systems/guided-tutorial.md)  
**Synchro tutorial FOE:** [synchro — S1 gating](../../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe) · [B2F FOE](../dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe) · **Rules:** [#10](https://github.com/miramocha/griddungeon-game/issues/10) · **VN:** [#87](https://github.com/miramocha/griddungeon-game/issues/87) · **Coach:** [#88](https://github.com/miramocha/griddungeon-game/issues/88) · **HUD:** [#35](https://github.com/miramocha/griddungeon-game/issues/35) (done)

Terminology: **campaign intro** = this doc (Acts 1–3). **Event** = tile scripts / one-off story cells ([dungeons § Encounter types](../dungeons-and-encounters.md#encounter-types)); MVP1 S1 uses **B1F** (before first hub) and **B2F** (before tutorial FOE / scripted hub warp).

**Narrative frame:** Player is the active **Navigator** with **no memory** at Act 1; Synchro / Protocol are **discovered** on B2F after crisis — [narrative POV](../../02-systems/narrative-pov.md).

---

## Three acts (same `s1_B1F` map)

Act 1 and Act 3 use **one** `s1_B1F` asset; behavior differs by save flags and tutorial blockers on the floor.

| Act | Phase | Map | Enemies | Paths / spawns |
|-----|-------|-----|---------|----------------|
| **1 — Movement** | Exploration | `s1_B1F` | **Off** — `baseEncounterRate: 0`, `foeSpawns: []` | **Intro spawn** `(4, 2)`; **blockers** funnel to mouth; **`v` to B2F blocked** |
| **2 — Party** | **Hub** (no grid) | — | Off | Guild + Navigator: build **6 core** roster |
| **3 — Tutorial dive** | Exploration | `s1_B1F` → B3F | On per floor; Synchro taught on B2F | **Mouth spawn** `(10, 11)` (`stairsUp`) from hub; blockers **cleared**; mandatory tutorial FOE |

**Act 1 beats:** move from intro cell → wall bump / optional **G** / **C** on route → **Event cell** Navigator briefing → mouth **stairs up** → hub ([guided hints](s1-guided-tutorials.md#act-1--movement-b1f), [mouth briefing](../story-events/s1/s1_b1f_mouth_briefing.md)).

**Act 3 beats:** hub **Enter Stratum 1** at mouth → B1F (optional chaff) → B2F **Event cell briefing VN** → tutorial FOE fight (crisis AOE → VN unlock → guided `protocol_strike` → kill → VN + **warp hub** — [story events § S1 flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)) → re-enter stratum → B3F boss.

---

## Save flags (campaign)

| Flag | Set when |
|------|----------|
| `s1_b1f_mouth_briefing_seen` | Act 1: Event cell VN before first hub (`s1_b1f_mouth_briefing`) |
| `s1_intro_movement_complete` | Act 1: first `stairsUp` → hub at mouth |
| `s1_party_ready` | Act 2: guild party requirement met |
| `s1_tutorial_dive_started` | Act 3: first **Enter Stratum 1** after Act 2 |
| `s1_b2f_stalker_briefing_seen` | After B2F Event-cell approach VN (`s1_b2f_stalker_briefing`) |
| `s1_synchro_unlocked` | After unlock VN (`s1_synchro_protocol_unlock`), post-crisis AOE |
| `s1_synchro_protocol_tutorial_done` | `protocol_strike` finisher killed FOE |
| `s1_first_foe_tutorial_complete` | Hub return VN + scripted warp from B2F tutorial; **B3F** unblocked |

---

## Stratum 1 entry rules (locked)

| Rule | Detail |
|------|--------|
| **Warp gate** | **None** on any `s1_*` floor |
| **New game** | Cold start Act 1 on B1F intro spawn — not hub first |
| **After Act 1** | No hub teleport back to intro cell |
| **Act 3+ hub entry** | Always **B1F mouth** `(10, 11)` — `stairsUp` cell; same on every repeat dive |
| **Mouth `stairsUp`** | → Hub only |
| **Synchro on hub exit** | **0%** / locked until mid–first FOE; **100%** after tutorial complete |

Stratum **2+:** hub entry at warp gate after in-world unlock — [dungeons — warp gates](../dungeons-and-encounters.md#stratum-entry--warp-gates-locked).

---

## Progression gates (MVP1)

- **`v` B1F → B2F:** blocked until Act 3 (`s1_tutorial_dive_started`).
- **B3F / north path:** blocked until `s1_first_foe_tutorial_complete` (tutorial FOE on B2F).
- **Win:** defeat `foe_s1_warden` on B3F ([mvp1-spec §3](../../mvp1-spec.md#3-content-slice-stratum-1-mvp1)).

---

## Related

- [s1-guided-tutorials.md](s1-guided-tutorials.md) — Act 1 / hub / combat coach beats
- [guided-tutorial.md](../../02-systems/guided-tutorial.md) — system (modes, schema, runtime)
- [mvp1-spec §1](../../mvp1-spec.md#1-player-facing-loop-mvp1) — player-facing loop
- [01 — Core loop](../../01-core-loop.md)
- [game-phase](../../02-systems/game-phase.md) — new game bootstrap, `LeaveHub`
- [foe-encounters — tutorial FOE](../../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker)
