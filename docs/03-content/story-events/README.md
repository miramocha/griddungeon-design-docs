---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/active
  - domain/story-vn
  - domain/campaign/s1
---
# Story event content index

**System:** [story-events.md](../../02-systems/story-events.md) · **ADR:** [028](../../../decisions/028-story-visual-novel-events.md) (Proposed) · **Graph authoring (follow-up):** [030](../../../decisions/030-story-event-graph-authoring.md) · **Implementation:** [game #87](https://github.com/miramocha/griddungeon-game/issues/87)

Authoring drafts live in subfolders (`s1/`, …). **Game sync:** `griddungeon-game` → `Assets/Content/StoryEvents/<storyEventId>.asset` (regen menu: **GridDungeon → Content → Ensure MVP1 S1 Story Events**). Edit drafts here first, then menu/assets. Later: optional graph editor per [ADR 030](../../../decisions/030-story-event-graph-authoring.md) compiles to the same step format.

**Voice (locked):** [narrative POV](../../02-systems/narrative-pov.md) — player is the Navigator (**first person** on `navigator:guild_handler` steps); **`npc:*` may speak to the Navigator** when a beat needs it; **no `core:` speakers**. **Act 1 solo**, then **sideline** with crew after hub recruit; *Amnesia*-style **blank state**; no Synchro / Protocol until unlock beat. **Launch table below:** Navigator-only drafts until NPC lines are authored.

## Stratum 1 at launch

| storyEventId                 | once | Prerequisite                                                                 | Trigger                                                                  | Copy                                       |
| ---------------------------- | ---- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------ |
| `s1_b1f_gate_briefing`       | yes  | Act 1; not `s1_intro_movement_complete`                                      | **Exploration:** Event cell on `s1_B1F` `(10, 9)` — before first hub     | [synced](s1/s1_b1f_gate_briefing.md)       |
| `s1_b2f_stalker_briefing`    | yes  | `s1_tutorial_dive_started` *(planned)*; not `S1_FIRST_FOE_TUTORIAL_COMPLETE` | **Exploration:** Event cell on `s1_B2F` `(7, 11)` → VN → tutorial combat | [synced](s1/s1_b2f_stalker_briefing.md)    |
| `s1_synchro_protocol_unlock` | yes  | not `S1_SYNCHRO_UNLOCKED`                                                    | **Combat:** after crisis AOE UI beat                                     | [synced](s1/s1_synchro_protocol_unlock.md) |
| `s1_tutorial_hub_return`     | yes  | tutorial FOE fight (`grp_alley_stalker_tutorial`)                            | **Combat:** victory after `protocol_strike` kill → hub warp              | [synced](s1/s1_tutorial_hub_return.md)     |

## Later (placeholders)

| storyEventId | Notes |
|--------------|-------|
| `s2_navigator_unlock_*` | Per Navigator unlockCondition |
| `explore_event_*` | Tile Event cells |
