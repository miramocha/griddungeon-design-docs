# Narrative POV — Navigator, blank state

**Status:** Locked (MVP1 S1)  
**Applies to:** [story events](story-events.md), [guided tutorial](guided-tutorial.md), hub copy, future Navigator unlock scenes  
**Reference tone:** *Amnesia*-style blank state — the player **is** the active Navigator; they **do not** know their role, past, or full toolkit at new game.

---

## Player identity (locked)

| Layer | Who speaks | Who the player is |
|-------|------------|-------------------|
| **Story VN** | Active Navigator only (`navigator:guild_handler` in S1) | The Navigator — first-person **I** / **my**, on the march |
| **Guided tutorial** | **No character speaker** — impersonal system / imperative coach ([guided-tutorial](guided-tutorial.md)) | Same player, but copy does not use Navigator **I** |
| **Combat log / skills** | System + neutral tags until taught | Navigator directs cores; no core-by-class dialogue |
| **Hub services** | UI labels + optional Navigator asides (post-MVP1) | Navigator between dives |

**Not the player:** a disembodied “commander” watching from outside, or a named core guild member. Cores stay **silent** in scripted fiction so any class roster works.

**Guide, not fighter (locked):** The Navigator **explores the labyrinth** on every dive — mouth in, hub out. **Act 1 (S1):** **alone** until hub recruitment. **Act 3+:** walks with the recruited party on the **sideline**, **off the 3+3 formation**. They **support** through map sense, sealed **kit tools**, and (when unlocked) Synchro / Protocol — not by fighting on the grid or taking AGI turns.

**Camera / grid:** FPV follows the **party blob** on the labyrinth grid ([vision § pillars](../00-vision.md#design-pillars-etrian-odysseyfirst)); in Act 1 that blob is the **solo Navigator**; after recruitment it is the six-core formation with the Navigator off-grid fictionally.

**Diction (S1 copy pass):** Prefer **guide / kit / map / pull / sealed tools** — grounded “low myth,” municipal underworks. **Avoid** comms, channel, line, radio, and remote-commander framing unless a later beat explicitly needs it.

---

## Blank state (locked)

At **new game** the Navigator:

- **Does not** recall their name, title, employer history, or what their kit tools are for.
- **Does not** name **Synchro**, **Protocol**, or aura mechanics until a beat **proves** them in play (S1: first after crisis AOE on B2F).
- **May** feel instincts (report topside, map answering, power **sealed** in the kit) without explaining them.
- **May** reference unread kit tags, contract fragments, or guild paperwork they cannot parse yet — diegetic mystery, not tutorial infodump.

**Avoid in early scenes:** “As your Sortie Lead…”, “I always give +5% Synchro…”, “Remember your Protocol kit”, lore that assumes prior campaigns.

**Reveal pacing (S1 MVP1):**

| Beat | Navigator knows (fiction) | Systems unlocked |
|------|---------------------------|------------------|
| Act 1 B1F | **Solo**; map/kit sense waking; topside report “feels” mandatory | Movement, gather, mouth → hub |
| Act 2 hub | Recruit **six cores**; Navigator Office / kit tools; still light on backstory | Party build, `guild_handler` assigned |
| B2F approach VN | Threat on board; contract says engage; **something** on their side is locked | Tutorial combat, Synchro **rules** locked |
| Post-crisis unlock VN | First **conscious** use of kit burst power; hears “Synchro” / “Protocol” as labels | `s1_synchro_unlocked`, meter, guided Protocol |
| Hub return VN | Target down; pulse is real; topside rest — **not** full origin story | Hub warp, repeat dives |

Later strata / Navigator unlocks add **memory chips**, office files, and `s2_navigator_unlock_*` scenes — out of S1 scope.

---

## Voice guidelines

| Do | Don't |
|----|--------|
| First person: “I’m alone down here…”, “My kit…”, “The map’s answering…” (Act 3+: sideline with crew) | Second-person tutorial voice (“You are the navigator”) |
| Short field cadence — municipal underworks + **low myth** (sealed tools, sense, pull) ([vision § tone](../00-vision.md#tone--setting)) | High fantasy monologues; remote commander voice |
| Hedge early: “I don’t know yet”, “sealed tools”, “paperwork calls it…” | Front-load mechanic glossary |
| Name mechanics **when** the scene’s job is teach (unlock VN, coach) | Spoil Synchro in Act 1 mouth briefing |
| “Your crew / the six” for the formation | “Gunner said…” / class-specific banter |
| — | **Comms / channel / line / radio** in S1 scripts (unless a later beat revisits) |

**Speakers (MVP1):** Navigator for **story VN** only (`navigator:guild_handler`). **Guided tutorials:** no `speakerId` — system-style tips. **Narrator / signage / FOE voice** only when impersonal ([story-events § speakers](story-events.md#speakers-and-custom-party)). **No core `speakerId`** in S1 scripts.

---

## Authoring workflow

1. Draft `textKey` + `textEn` under [story-events](../03-content/story-events/README.md) or [s1-guided-tutorials](../03-content/campaign/s1-guided-tutorials.md).
2. Check row against **Reveal pacing** table above.
3. Import to game `Assets/Content/StoryEvents/` when implementation syncs ([#87](https://github.com/miramocha/griddungeon-game/issues/87)).

Game copy should match design drafts; re-running **Ensure MVP1 S1 Story Events** overwrites hand edits — prefer updating drafts first, then menu/assets.

---

## Related

- [Navigator](navigator.md#narrative-role-mvp1)
- [Story events](story-events.md)
- [Guided tutorial](guided-tutorial.md)
- [S1 intro](../03-content/campaign/s1-intro.md)
- [ADR 028 — Story events](../../decisions/028-story-visual-novel-events.md)
