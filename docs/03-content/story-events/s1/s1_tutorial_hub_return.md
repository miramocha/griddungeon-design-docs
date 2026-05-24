# Draft — `s1_tutorial_hub_return`

**Status:** Copy draft — Navigator only; MVP1 = click-through block.

**When:** Immediately after **`protocol_strike`** resolves and FOE is removed (tutorial kill).

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_first_foe_tutorial_complete = true`
- `teleport_to_hub` — scripted **`Combat → Hub`** (player does not walk out on B2F)

---

## Script (placeholder — `textKey` + `textEn`)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.hub_return.line_01` | Target down. Pulling you back to guild channel before anything else wakes up down here. |
| `story.s1.hub_return.line_02` | **Synchro** stays on your roster from here. Recharge it in fights — use Protocol when the bar hits full. |
| `story.s1.hub_return.line_03` | Rest at the hub. When you’re ready, **Enter Stratum 1** again from the mouth. |

Speaker: **`navigator:guild_handler`** only.

---

## Related

- [s1_b2f_stalker_briefing](s1_b2f_stalker_briefing.md) — exploration Event cell before tutorial fight
- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [S1 intro — flags](../../campaign/s1-intro.md#save-flags-campaign)
