# Story event content index

**System:** [story-events.md](../../02-systems/story-events.md) · **ADR:** [028](../../decisions/028-story-visual-novel-events.md) (Proposed)

Authoring drafts live in subfolders (`s1/`, …). Game repo imports to `Assets/Content/StoryEvents/` when implementation starts.

## MVP1 — Stratum 1

| storyEventId | once | Prerequisite | Trigger | Status |
|--------------|------|--------------|---------|--------|
| `s1_synchro_protocol_unlock` | yes | not `s1_synchro_unlocked` | After crisis AOE UI beat | [draft](s1/s1_synchro_protocol_unlock.md) |
| `s1_tutorial_hub_return` | yes | `s1_synchro_protocol_tutorial_done` | After Protocol kills FOE | [draft](s1/s1_tutorial_hub_return.md) |

## Post-MVP1 (placeholders)

| storyEventId | Notes |
|--------------|-------|
| `s2_navigator_unlock_*` | Per Navigator unlockCondition |
| `explore_event_*` | Tile Event cells |
