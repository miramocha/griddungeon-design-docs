# Draft — `s1_tutorial_hub_return`

**Status:** Copy draft — **Navigator-only** lines (no `npc:*` yet); post-discovery, still **no origin lore**; MVP1 = click-through block.

**When:** Immediately after **`protocol_strike`** resolves and FOE is removed (tutorial kill).

**Narrative job:** Confirm the pulse is real; topside rest — **defer** full identity / guild history to later content.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_first_foe_tutorial_complete = true`
- `teleport_to_hub` — scripted **`Combat → Hub`** (player does not walk out on B2F)

---

## Script (placeholder — `textKey` + `textEn`)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.hub_return.line_01` | It's down. I'm pulling your line to the surface channel before anything else stirs down here. |
| `story.s1.hub_return.line_02` | Whatever that pulse was — it's still on me. I'll learn the rest topside. For now: recharge it in a fight, hit **Protocol** when the bar tops out. |
| `story.s1.hub_return.line_03` | Rest at hub. When you're ready, we enter from the mouth again. |

Speaker: **`navigator:guild_handler`** only.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md)
- [s1_b2f_stalker_briefing](s1_b2f_stalker_briefing.md) — exploration Event cell before tutorial fight
- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [S1 intro — flags](../../campaign/s1-intro.md#save-flags-campaign)
