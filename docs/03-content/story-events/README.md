# Story event content index

**System:** [story-events.md](../../02-systems/story-events.md) · **ADR:** [028](../../decisions/028-story-visual-novel-events.md) (Proposed) · **Graph authoring (follow-up):** [030](../../decisions/030-story-event-graph-authoring.md) · **Implementation:** [game #87](https://github.com/miramocha/griddungeon-game/issues/87)

Authoring drafts live in subfolders (`s1/`, …). Game repo imports to `Assets/Content/StoryEvents/` when implementation starts. Post-MVP1: optional graph editor per [ADR 030](../../decisions/030-story-event-graph-authoring.md) compiles to the same step format.

## MVP1 — Stratum 1

| storyEventId | once | Prerequisite | Trigger | Status |
|--------------|------|--------------|---------|--------|
| `s1_b1f_mouth_briefing` | yes | Act 1; not `s1_intro_movement_complete` | **Exploration:** Event cell on `s1_B1F` `(9, 10)` — before first hub | [draft](s1/s1_b1f_mouth_briefing.md) |
| `s1_b2f_stalker_briefing` | yes | `s1_tutorial_dive_started`; not `s1_first_foe_tutorial_complete` | **Exploration:** Event cell on `s1_B2F` `(7, 11)` → VN → tutorial combat | [draft](s1/s1_b2f_stalker_briefing.md) |
| `s1_synchro_protocol_unlock` | yes | not `s1_synchro_unlocked` | **Combat:** after crisis AOE UI beat | [draft](s1/s1_synchro_protocol_unlock.md) |
| `s1_tutorial_hub_return` | yes | `s1_synchro_protocol_tutorial_done` | **Combat:** after Protocol kills FOE | [draft](s1/s1_tutorial_hub_return.md) |

## Post-MVP1 (placeholders)

| storyEventId | Notes |
|--------------|-------|
| `s2_navigator_unlock_*` | Per Navigator unlockCondition |
| `explore_event_*` | Tile Event cells |
