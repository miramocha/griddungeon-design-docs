# Draft — `s1_synchro_protocol_unlock`

**Status:** Copy draft — Navigator only; MVP1 = click-through block (no portrait art).

**Trigger:** Whichever is first — 2 completed core turns in Phase A, or FOE at tutorial HP floor ([synchro § S1](../../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe)).

**Start:** After triggering action UI beat completes.

**Dismiss:** Z or click per line; **no skip**.

**Effects on final dismiss:**

- `set_campaign_flag` → `s1_synchro_unlocked = true`
- `set_synchro_charge` → `100`
- `combat_tutorial_phase` → forced `protocol_strike` on next core turn

---

## Script (placeholder — use `textKey` + `textEn` in data)

| textKey | textEn (draft) |
|---------|----------------|
| `story.s1.synchro_unlock.line_01` | *(optional — FOE reacts via combat UI only, no line)* |
| `story.s1.synchro_unlock.line_02` | The whole squad’s channel just locked in. That’s **Synchro** — my link to your crew. |
| `story.s1.synchro_unlock.line_03` | I can run one **Protocol** on your signal. Full bar, one shot. |
| `story.s1.synchro_unlock.line_04` | On your next turn, open **Protocol** and take **Protocol Strike**. We hit hard, then pull back before it rallies. |

Speaker: **`navigator:guild_handler`** for all lines. No core-named dialogue (custom party).

---

## Related

- [ADR 028](../../../decisions/028-story-visual-novel-events.md)
- [Story events](../../02-systems/story-events.md)
