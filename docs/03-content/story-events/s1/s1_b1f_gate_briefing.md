---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/synced
  - domain/campaign/s1
  - domain/story-vn
---
# Draft — `s1_b1f_gate_briefing`

**Synced:** with game `Assets/Content/StoryEvents/s1_b1f_gate_briefing.asset` — **Navigator-only** (no `npc:*` yet), **blank state**; Launch = click-through block.

**When:** **Exploration Act 1** — Navigator enters the authored **Event** cell **`!` `(10, 9)`** on `s1_B1F` (gate camp threshold), **solo**, **before** first **hub** via gate `^` `(10, 11)`.

**Prerequisite:** Act 1 movement path (not `s1_intro_movement_complete` *(planned)*); not already `S1_B1F_GATE_BRIEFING_SEEN`.

**Narrative job:** **Solo** recon — no crew yet (recruitment is Act 2 hub). Kit has **sealed tools** / latent power not usable yet. Instinct to report topside — **no** Synchro / Protocol / role title; **no** comms-or-“line” diction.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `S1_B1F_GATE_BRIEFING_SEEN = true`
- *(none)* — player continues on foot to **`^`** → hub ([game phase § return](../../../02-systems/game-phase.md#return-to-hub-exploration-only))

**Act 3:** same cell **`(10, 9)`** is **skipped** (`once` + flag); dive spawns at gate **`(10, 11)`** without re-playing.

---

## Script (`textKey` + `textEn`)

| textKey | textEn |
|---------|--------|
| `story.s1.b1f_gate.line_01` | s1_b1f_gate_briefing Event Line 1 |
| `story.s1.b1f_gate.line_02` | s1_b1f_gate_briefing Event Line 2 |
| `story.s1.b1f_gate.line_03` | s1_b1f_gate_briefing Event Line 3 |

Speaker: **`navigator:guild_handler`** only.

**Following beat:** optional short guided hint on **`^`** interact ([s1_explore_gate_stairs](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)) if player skipped the Event tile; otherwise stairs-only prompt.

---

## Related

- [narrative POV](../../../02-systems/narrative-pov.md)
- [Act 1 guided movement](../../campaign/s1-guided-tutorials.md#act-1--movement-b1f)
- [s1-intro § Act 1](../../campaign/s1-intro.md#three-acts-same-s1_b1f-map)
- [archive — s1_B1F Event cell (draft)](../../../archive/mvp1-s1-floor-layouts-draft.md#s1_b1f--outskirts-gate-intro--gate)
