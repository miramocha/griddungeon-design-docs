# Draft — `s1_b2f_stalker_briefing`

**Status:** **Synced** with game `Assets/Content/StoryEvents/s1_b2f_stalker_briefing.asset` — **Navigator-only** (no `npc:*` yet), **blank state**; Launch = click-through block.

**When:** **Exploration Act 3** — party on the sideline enters the authored **Event** cell on `s1_B2F` `(7, 11)` (west-loop approach, before the tutorial fight).

**Prerequisite:** `s1_tutorial_dive_started`; not `s1_first_foe_tutorial_complete`.

**Narrative job:** Threat on the board + contract pressure — **no** Synchro tutorial; Navigator feels a **lock** they cannot open yet.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_b2f_stalker_briefing_seen = true` (optional replay guard; `once` on content row is authoritative)
- `start_combat` → `EncounterGroupId = grp_alley_stalker_tutorial`, `NoFlee = true` on `CombatEntryContext` (tutorial detect: `CombatTutorialHudRules.IsS1FirstFoeTutorial`; floor spawn: `TutorialFirstFoe` on `foe_alley_stalker`)

**Rejected:** FOE grid contact as the only tutorial entry — main path is **Event cell → VN → combat**. FOE patrol remains for map literacy; contact on `foe_alley_stalker` still starts the same tutorial fight if the player reaches the cell without firing the Event (anti-bypass).

---

## Script (`textKey` + `textEn`)

| textKey | textEn |
|---------|--------|
| `story.s1.b2f_briefing.line_01` | s1_b2f_stalker_briefing Event Line 1 |
| `story.s1.b2f_briefing.line_02` | s1_b2f_stalker_briefing Event Line 2 |
| `story.s1.b2f_briefing.line_03` | s1_b2f_stalker_briefing Event Line 3 |

Speaker: **`navigator:guild_handler`** only.

**Following beat:** normal tutorial combat opening (Synchro locked) — crisis AOE → unlock VN → guided Protocol → hub outro VN.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md)
- [s1_b1f_gate_briefing](s1_b1f_gate_briefing.md) — Act 1 Event cell before first hub
- [S1 tutorial flow](../../02-systems/story-events.md#s1-tutorial-flow-foe_alley_stalker)
- [archive — s1_B2F Event cell (draft)](../../archive/mvp1-s1-floor-layouts-draft.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)
- [s1_synchro_protocol_unlock](s1_synchro_protocol_unlock.md)
- [s1_tutorial_hub_return](s1_tutorial_hub_return.md)
