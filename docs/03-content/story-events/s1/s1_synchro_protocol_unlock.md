# Draft — `s1_synchro_protocol_unlock`

**Status:** Copy draft — **Navigator-only** lines (no `npc:*` yet); **first mechanic reveal**; MVP1 = click-through block.

**When:** After FOE **crisis AOE** (party all at **1 HP**) UI beat completes — not on raw crisis trigger.

**Prerequisite:** B2F tutorial FOE; crisis already fired.

**Narrative job:** Navigator **discovers** the channel burst and hears **Synchro / Protocol** as labels for the first time — still no full backstory.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_synchro_unlocked = true`
- `set_synchro_charge` → `100`
- `start_guided_protocol` → `protocol_strike` only

---

## Script (placeholder — `textKey` + `textEn`)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.synchro_unlock.line_01` | That should've dropped your line. It didn't. |
| `story.s1.synchro_unlock.line_02` | There's a pulse in the channel — I didn't know I had it until now. Paperwork calls it **Synchro**. One coordinated shot when it peaks. |
| `story.s1.synchro_unlock.line_03` | It's lining up. When your turn hits, open **Protocol** — I'll push **Protocol Strike** through. |
| `story.s1.synchro_unlock.line_04` | One strike. I don't think we get another window at this range. |

Speaker: **`navigator:guild_handler`** only.

**Preceding beat (combat, not VN):** FOE crisis AOE — log/VFX only; no FOE dialogue required.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md#blank-state-locked)
- [s1_b2f_stalker_briefing](s1_b2f_stalker_briefing.md) — exploration Event cell before this fight
- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [Guided Protocol coach](../../campaign/s1-guided-tutorials.md#guided-hint--protocol-coach) — HUD after this event
- [s1_tutorial_hub_return](s1_tutorial_hub_return.md)
