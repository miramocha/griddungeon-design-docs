---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/draft
  - domain/campaign/s1
---
# Stratum 1 — Campaign intro

**Tracking:** [design-docs #1](https://github.com/miramocha/griddungeon-design-docs/issues/1)  
**Floor layouts (ASCII, FOE YAML — draft):** [archive — S1 floor layouts](../../archive/mvp1-s1-floor-layouts-draft.md) — do not duplicate grids here.  
**Enemy stats / encounter groups:** [enemy-roster](../enemy-roster.md).  
**Hub services (Act 2):** [hub — S1 intro](../../02-systems/hub-and-services.md#stratum-1-intro)  
**Guided tutorials (S1):** [s1-guided-tutorials](s1-guided-tutorials.md) · [system](../../02-systems/guided-tutorial.md)  
**Synchro tutorial FOE:** [synchro — S1 gating](../../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe) · [B2F FOE (draft)](../../archive/mvp1-s1-floor-layouts-draft.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe) · **Rules:** [#10](https://github.com/miramocha/griddungeon-game/issues/10) · **VN:** [#87](https://github.com/miramocha/griddungeon-game/issues/87) · **Coach:** [#88](https://github.com/miramocha/griddungeon-game/issues/88) · **HUD:** [#35](https://github.com/miramocha/griddungeon-game/issues/35) (done)

Terminology: **campaign intro** = this doc (Acts 1–3). **Event** = tile scripts / one-off story cells ([dungeons § Encounter types](../dungeons-and-encounters.md#encounter-types)); Launch S1 uses **B1F** (before first hub) and **B2F** (before tutorial FOE / scripted hub warp).

**Narrative frame:** Player is the active **Navigator** with **no memory** at Act 1; Synchro / Protocol are **discovered** on B2F after crisis — [narrative POV](../../02-systems/narrative-pov.md).

---

## Three acts (same `s1_B1F` map)

Act 1 and Act 3 use **one** `s1_B1F` asset; behavior differs by save flags and tutorial blockers on the floor.

| Act | Phase | Map | Enemies | Paths / spawns |
|-----|-------|-----|---------|----------------|
| **1 — Movement** | Exploration | `s1_B1F` | **Off** — `baseEncounterRate: 0`, `foeSpawns: []` | **Intro spawn** `(4, 2)`; **blockers** funnel to gate; **`v` to B2F blocked** |
| **2 — Party** | **Hub** (no grid) | — | Off | Guild + Navigator: build **6 core** roster |
| **3 — Tutorial dive** | Exploration | `s1_B1F` → B3F | On per floor; Synchro taught on B2F | **Gate spawn** `(10, 11)` (`stairsUp`) from hub; blockers **cleared**; mandatory tutorial FOE |

**Act 1 beats:** **solo** Navigator — intro cell → wall bump / optional **G** / **C** → **Event cell** briefing → gate **stairs up** → hub (no cores yet; [guided hints](s1-guided-tutorials.md#act-1--movement-b1f), [gate briefing](../story-events/s1/s1_b1f_gate_briefing.md)).

**Act 3 beats:** hub **Enter Stratum 1** at gate → B1F (optional chaff) → B2F **Event cell briefing VN** → tutorial FOE fight (crisis AOE → VN unlock → guided `protocol_strike` → kill → VN + **warp hub** — [story events § S1 flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)) → re-enter stratum → B3F boss.

---

## Save flags (campaign)

**Implemented** (`CampaignFlagRegistry` asset in game — `SCREAMING_SNAKE_CASE` doc ids; Save Editor + story/floor/hub-leave authoring use registry-backed pickers):

| Flag | Set when |
|------|----------|
| `S1_B1F_GATE_BRIEFING_SEEN` | Act 1: Event cell VN before first hub (`s1_b1f_gate_briefing`) |
| `S1_PARTY_READY` | Act 2: guild party requirement met |
| `S1_B2F_STALKER_BRIEFING_SEEN` | After B2F Event-cell approach VN (`s1_b2f_stalker_briefing`) |
| `S1_SYNCHRO_UNLOCKED` | After unlock VN (`s1_synchro_protocol_unlock`), post-crisis AOE |
| `S1_SYNCHRO_PROTOCOL_TUTORIAL_DONE` | `protocol_strike` finisher killed FOE |
| `S1_FIRST_FOE_TUTORIAL_COMPLETE` | Hub return VN + scripted warp from B2F tutorial; **B3F** unblocked |
| `S1_STRATUM_CLEARED` | Stratum boss defeated (future win gate) |

**Planned** (design only — not in `CampaignFlagRegistry` / save yet):

| Flag (planned id) | Set when |
|-------------------|----------|
| `s1_intro_movement_complete` | Act 1: first `stairsUp` → hub at gate |
| `s1_tutorial_dive_started` | Act 3: first **Enter Stratum 1** after Act 2 |

---

## Stratum 1 entry rules (locked)

| Rule | Detail |
|------|--------|
| **Warp gate** | **None** on any `s1_*` floor |
| **New game** | Cold start Act 1 on B1F intro spawn — not hub first |
| **After Act 1** | No hub teleport back to intro cell |
| **Act 3+ hub entry** | Always **B1F gate** `(10, 11)` — `stairsUp` cell; same on every repeat dive |
| **Gate `stairsUp`** | → Hub only |
| **Synchro on hub exit** | **0%** / locked until mid–first FOE; **100%** after tutorial complete |

Stratum **2+:** hub entry at warp gate after in-world unlock — [dungeons — warp gates](../dungeons-and-encounters.md#stratum-entry--warp-gates-locked).

---

## Progression gates (required slice)

- **`v` B1F → B2F:** blocked until Act 3 (`s1_tutorial_dive_started`).
- **B3F / north path:** blocked until `S1_FIRST_FOE_TUTORIAL_COMPLETE` (tutorial FOE on B2F).
- **Win:** defeat `foe_s1_warden` on B3F ([dungeons § floor summary](../dungeons-and-encounters.md#required-slice-floor-summary)).

---

## Related

- [s1-guided-tutorials.md](s1-guided-tutorials.md) — Act 1 / hub / combat coach beats
- [guided-tutorial.md](../../02-systems/guided-tutorial.md) — system (modes, schema, runtime)
- [01 — Core loop](../../01-core-loop.md) — player-facing loop
- [01 — Core loop](../../01-core-loop.md)
- [game-phase](../../02-systems/game-phase.md) — new game bootstrap, `LeaveHub`
- [foe-encounters — tutorial FOE](../../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker)
