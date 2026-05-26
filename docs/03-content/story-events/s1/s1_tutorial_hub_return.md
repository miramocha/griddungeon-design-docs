# Draft — `s1_tutorial_hub_return`

**Status:** **Synced** with game `Assets/Content/StoryEvents/s1_tutorial_hub_return.asset` — **Navigator-only** (no `npc:*` yet); post-discovery, still **no origin lore**; MVP1 = click-through block.

**When:** Immediately after **`protocol_strike`** resolves and FOE is removed (tutorial kill).

**Narrative job:** Confirm the pulse is real; topside rest — **defer** full identity / guild history to later content.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_first_foe_tutorial_complete = true`
- `teleport_to_hub` — scripted **`Combat → Hub`** (player does not walk out on B2F)

---

## Script (`textKey` + `textEn`)

| textKey | textEn |
|---------|--------|
| `story.s1.hub_return.line_01` | s1_tutorial_hub_return Event Line 1 |
| `story.s1.hub_return.line_02` | s1_tutorial_hub_return Event Line 2 |
| `story.s1.hub_return.line_03` | s1_tutorial_hub_return Event Line 3 |

Speaker: **`navigator:guild_handler`** only.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md)
- [s1_b2f_stalker_briefing](s1_b2f_stalker_briefing.md) — exploration Event cell before tutorial fight
- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [S1 intro — flags](../../campaign/s1-intro.md#save-flags-campaign)
