# Synchro Protocol (Team Bar)

**Locked name** ([ADR 020](../../decisions/020-team-burst-naming.md)). Replaces working name **Union**.

Party-wide **Synchro** meter for coordinated **Protocol** skills, executed by the active **[Navigator](navigator.md)**. Inspired by *Etrian Odyssey V* Union skills; implemented as a **single shared bar**.

## Synchro bar

| Property | Rule |
|----------|------|
| **Range** | 0–100% (one bar for the whole party) |
| **UI** | Prominent combat meter (label: **Synchro**) |
| **Charge** | **Core six** combat actions only |
| **Spend** | **Navigator** invokes a Protocol when bar is 100% |

## Charging the bar

### When leaving hub

- Bar set to **100%** when party enters the labyrinth from hub — **except** before Stratum 1 Synchro tutorial ([§ S1 tutorial gating](#s1-tutorial-gating-first-foe)).
- Navigator auras may modify gain rate (e.g. `guild_handler` +5%) — only while Synchro is **unlocked**.

### S1 tutorial gating (first FOE)

**Campaign flags:** `s1_synchro_unlocked` (mid-fight), `s1_synchro_protocol_tutorial_done`, `s1_first_foe_tutorial_complete` (see table below).

| State | Synchro bar | Charge in combat | Protocol (`U` / core turn) | Hub → labyrinth |
|-------|-------------|------------------|----------------------------|-----------------|
| **Before first FOE contact** | Hidden / locked | **No gain** | **Disabled** | **0%** |
| **First FOE phase A** (start) | Locked | No gain | Disabled | — |
| **First FOE phase B** (mid unlock) | **100%** | Yes | **Forced** `protocol_strike` only | — |
| **After tutorial complete** | Normal | Normal | Normal | **100%** on hub exit |

**First FOE (locked):** `foe_alley_stalker` on `s1_B2F` — mandatory tutorial fight ([campaign S1](../03-content/campaign/s1-intro.md) · [dungeons — B2F](../03-content/dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe)).

1. **Act 3 path** — block B3F until `s1_first_foe_tutorial_complete`.
2. **`noFlee: true`** — cannot skip the lesson.
3. **Unbeatable FOE** — tutorial enemies **cannot be killed** (HP floor at 1 / `tutorialUnbeatable`); fight does not end on normal damage.
4. **Phase A** — Synchro locked for first core turns (or until trigger).
5. **Phase B (mid-fight)** — on trigger (e.g. 2 core turns or first party HP loss): set `s1_synchro_unlocked`, bar **100%**, Navigator prompt; next core turn **must** use **`protocol_strike`**.
6. **End** — on Protocol resolve: scripted FOE retreat, victory, set `s1_synchro_protocol_tutorial_done` + `s1_first_foe_tutorial_complete`.

Random fights before this FOE contact: Synchro **locked**. `CombatEntryContext.tutorialKind = SynchroFirstFoe` in implementation ([combat](combat.md)).

### During combat

While bar is below 100%, **core formation members** add to the shared bar:

| Event | Synchro gain (MVP1 baseline — tune in data) |
|-------|-------------------|
| Normal attack | +4% |
| Skill used | +6% |
| Guard | +3% |
| Item use | +2% |
| Core member takes HP damage | +2% (once per hit) |
| Enemy killed (participating in kill) | +5% |
| Core member downed | −25% bar |
| Combat ends (victory) | +10% if bar below 100% (optional catch-up) |

- **Navigator** does not act in AGI queue — does not directly add bar.
- **No gain** from aux summons/guests or enemy actions.
- Bar cannot exceed 100%.
- **Between battles** on the same floor: bar **persists** (if unlocked).
- **Return to hub:** bar reset to **100%** when unlocked; **0%** and locked when `s1_synchro_unlocked` false.

Exploration steps do **not** charge Synchro.

## Spending — Protocol skills (Navigator)

| Rule | Detail |
|------|--------|
| **Executor** | Active **Navigator** only ([navigator.md](navigator.md)) |
| **Cost** | Bar → **0%** after use |
| **Threshold** | Bar must be **100%** |
| **Participants** | Living **core six** per skill min/max; downed excluded |
| **Aux** | Do not participate (MVP1) |
| **Skill list** | Navigator kit + guild-unlocked common Protocols |

### Timing — core turn action (MVP1)

When the Synchro bar is **100%**, a **core member** on their AGI turn may use **Protocol** (`CombatCommand.Protocol`) instead of attack/guard/skill/item:

1. Player picks a Protocol from the **Navigator’s** available list (Navigator executes; living core join per skill rules).
2. Resolve effects; bar → **0%**; that character’s turn ends (normal queue advance).
3. Other core/enemy/summon turns continue in AGI order.

Only **one Protocol use** while the bar is full (spend resets the bar).

```
Combat round:
  AGI turn phase (core may choose Protocol when Synchro = 100%)
  → End of round
```

## Protocol skill list (draft)

**Common** (guild unlock) + **Navigator-specific** extras:

| Skill | Participants | Effect |
|-------|----------------|--------|
| **Protocol Strike** | 2+ | Damage all enemies (MVP1: `protocol_strike`) |
| **Protocol Guard** | 3+ | Party damage reduction 1 turn |
| **Protocol Mend** | 2+ | Heal all living core (MVP1: `protocol_mend`) |
| **Protocol Retreat** | 4+ | High chance flee to floor entrance |
| **Protocol Scan** | 1+ | Register enemy in codex |

## Presentation

- Navigator portrait leads Protocol command ([combat presentation](combat-presentation.md)).
- Highlight participating core portraits.

## MVP1

- [x] Synchro bar + Protocol on core turn at 100%
- [x] Default Navigator: **Protocol Strike**, **Protocol Mend** (`protocol_strike`, `protocol_mend`)
- [x] Core actions charge bar; Navigator off-formation
- [ ] S1 gate: unlock Synchro **mid** first FOE; unbeatable FOE; forced `protocol_strike` **in that fight**

## Not in scope (MVP1)

- Per-character Synchro gauges
- Aux in Protocol skills
- **Boost/Break**

## Related docs

- [Navigator](navigator.md)
- [Combat](combat.md)
- [ADR 006 — Team bar mechanics](../../decisions/006-union-team-bar.md)
- [ADR 020 — Naming](../../decisions/020-team-burst-naming.md)
- [ADR 007 — Navigator role](../../decisions/007-navigator-role.md)
