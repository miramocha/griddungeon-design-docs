# ADR 029 — Guided Tutorial (player coaching)

> **Scope: Optional feature** — not required for initial release.

**Status:** Accepted (2026-05-23)  
**Date:** 2026-05-23  
**First consumer:** S1 — Act 1 B1F movement hints; B2F `s1_combat_guided_protocol` after Synchro unlock VN  
**Aligns with:** [ADR 017](017-game-phase-controller.md) (macro phases), [ADR 028](028-story-visual-novel-events.md) (story VN — **handoff, not merge**), [ADR 027](027-combat-cinematic-timeline-events.md) (skill cinematics — **orthogonal**), [04 — Tech notes § UI reactivity](../docs/04-tech-notes.md#ui-reactivity)

## Context

Grid Dungeon needs **short, actionable coaching** that teaches controls without autoplaying the game:

- **Exploration (S1 Act 1):** movement, wall bump, optional gather/signage, gate stairs — map stays visible; player keeps (or regains) movement between dismissible lines.
- **Combat (S1 B2F):** after Navigator **story** lines, pulse **Protocol** and **gate** commands until the player confirms `protocol_strike`.

Today these beats are specified across [synchro-protocol](../docs/02-systems/synchro-protocol.md), [story-events](../docs/02-systems/story-events.md), and [game #35](https://github.com/miramocha/griddungeon-game/issues/35) (Synchro HUD — done) without a named **coach** owner. Implementation: [#88](https://github.com/miramocha/griddungeon-game/issues/88). Hard-coding strings in `CombatHudView` duplicates [ADR 028](028-story-visual-novel-events.md) **dialogue** ([#87](https://github.com/miramocha/griddungeon-game/issues/87)).

**Not in scope**

- Multi-line narrative (→ [ADR 028](028-story-visual-novel-events.md)).
- Skill Timeline clips (→ [ADR 027](027-combat-cinematic-timeline-events.md)).
- Campaign **rules** (blockers, crisis AOE, unbeatable FOE) — stay in Core / `CombatController` / save flags.

## Decision (proposed)

### 1. One system: `GuidedTutorial` + coach presenter

| Piece | Owner | Responsibility |
|-------|--------|----------------|
| **`GuidedTutorialDefinition`** | Content (`Assets/Content/GuidedTutorials/`) | `hintId`, mode, copy keys, highlights, completion rule |
| **`GuidedTutorialSequence`** (optional) | Content | Ordered hints for one beat (e.g. Act 1 gate approach) |
| **`GuidedTutorialController`** | Runtime | Start/complete hints, completion rules, **invoke** gates via combat/explore APIs |
| **`GuidedTutorialView`** | UI | Banner, target pulses, disabled chrome ([#88](https://github.com/miramocha/griddungeon-game/issues/88)) |

**Player-facing name:** “Tip” or brief on-screen coach text — not “tutorial mode.”

### 2. Do **not** add a fourth macro `GamePhase`

Same as [ADR 028](028-story-visual-novel-events.md): stay **`Hub | Exploration | Combat`**.

While a **blocking** combat hint is active:

- **`GamePhase`** stays `Combat`.
- **`GuidedTutorialController`** + **`CombatController`** command gate share a **presentation / input lock** for disallowed commands only.
- **Story events** may run immediately before (VN lock) or after (none) — never overlap VN and mandatory combat coach.

**Rejected:** `GamePhase.Tutorial`; merging guided hints into `StoryEventRunner` (different copy length, skip policy, and completion rules).

### 3. Three layers (locked separation)

| Layer | Owner | S1 example |
|-------|--------|------------|
| **Rules** | `CombatController`, campaign resolvers, floor data | Crisis AOE, `tutorialUnbeatable`, walk blockers |
| **Story (VN)** | `StoryEventRunner` | `s1_b1f_gate_briefing`, `s1_b2f_stalker_briefing`, `s1_synchro_protocol_unlock`, `s1_tutorial_hub_return` |
| **Guided coach** | `GuidedTutorialController` | `s1_explore_intro_move`, `s1_combat_guided_protocol` |

**Handoff (locked):** story effect `start_guided_protocol` → sets combat tutorial phase + `GuidedTutorialController.Start("s1_combat_guided_protocol")`. VN must **complete** before coach starts.

### 4. Modes and presentation (stakeholder 2026-05-23)

| Mode | `GamePhase` | In-world presentation | Input while active |
|------|-------------|----------------------|-------------------|
| **Exploration** | `Exploration` | **Paginated screen block** — text + image/video slot per page; player flips pages (Z / click) | **Blocking** — no movement until player exits the block |
| **Combat** | `Combat` | Same **page block** for copy **or** compact banner + HUD pulse for Protocol-only coach | **Blocking** for mandatory S1 Protocol coach |
| **Hub** | `Hub` | Same page block when used | **Blocking** while open |

**Early MVP simplification:** one reusable **tutorial panel** layout (screen block + optional still / short clip) for Act 1 and combat coach — not a separate “toast” stack and VN chrome. Full portrait VN remains [ADR 028](028-story-visual-novel-events.md).

**Rejected:** Act 1 as ephemeral corner-only banners with movement continuing (superseded by paginated block). Act 1 **fully** as **`storyEventId`** scenes for every movement beat.

**Exception (locked):** **`s1_b1f_gate_briefing`** — single Event-cell VN before first hub; all other Act 1 beats stay guided pages ([s1-guided-tutorials § Act 1](../docs/03-content/campaign/s1-guided-tutorials.md#act-1--movement-b1f)).

### 5. Codex (replay — stakeholder 2026-05-23)

**Yes — still “guided tutorial.”** The **codex** is the **menu UI** that lists unlocked **tutorial entries**; it does not replace `GuidedTutorialController`.

| Piece | Role |
|-------|------|
| **`GuidedTutorialDefinition`** | Authoring: pages, media refs, `hintId` / `tutorialEntryId` |
| **In-world play** | `GuidedTutorialController` shows the block when triggered |
| **`TutorialCodex`** (UI + save) | Index of entries the player has **seen**; read-only replay, no re-apply of combat gates |

**Unlock rule:** completing (or fully paging through) an in-world tutorial adds `tutorialEntryId` to save (`unlockedCodexTutorialIds` or equivalent). Codex does **not** re-run `set_campaign_flag` / `start_guided_protocol`.

**Story events vs codex:** Navigator **story** scenes ([ADR 028](028-story-visual-novel-events.md)) may optionally add a codex entry later — **not required at launch S1 unlock/outro**. launch codex content = **guided tutorial entries** from [s1-guided-tutorials](../docs/03-content/campaign/s1-guided-tutorials.md).

**Hub Act 2:** guild / Enter Stratum coach hints **cut at launch** unless playtest fails ([stakeholder](#stakeholder-decisions-2026-05-23)).

### 6. Page schema (draft)

| Field | Notes |
|-------|-------|
| `tutorialEntryId` | Stable id (may equal `hintId`); codex row key |
| `pages[]` | Ordered `{ textKey, imageId? }` per page — **`videoId` reserved**; **stills only** at launch |
| `mode` | `exploration` \| `combat` \| `hub` \| `codex_only` (later) |
| `codexCategory` | e.g. `basics`, `combat`, `synchro` — for menu grouping |

Advance: **Z** or click — same as [ADR 028](028-story-visual-novel-events.md) story advance. Last page dismiss ends in-world block.

### 7. Command gating (combat — locked)

**Truth** lives in `CombatController` (or Core helper it calls), not in the view:

- While `s1_combat_guided_protocol` is active, only **`protocol_strike`** may be queued/confirmed.
- View **reflects** allowed commands (grey/disable + pulse Protocol).
- Finisher clears guided state → story event `s1_tutorial_hub_return`.

Aligns with [game #10](https://github.com/miramocha/griddungeon-game/issues/10): tutorial fight via `EncounterGroupId` (`grp_alley_stalker_tutorial`) + `CombatTutorialHudRules` (not a `TutorialCombatKind` field on `CombatEntryContext`).

### 8. Triggers

| Context | Trigger owner | Example |
|---------|---------------|---------|
| **Exploration** | `ExplorationPhaseController` / floor `OnPartyEnteredCell` / first bump | Act 1 hint table |
| **Combat** | `CombatController` tutorial phase + story effect | After unlock VN |
| **Hub** | `HubPhaseController` when flag transitions | `s1_hub_enter_stratum` (optional) |

Content authority: [s1-guided-tutorials.md](../docs/03-content/campaign/s1-guided-tutorials.md).

### 9. Completion rules (schema)

| `completion` | Use |
|--------------|-----|
| `dismiss` | Player confirm / click banner |
| `move` | Enter target cell |
| `bump_wall` | First wall bump |
| `interact` | Interact on feature |
| `combat_command` | Allowed command queued (`protocol_strike` for S1) |

**Once-seen (in-world):** on complete, add `tutorialEntryId` to codex unlock list **and** set campaign flags when the beat gates progression (`s1_intro_movement_complete`, etc.). Do not rely on codex alone for gating.

### 10. Highlight target ids at launch — combat coach)

Stable string ids consumed by `GuidedTutorialView` — see [guided-tutorial § highlights](../docs/02-systems/guided-tutorial.md#highlight-targets-mvp1).

Add new ids via ADR appendix or system doc amendment — no ad-hoc transforms in views.

### 11. Orthogonal: guided vs story vs cinematic

| | **Guided (this ADR)** | **Story ([ADR 028](028-story-visual-novel-events.md))** | **Cinematic ([ADR 027](027-combat-cinematic-timeline-events.md))** |
|---|----------------------|-----------------------------------------------------------|---------------------------------------------------------------------|
| **Purpose** | Coach next input | Narrative dialogue | Skill spectacle |
| **Typical UI** | Paginated screen block (+ HUD pulse in combat) | Narrative VN block; portraits later | Timeline on skill |
| **Codex replay** | **Yes** — instructional entries | Optional later | No |
| **Blocks movement** | Yes while in-world block open | Yes (VN lock) | During clip |
| **Skip** | No on mandatory S1 combat coach | No on mandatory tutorial | Skip → base damage |

### 12. MVP scope

| Milestone | Deliverable |
|-----------|-------------|
| **Launch — S1 teach (shipped path)** | Story VN ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) + `CombatTutorialHudRules` Protocol-only gate ([#35](https://github.com/miramocha/griddungeon-game/issues/35)); campaign rules unchanged |
| **Later — S1 Act 1** | Paginated tutorial entries per [s1-guided-tutorials § Act 1](../docs/03-content/campaign/s1-guided-tutorials.md#act-1--movement-b1f); unlock codex rows on complete ([#88](https://github.com/miramocha/griddungeon-game/issues/88)) |
| **Later — S1 B2F** | `s1_combat_guided_protocol` coach after `s1_synchro_protocol_unlock` (in addition to HUD gate) |
| **Later — Codex UI** | Read-only replay — **Pause menu** row (`Esc`; exploration, combat, hub) |
| **Later — Hub** | Guild / Enter Stratum coach only if playtest requires (was cut at launch) |
| **Deferred** | Map-key entry; full codex categories; story scenes in codex |
| **Later** | S2+ entries, tile triggers, boss mechanic pages |

**Save / replay:** Same as [ADR 028](028-story-visual-novel-events.md) — inn at hub only; do not replay Act 1 hints when `s1_intro_movement_complete`.

### 13. Testing (game repo — when implemented)

- **Edit Mode:** `GuidedTutorialControllerTests` — given hint def + mock campaign, assert completion fires once, gate callbacks invoked.
- **Play Mode:** DevBootstrap F2 (Act 1) + F3 (forced guided Protocol after crisis) — checklist in [#88](https://github.com/miramocha/griddungeon-game/issues/88).

## Rejected

| Option | Why |
|--------|-----|
| Strings only in `CombatHudView` / explore HUD | Not reusable; splits coaching from content |
| `GamePhase.Tutorial` | Same rejection as ADR 028 |
| View-only disable (no `CombatController` gate) | Player could queue illegal commands via input edge cases |
| Corner-only toast coach for Act 1 | Superseded — paginated block + codex is the teaching surface |
| Merge into `StoryEventRunner` | Different completion, skip, and layout; bloats step schema |
| `Cinematic` for Protocol coach | [ADR 028](028-story-visual-novel-events.md) §7 — Protocol teach is not a skill clip |

## Consequences

- **Design:** [guided-tutorial.md](../docs/02-systems/guided-tutorial.md) (system); [s1-guided-tutorials.md](../docs/03-content/campaign/s1-guided-tutorials.md) (beats).
- **Content:** `Assets/Content/GuidedTutorials/` + campaign beat table.
- **Runtime:** `GuidedTutorialController`, `GuidedTutorialView`; `StoryEventRunner` effect `start_guided_protocol` delegates here.
- **Issues:** [#88](https://github.com/miramocha/griddungeon-game/issues/88) — coach; [#87](https://github.com/miramocha/griddungeon-game/issues/87) — story VN; [#20](https://github.com/miramocha/griddungeon-game/issues/20) — S1 wiring.
- **Class design:** Add types to [05 — class design](../docs/05-class-design.md).

## Stakeholder decisions (2026-05-23)

| Topic | Decision |
|-------|----------|
| Act 1 presentation | **Paginated screen block** — text + **still** per page (no video at launch) |
| Codex placement | **Pause menu** — `Esc` from exploration, combat, or hub ([input bindings](../docs/02-systems/input-bindings.md)) |
| launch media | **Stills only** — schema may reserve `videoId` for later |
| Act 1 G + C | **One** entry `s1_explore_route_features` (signage + gather); not separate codex rows |
| Shared panel UXML | **Undecided** — implement `GuidedTutorialView` first ([#88](https://github.com/miramocha/griddungeon-game/issues/88)); revisit sharing with `StoryEventView` ([#87](https://github.com/miramocha/griddungeon-game/issues/87)) |
| Act 1 input | **Blocking** while block is open (flip pages, then dismiss) |
| Naming | Instructional beats stay **guided tutorial**; **codex** = replay UI for unlocked entries |
| Codex | Unlock on complete / full read; **no** re-apply of combat gates or flags on replay |
| Hub Act 2 hints | **Cut at launch** unless playtest fails |
| Combat Protocol coach | **Blocking** + command gate; may use same page block for copy + HUD pulse |
| **Launch full coach + codex** | **Deferred** (2026-06-03) — [#88](https://github.com/miramocha/griddungeon-game/issues/88); launch relies on VN + `CombatTutorialHudRules` only ([release scope § Later](../docs/00-release-scope.md#later)) |
| Progression storage | **Campaign flags** for gates + **codex unlock list** for replay index |
| Story vs guided | **S1 unlock/outro** remain **story events** ([ADR 028](028-story-visual-novel-events.md)); Act 1 movement + Protocol coach = **guided** |

## Open questions (deferred)

1. **Act 1 — teach map (`M`)** — defer until explore HUD [#36](https://github.com/miramocha/griddungeon-game/issues/36).
2. **Shared `TutorialPanel.uxml` with story layer** — undecided; pick during #87 / #88 implementation.
3. **Authoring** — YAML vs ScriptableObject (defer with [ADR 028](028-story-visual-novel-events.md)).

## Related

- [Guided tutorial (system doc)](../docs/02-systems/guided-tutorial.md)
- [ADR 028 — Story events](028-story-visual-novel-events.md)
- [ADR 027 — Combat cinematics](027-combat-cinematic-timeline-events.md)
- [S1 guided tutorials (content)](../docs/03-content/campaign/s1-guided-tutorials.md)
- [Game #88 — Guided tutorials](https://github.com/miramocha/griddungeon-game/issues/88)
- [Game #87 — Story events](https://github.com/miramocha/griddungeon-game/issues/87)
- [Game #35 — Combat reactive + Synchro tutorial UI](https://github.com/miramocha/griddungeon-game/issues/35) (done)
