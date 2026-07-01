---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/synced
  - domain/campaign/s1
  - domain/story-vn
  - domain/synchro
---
# Draft — `s1_synchro_protocol_unlock`

**Synced:** with game `Assets/Content/StoryEvents/s1_synchro_protocol_unlock.asset` — **Navigator-only** (no `npc:*` yet); **first mechanic reveal**; Launch = click-through block.

**When:** After FOE **crisis AOE** (party all at **1 HP**) UI beat completes — not on raw crisis trigger.

**Prerequisite:** B2F tutorial FOE; crisis already fired.

**Narrative job:** Navigator **discovers** the kit burst and hears **Synchro / Protocol** as labels for the first time — still no full backstory.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `S1_SYNCHRO_UNLOCKED = true`
- `set_synchro_charge` → `100`
- `start_guided_protocol` → `protocol_strike` only

---

## Script (`textKey` + `textEn`)

| textKey | textEn |
|---------|--------|
| `story.s1.synchro_unlock.line_01` | s1_synchro_protocol_unlock Event Line 1 |
| `story.s1.synchro_unlock.line_02` | s1_synchro_protocol_unlock Event Line 2 |
| `story.s1.synchro_unlock.line_03` | s1_synchro_protocol_unlock Event Line 3 |
| `story.s1.synchro_unlock.line_04` | s1_synchro_protocol_unlock Event Line 4 |

Speaker: **`navigator:guild_handler`** only.

**Preceding beat (combat, not VN):** FOE crisis AOE — log/VFX only; no FOE dialogue required.

---

## Related

- [narrative POV](../../../02-systems/narrative-pov.md#blank-state-locked)
- [s1_b2f_stalker_briefing](s1_b2f_stalker_briefing.md) — exploration Event cell before this fight
- [S1 tutorial flow](../../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [Guided Protocol coach](../../campaign/s1-guided-tutorials.md#guided-hint--protocol-coach) — HUD after this event
- [s1_tutorial_hub_return](s1_tutorial_hub_return.md)
