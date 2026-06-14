# ADR 028 — Story Events (Visual Novel Presentation)

**Status:** Proposed (decisions locked 2026-05-23 — UI-retract detail open; implementation [#87](https://github.com/miramocha/griddungeon-game/issues/87))  
**Date:** 2026-05-23  
**First consumer:** S1 — four scenes (B1F / B2F Event cells + mid-combat unlock + hub outro) ([story-events](../docs/02-systems/story-events.md), [game #87](https://github.com/miramocha/griddungeon-game/issues/87))  
**Aligns with:** [ADR 017](017-game-phase-controller.md) (macro phases), [ADR 027](027-combat-cinematic-timeline-events.md) (combat skill cinematics — **orthogonal**), [04 — Tech notes § UI reactivity](../docs/04-tech-notes.md#ui-reactivity)

## Context

Grid Dungeon needs **scripted narrative beats** that:

- Pause normal input and show **character-forward dialogue** (visual-novel / ADV style): portraits, name plates, line-by-line text, optional choices.
- Run in **multiple contexts** — hub, exploration, and **mid-combat** (tutorial FOE is the first requirement).
- Stay **data-driven** and **testable** where rules touch campaign flags; presentation stays in Runtime/UI.
- Reuse one pipeline for S1 Protocol teaching and later beats (Navigator unlock scenes, tile **Event** fights, boss intros).

Today, S1 gating is specified in rules + flags ([synchro-protocol](../docs/02-systems/synchro-protocol.md), [s1-intro](../docs/03-content/campaign/s1-intro.md)) with “Navigator prompt” called out but **no shared presentation owner**. [Game #35](https://github.com/miramocha/griddungeon-game/issues/35) (done) covers Synchro meter + Protocol-only HUD; **story dialogue** ships in [#87](https://github.com/miramocha/griddungeon-game/issues/87). **HUD coaching** ships in [#88](https://github.com/miramocha/griddungeon-game/issues/88) ([ADR 029](029-guided-tutorial.md)).

**Not in scope for this ADR**

- **Combat skill cinematics** (`Cinematic` / `CinematicQTE`, Timeline, QTE) — [ADR 027](027-combat-cinematic-timeline-events.md).
- **Tile Event** encounter *rules* (no flee, rewards) — still [dungeons — Encounter types](../docs/03-content/dungeons-and-encounters.md#encounter-types); this ADR only covers **presentation + orchestration hooks**.
- Full **branching campaign** graph framework — defer until more than a handful of scenes.

## Decision (proposed)

### 1. One system: `StoryEvent` + VN presenter

| Piece | Owner | Responsibility |
|-------|--------|----------------|
| **`StoryEventDefinition`** | Content (`Assets/Content/StoryEvents/`) | Ordered **steps** (lines, choices, waits, side effects) |
| **`StoryEventRunner`** | Runtime (`GridDungeon.Runtime`) | Load script, advance steps, apply **effects**, signal completion |
| **`StoryEventView`** | UI (`GridDungeon.UI`) | Full-screen (or near full-screen) VN layout: portraits, text box, advance control |
| **Triggers** | Phase controllers / `CombatController` tutorial hooks | Start event by `storyEventId` when campaign/combat conditions match |

**Player-facing name:** “Story scene” or “Briefing” in UI copy — not required to say “visual novel.”

### 2. Do **not** add a fourth macro `GamePhase`

Macro flow stays **`Hub | Exploration | Combat`** ([ADR 017](017-game-phase-controller.md)).

While a story event runs:

- **`GamePhase` unchanged** (combat stays `Combat` during mid-fight tutorial).
- **`StoryEventRunner`** sets an **input / presentation lock** (same EO-style pattern as combat presentation lock — [04 — Tech notes](../docs/04-tech-notes.md#ui-reactivity)).
- Underlying sim **paused** (combat AGI queue does not advance; exploration steps blocked).

**Rejected at launch:** `GamePhase.Story` as a peer phase — would complicate save/resume, combat state, and `InputRouter` for little gain.

### 3. Step model (content schema)

Minimum step kinds for **(launch) + S1 tutorial**:

| Step kind | Purpose |
|-----------|---------|
| `line` | Speaker id, body text, optional portrait emotion |
| `wait` | Auto-advance after `durationSec` (optional) |
| `choice` | 1–N branches → jump to step index or nested `branchId` |
| `effect` | Side effect only (no line) — see §4 |

**Later (optional):** `bg`, `music`, `shake`, `illustration` full-screen still.

Authoring format: **YAML or ScriptableObject** referencing text keys — **TBD** ([Open questions](#open-questions)).

### 4. Effects (scripted, not player-visible)

`StoryEventRunner` executes **effects** declared on steps or choices. Effects call existing systems — no duplicate campaign logic in UI.

| Effect (draft id) | Example use |
|-------------------|-------------|
| `set_campaign_flag` | `s1_synchro_unlocked` |
| `set_synchro_charge` | Force 100% at Protocol tutorial unlock |
| `combat_tutorial_phase` | **Target** — advance S1 tutorial beat (campaign flags + `CombatController`; game #10 rules). Supersedes early `TutorialCombatKind` sketch on `CombatEntryContext`. |
| `unlock_input_hint` | Show combat HUD callout (may delegate to #35) |
| `start_combat_rule` | Resume AGI after scene ends |
| `start_guided_protocol` | HUD highlight + command gate (`protocol_strike`) |
| `start_combat` | After exploration Event VN — `RequestCombat` with tutorial group (`grp_alley_stalker_tutorial`) |
| `teleport_to_hub` | Script `Combat → Hub` after outro VN |
| `play_foe_crisis_aoe` | Scripted tutorial enemy action (rules-owned; optional story hook) |

**Rule:** Campaign **truth** stays in `CampaignSaveData` + `CombatController` / resolvers; story events only **invoke** documented APIs.

### 5. S1 Protocol tutorial — beat mapping (locked)

Full sequence: [story events § S1 tutorial flow](../docs/02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker). Aligns with [synchro § S1](../docs/02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe).

| Step | Combat / rules | Story / guided UI |
|------|----------------|-------------------|
| **0** Approach | Event cell on `s1_B2F` — west loop | **`s1_b2f_stalker_briefing`** → `start_combat` (before hub warp arc) |
| **A** Opening | Synchro locked; FOE `tutorialUnbeatable` | — |
| **B** Crisis trigger | **2 core turns** OR **FOE at HP floor** (first) | — |
| **C** Crisis AOE | FOE scripted attack → **all living core HP = 1** (fake wipe, no KO) | After AOE UI beat |
| **D** Unlock VN | `s1_synchro_unlocked`, Synchro 100% | **`s1_synchro_protocol_unlock`** |
| **E** Guided Protocol | Only `protocol_strike` allowed | HUD highlights ([#35](https://github.com/miramocha/griddungeon-game/issues/35)) — [guided-tutorial § combat](../docs/02-systems/guided-tutorial.md#combat-guided-tutorial-s1--protocol) |
| **F** Finisher | Protocol **kills** FOE; `s1_synchro_protocol_tutorial_done` | — |
| **G** Hub outro | Script **`Combat → Hub`** | **`s1_tutorial_hub_return`** → `s1_first_foe_tutorial_complete` |

**Not used:** FOE scripted **retreat** after Protocol; player does **not** resume exploration on B2F after this fight.

**Scene timing (locked):** each VN starts **after** the preceding combat UI beat (crisis AOE tween, Protocol resolve VFX).

**Speakers (locked):** **Navigator only** — [story-events § Speakers](../docs/02-systems/story-events.md#speakers-and-custom-party). **POV:** [narrative POV](../docs/02-systems/narrative-pov.md) — blank-state amnesia; first **named** Synchro beat = step **D** unlock VN, not Act 1 gate briefing.

### 6. Presentation — phased (locked)

| Milestone | UI | Notes |
|-----------|-----|--------|
| **(launch) (S1 unlock)** | **Click-through block** — full-screen panel, text, click or **Z** to advance/dismiss each step | No portraits required yet; same `StoryEventRunner` step pipeline |
| **Next** | Full VN layout (`StoryEvent.uxml`): portraits, name plate, line advance | Portrait **emotion** swaps supported in schema; **low art priority** |
| **Later** | Skip, auto-advance, back — **VN controls deferred** | No skip on tutorial at launch |

| Element | Rule |
|---------|------|
| **Background (combat)** | **Arena / battle view stays visible**; combat chrome may **retract** — which panels TBD ([open questions](#open-questions)) |
| **Advance** | **Z** (combat confirm) **or mouse click** on panel — no separate Story map at launch |
| **Skip** | **Disabled** at launch tutorial |
| **Act 1 B1F** | **One** Event-cell story scene before first hub (`s1_b1f_gate_briefing`); other beats = [ADR 029](029-guided-tutorial.md) guided pages + codex |

Exploration/hub: use same overlay pattern when content exists; Act 1 + B2F tutorial can land in either order — **implementation order deferred**.

### 7. Orthogonal: combat cinematics vs story scenes

| | **Story event (this ADR)** | **Skill cinematic ([ADR 027](027-combat-cinematic-timeline-events.md))** |
|---|---------------------------|---------------------------------------------------------------------------|
| **Trigger** | Campaign, tile, tutorial phase | Player confirms Attack/Skill/Protocol |
| **Content** | Dialogue steps + light effects | Timeline on skill prefab |
| **Outcome** | Flags, tutorial phase, unlocks | Damage / status resolve |
| **Skip policy** | Never skip mandatory tutorial effects without applying them | Skip → base tier damage |

A Protocol tutorial scene **must not** be implemented as a `Cinematic` skill clip.

### 8. Triggers (throughout game)

| Context | Trigger owner | Example |
|---------|---------------|---------|
| **Hub** | `HubPhaseController` / service script | Navigator unlock briefing |
| **Exploration** | Floor tile script / `OnPartyEnteredCell` | Event cell dialogue before fight |
| **Combat** | `CombatController` tutorial / boss script | S1 Synchro unlock |
| **Post-combat** | `OnBattleEnded` → runner | Short victory line (optional) |

Content table: `docs/03-content/story-events/` (new) — index of `storyEventId` → file, `once` flag, prerequisites.

### 9. MVP scope (locked / deferred)

| Milestone | Deliverable |
|-----------|-------------|
| **Launch** | Runner + click-through view; **`s1_b1f_gate_briefing`** (Act 1 Event → first hub) + **`s1_b2f_stalker_briefing`** (B2F Event → tutorial fight) + **`s1_synchro_protocol_unlock`** + **`s1_tutorial_hub_return`**; crisis AOE + guided Protocol + hub warp; **Z** or click advance |
| **(launch) schema** | `line` + `effect` steps; **`choice` / branching deferred** but schema reserves `gotoStep` + flag hooks for later |
| **(launch) content** | Navigator-only copy; **no VO** (schema may add optional `voClipId` later) |
| **Deferred** | Authoring format (YAML vs SO); hub/explore content beyond S1 |
| **Later** | Full VN portraits; Act 1 beats; skip/auto; exploration tile events; hub Navigator unlock scenes |

**Save / replay:** Inn save at hub only — no mid-fight save. Reloading during tutorial is out of scope; flags gate re-showing scenes.

### 10. Testing & implementation notes (for game repo — not done in this ADR pass)

- **Edit Mode:** `StoryEventRunnerTests` — given step list + mock campaign, assert flags/effects after `Complete()`.
- **Play Mode:** DevBootstrap — manual checklist in [#87](https://github.com/miramocha/griddungeon-game/issues/87).
- **Input:** While `StoryEventRunner.IsActive`, `InputRouter` routes to story map only ([ADR 009](009-input-bindings-pc.md) amendment when implemented).

## Rejected (draft)

| Option | Why |
|--------|-----|
| Hard-coded tutorial strings only in `CombatHudView` | Not reusable; duplicates portrait/text behavior |
| `GamePhase.Story` | Extra transition matrix; combat save mid-scene |
| Timeline as primary dialogue author | Wrong tool; no line-by-line advance without friction |
| UVS graph owning story logic | Same rejection as [ADR 017](017-game-phase-controller.md) for rules |
| Merge story scenes into ADR 027 cinematics | Different triggers, skip policy, and content lifecycle |

## Consequences

- **Design:** [story-events.md](../docs/02-systems/story-events.md) (system doc); update [synchro-protocol](../docs/02-systems/synchro-protocol.md), [s1-intro](../docs/03-content/campaign/s1-intro.md), [foe-encounters](../docs/02-systems/foe-encounters.md) with story-event ids.
- **Content:** `Assets/Content/StoryEvents/` + `docs/03-content/story-events/` index.
- **Runtime:** `StoryEventRunner`, `StoryEventView`; combat tutorial invokes runner instead of ad-hoc modal.
- **Issues:** [#87](https://github.com/miramocha/griddungeon-game/issues/87) (story runner + S1 content); [#88](https://github.com/miramocha/griddungeon-game/issues/88) (guided coach — handoff from `start_guided_protocol`).
- **Class design:** Add types to [05 — class design](../docs/05-class-design.md) when accepted.

## Stakeholder decisions (2026-05-23)

| Topic | Decision |
|-------|----------|
| Phase B trigger | **2 core turns** OR **FOE at HP floor** — first wins |
| Scene timing | After triggering action UI beat completes |
| (launch) UI | Click-through full-screen block (text + dismiss); full VN chrome later |
| Skip | None at launch; controls later |
| Combat backdrop | Arena visible; UI retract **TBD** |
| Speakers (S1) | Navigator only; no core dialogue (custom party) |
| Input | **Z** or click |
| Act 1 movement | **Guided tutorial** paginated block + codex ([ADR 029](029-guided-tutorial.md)); **one** Event-cell VN before first hub (`s1_b1f_gate_briefing`) |
| #35 split | **Resolved** — [#35](https://github.com/miramocha/griddungeon-game/issues/35) = combat reactive + Synchro HUD only; [#87](https://github.com/miramocha/griddungeon-game/issues/87) = story events |
| Branching | Deferred; schema should support flag branches later |
| VO | None planned yet |
| Localization | **Recommendation:** `textKey` on every line from day one; optional inline `textEn` (or default table) at launch authoring — see [story-events § Localization](../docs/02-systems/story-events.md#localization) |
| Mid-fight save replay | N/A (hub inn only) |

## Open questions

1. **Combat UI retract** — which panels hide during mid-combat story (command bar, AGI strip, Synchro meter reveal timing, etc.).
2. **Authoring pipeline** — YAML vs ScriptableObject (deferred).

Resolve UI retract before **Accepted** (implementation may proceed on [#87](https://github.com/miramocha/griddungeon-game/issues/87)).

## Related

- [ADR 030 — Story event graph authoring](030-story-event-graph-authoring.md) — follow-up; graph UI compiles to step list; does not block (launch)
- [ADR 029 — Guided tutorial (HUD coaching)](029-guided-tutorial.md) — orthogonal; `start_guided_protocol` handoff
- [Story events (system doc)](../docs/02-systems/story-events.md)
- [ADR 017 — Game phase controller](017-game-phase-controller.md)
- [ADR 027 — Combat cinematic timeline events](027-combat-cinematic-timeline-events.md)
- [Synchro Protocol — S1 tutorial gating](../docs/02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe)
- [S1 campaign intro](../docs/03-content/campaign/s1-intro.md)
- [Game #87 — Story events (StoryEventRunner + S1 scenes)](https://github.com/miramocha/griddungeon-game/issues/87)
- [Game #88 — Guided tutorials (coach layer)](https://github.com/miramocha/griddungeon-game/issues/88)
- [Game #35 — Combat reactive + Synchro tutorial UI](https://github.com/miramocha/griddungeon-game/issues/35) (done — HUD only)
