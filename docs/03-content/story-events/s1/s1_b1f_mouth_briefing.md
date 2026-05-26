# Draft — `s1_b1f_mouth_briefing`

**Status:** Copy draft — Navigator only, **blank state**; MVP1 = click-through block.

**When:** **Exploration Act 1** — party enters the authored **Event** cell **`!` `(10, 9)`** on `s1_B1F` (mouth camp threshold), **before** first **hub** via mouth `^` `(10, 11)`.

**Prerequisite:** Act 1 movement path (not `s1_intro_movement_complete`); not already `s1_b1f_mouth_briefing_seen`.

**Narrative job:** Instinct to report topside — **no** Synchro / Protocol / role title. Navigator does not know who they are.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_b1f_mouth_briefing_seen = true`
- *(none)* — player continues on foot to **`^`** → hub ([game phase § return](../../02-systems/game-phase.md#return-to-hub-exploration-only))

**Act 3:** same cell **`(10, 9)`** is **skipped** (`once` + flag); dive spawns at mouth **`(10, 11)`** without re-playing.

---

## Script (placeholder — `textKey` + `textEn`)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.b1f_mouth.line_01` | Static on the line — and stairs up ahead. Something's pulling toward a surface channel I don't have a name for yet. |
| `story.s1.b1f_mouth.line_02` | There's a tag in my kit I can't read. Report in before we go deeper. That's the only part that feels true. |
| `story.s1.b1f_mouth.line_03` | Your crew moves when you're ready. I'll keep the channel open. |

Speaker: **`navigator:guild_handler`** only.

**Following beat:** optional short guided hint on **`^`** interact ([s1_explore_mouth_stairs](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)) if player skipped the Event tile; otherwise stairs-only prompt.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md)
- [Act 1 guided movement](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)
- [s1-intro § Act 1](../../campaign/s1-intro.md#three-acts-same-s1_b1f-map)
- [dungeons — s1_B1F Event cell](../dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--mouth)
