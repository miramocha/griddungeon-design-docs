# Draft — `s1_b1f_mouth_briefing`

**Status:** Copy draft — Navigator only, **blank state**; MVP1 = click-through block.

**When:** **Exploration Act 1** — Navigator enters the authored **Event** cell **`!` `(10, 9)`** on `s1_B1F` (mouth camp threshold), **solo**, **before** first **hub** via mouth `^` `(10, 11)`.

**Prerequisite:** Act 1 movement path (not `s1_intro_movement_complete`); not already `s1_b1f_mouth_briefing_seen`.

**Narrative job:** **Solo** recon — no crew yet (recruitment is Act 2 hub). Kit has **sealed tools** / latent power not usable yet. Instinct to report topside — **no** Synchro / Protocol / role title; **no** comms-or-“line” diction.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_b1f_mouth_briefing_seen = true`
- *(none)* — player continues on foot to **`^`** → hub ([game phase § return](../../02-systems/game-phase.md#return-to-hub-exploration-only))

**Act 3:** same cell **`(10, 9)`** is **skipped** (`once` + flag); dive spawns at mouth **`(10, 11)`** without re-playing.

---

## Script (sample v4 — `textKey` + `textEn`)

| textKey | textEn (sample) |
|---------|-----------------|
| `story.s1.b1f_mouth.line_01` | Stairs cut through to topside — and something in me is pulling toward a check-in I don't have words for yet. |
| `story.s1.b1f_mouth.line_02` | My kit's full of sealed tools. Whatever they do, it isn't ready down here — but topside first still feels mandatory. |
| `story.s1.b1f_mouth.line_03` | No one else on this floor with me. I'll take the stairs up and see who answers. |

Speaker: **`navigator:guild_handler`** only.

**Following beat:** optional short guided hint on **`^`** interact ([s1_explore_mouth_stairs](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)) if player skipped the Event tile; otherwise stairs-only prompt.

---

## Related

- [narrative POV](../../02-systems/narrative-pov.md)
- [Act 1 guided movement](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)
- [s1-intro § Act 1](../../campaign/s1-intro.md#three-acts-same-s1_b1f-map)
- [dungeons — s1_B1F Event cell](../dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--mouth)
