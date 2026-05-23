# Story event content index

**System:** [story-events.md](../../02-systems/story-events.md) · **ADR:** [028](../../decisions/028-story-visual-novel-events.md) (Proposed)

Authoring drafts live in subfolders (`s1/`, …). Game repo imports to `Assets/Content/StoryEvents/` when implementation starts.

## MVP1 — Stratum 1

| storyEventId | once | Prerequisite | Trigger | Status |
|--------------|------|--------------|---------|--------|
| `s1_synchro_protocol_unlock` | yes | `s1_tutorial_dive_started`; not `s1_synchro_unlocked` | B2F FOE — Phase B: 2 core turns **or** FOE HP floor (first) | MVP1 click-block — [draft](s1/s1_synchro_protocol_unlock.md) |
| `s1_foe_stalker_intro` | — | — | — | **Not MVP1** |
| `s1_foe_stalker_retreat` | — | — | — | **Not MVP1** |

## Post-MVP1 (placeholders)

| storyEventId | Notes |
|--------------|-------|
| `s2_navigator_unlock_*` | Per Navigator unlockCondition |
| `explore_event_*` | Tile Event cells |
