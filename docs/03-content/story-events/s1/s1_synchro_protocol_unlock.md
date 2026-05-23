# Draft — `s1_synchro_protocol_unlock`

**Status:** Copy draft — Navigator only; MVP1 = click-through block.

**When:** After FOE **crisis AOE** (party all at **1 HP**) UI beat completes — not on raw crisis trigger.

**Prerequisite:** B2F tutorial FOE; crisis already fired.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_synchro_unlocked = true`
- `set_synchro_charge` → `100`
- `start_guided_protocol` → `protocol_strike` only

---

## Script (placeholder — `textKey` + `textEn`)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.synchro_unlock.line_01` | That blast should have ended you. It didn’t — because the channel’s still open. |
| `story.s1.synchro_unlock.line_02` | That’s **Synchro**. My link to your whole crew. One coordinated shot while the bar is full. |
| `story.s1.synchro_unlock.line_03` | I’m charging **Protocol Strike**. When your turn comes, open **Protocol** and confirm. |
| `story.s1.synchro_unlock.line_04` | Hit it once. Hard. We don’t get a second chance at this range. |

Speaker: **`navigator:guild_handler`** only.

**Preceding beat (combat, not VN):** FOE crisis AOE — log/VFX only; no FOE dialogue required.

---

## Related

- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [Guided Protocol coach](../../campaign/s1-guided-tutorials.md#guided-hint--protocol-coach) — HUD after this event
- [s1_tutorial_hub_return](s1_tutorial_hub_return.md)
