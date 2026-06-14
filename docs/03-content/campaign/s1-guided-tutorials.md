# S1 — Guided tutorial beats (later target)

**Required slice:** S1 teaching uses story VN ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) + `CombatTutorialHudRules` ([#35](https://github.com/miramocha/griddungeon-game/issues/35)) only — full coach + codex deferred ([#88](https://github.com/miramocha/griddungeon-game/issues/88), [release scope § Later](../../00-release-scope.md#later)).

**System:** [guided-tutorial.md](../../02-systems/guided-tutorial.md) · **ADR:** [029](../../decisions/029-guided-tutorial.md) (Accepted)  
**Campaign acts & flags:** [s1-intro.md](s1-intro.md)  
**Floor layout:** [archive — s1_B1F (draft)](../../archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate)  
**Combat + VN sequence:** [story events § S1 flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)

Each row is a **`tutorialEntryId`** (codex + in-world). Author **pages[]** with `textKey` + optional `imageId` (**stills only** at launch). Draft English below is per-page body (`textEn`). **Codex:** pause menu (`Esc`) → Tutorial codex ([ADR 029](../../decisions/029-guided-tutorial.md)).

**Voice:** **No character speaker** — impersonal coach copy only (system / second-person imperative). No `speakerId`, no portrait. Fiction and emotion live in **story VN** ([narrative POV](../../02-systems/narrative-pov.md)); tutorials teach **controls and UI**. **Act 1** fiction (solo Navigator) is **not** stated in guided rows — only in VN.

---

## Overview

| Act | Phase | Guided? | Story VN? |
|-----|-------|---------|-----------|
| **1 — Movement** | Exploration `s1_B1F` | **Yes** — movement + interact | **Yes** — gate Event cell before hub |
| **2 — Party** | Hub | Optional / UI motion only | No |
| **3 — Tutorial dive** | B1F → B2F combat | **Yes** — Protocol coach | **Yes** — B2F Event briefing + unlock + hub return |

---

## Act 1 — Movement (B1F)

**Prerequisites:** new game, not `s1_intro_movement_complete`.  
**End:** first `stairsUp` at gate **^** `(10, 11)` → hub.

**Party (fiction):** Navigator explores **solo** in Act 1 — see [gate briefing VN](../story-events/s1/s1_b1f_gate_briefing.md). Guided rows stay **impersonal** (no crew, Navigator, or backstory).

| Order | `tutorialEntryId` | Trigger | `completion` | Pages (draft `textEn`) |
|-------|-------------------|---------|--------------|-------------------------|
| 1 | `s1_explore_intro_move` | Act 1 spawn at **E** `(4, 2)` | last page dismiss | p1: “The map reveals tiles as you move.” p2: “Move **north** toward the camp marker.” (+ still: compass / passage) |
| 2 | `s1_explore_wall_bump` | First wall bump | last page dismiss | “Blocked. **Strafe** or **turn**, then step forward.” |
| 3 | `s1_explore_route_features` | First enter **G** or **C** | `interact` if triggered on **C**; else last page dismiss | p1: “New tiles are added to the map as you explore.” p2: “Cache on the grid. **Interact** on **C** to open it.” |
| 4 | `s1_explore_gate_stairs` | On **^** before hub (skip if `s1_b1f_gate_briefing_seen`) | `interact` | If briefing skipped: “Stairs lead topside. **Interact** to go up.” Else: “**Interact** — stairs up.” |

**Story VN (Act 1):** [s1_b1f_gate_briefing](../story-events/s1/s1_b1f_gate_briefing.md) on Event cell **`!` `(10, 9)`** — fires before row 4; Navigator copy owns hub report fiction.

**Codex:** each completed entry unlocks under category `basics` (four rows in codex for Act 1).

**On complete:** set `s1_intro_movement_complete`; transition **Exploration → Hub** ([game-phase](../../02-systems/game-phase.md)).

**Not coached at launch:** map fullscreen (`M`) — defer until [explore HUD #36](https://github.com/miramocha/griddungeon-game/issues/36).

---

## Act 2 — Party (Hub)

**Launch:** no guided entries — guild UI + service motion only ([ADR 029](../../decisions/029-guided-tutorial.md#stakeholder-decisions-2026-05-23)). Revisit if playtest shows Act 2 confusion.

**Navigator framing (S1 copy pass):** Launch presents **one** Navigator identity (`guild_handler`) on the sideline with the crew. **Navigator Office** teaches **tool / Protocol kit** options (different Synchro skills), not a roster of alternate Navigator characters — see [navigator § Active Navigator](../../02-systems/navigator.md#active-navigator). Optional 1–2 hub asides TBD when Act 2 lines are drafted.

---

## Act 3 — Combat (B2F `foe_alley_stalker`)

**Rules authority:** [synchro § S1 gating](../../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe) · [foe tutorial](../../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker).

VN scripts: [s1_b2f_stalker_briefing](../story-events/s1/s1_b2f_stalker_briefing.md), [s1_synchro_protocol_unlock](../story-events/s1/s1_synchro_protocol_unlock.md), [s1_tutorial_hub_return](../story-events/s1/s1_tutorial_hub_return.md).

### Phase map (exploration + combat)

| Phase | Rules (summary) | Story VN | Guided hint |
|-------|-----------------|----------|-------------|
| **0 — Approach** | Event cell on B2F west loop | **`s1_b2f_stalker_briefing`** → starts tutorial combat | — |
| **A — Opening** | Synchro locked; FOE unbeatable | — | — |
| **B — Crisis** | 2 core turns **or** FOE at HP floor → crisis AOE → party at 1 HP | — | — |
| **C — Unlock** | — | `s1_synchro_protocol_unlock` | — |
| **D — Protocol** | Only `protocol_strike` | — | **`s1_combat_guided_protocol`** |
| **E — Finisher** | Protocol kills FOE | — | — |
| **F — Hub outro** | Warp hub | `s1_tutorial_hub_return` | — |

### Guided hint — Protocol coach

| Field | Value |
|-------|-------|
| `tutorialEntryId` | `s1_combat_guided_protocol` |
| `mode` | `combat` |
| `codexCategory` | `synchro` |
| `once` | yes (per save) |
| `prerequisiteFlags` | `s1_synchro_unlocked` |
| `highlight` | `combat.command.protocol`, `combat.synchro_meter` |
| `completion` | `combat_command` → `protocol_strike` queued and confirmed |
| **Pages (draft)** | p1: “Synchro is full.” p2: “Open **Protocol** → **Protocol Strike**.” (+ still: meter screenshot) |

**Start:** story effect `start_guided_protocol` on last step of `s1_synchro_protocol_unlock`.  
**End:** clear highlight when `protocol_strike` begins resolve; set `s1_synchro_protocol_tutorial_done` on kill.

**Pre-fight:** **story VN** on Event cell (phase **0**); no guided HUD until post-crisis. Player may use normal commands in combat until crisis (**phase A**). FOE grid contact still starts the same tutorial if the Event was skipped.

---

## Flag cross-reference

| Flag | Guided / story relevance |
|------|--------------------------|
| `s1_b1f_gate_briefing_seen` | Act 1 gate VN done; shortens `s1_explore_gate_stairs` |
| `s1_intro_movement_complete` | Suppresses all Act 1 explore hints |
| `s1_party_ready` | Enables `s1_hub_enter_stratum` |
| `s1_tutorial_dive_started` | Act 3 B1F blockers cleared |
| `s1_b2f_stalker_briefing_seen` | B2F approach VN done; optional analytics / bypass guard |
| `s1_synchro_unlocked` | Prerequisite for `s1_combat_guided_protocol` |
| `s1_synchro_protocol_tutorial_done` | Protocol coach done |
| `s1_first_foe_tutorial_complete` | Hub return VN done; B3F unblocked |

---

## Implementation checklist at launch

- [ ] `GuidedTutorialDefinition` content for table above
- [ ] Act 1 triggers on `s1_B1F` intro mode (spawn, bump, cells G/C/^)
- [ ] `s1_combat_guided_protocol` wired from `start_guided_protocol` ([#88](https://github.com/miramocha/griddungeon-game/issues/88))
- [x] Protocol-only command gate — `CombatTutorialHudRules` + `CombatController` ([#35](https://github.com/miramocha/griddungeon-game/pull/35))
- [ ] Guided coach UI (`s1_combat_guided_protocol`) — [#88](https://github.com/miramocha/griddungeon-game/issues/88)
- [ ] Playtest: Act 1 ≤ 8 min with hints; B2F crisis → Protocol path not soft-lockable

---

## Related

- [guided-tutorial.md](../../02-systems/guided-tutorial.md)
- [s1-intro.md](s1-intro.md)
- [story-events index](../story-events/README.md)
