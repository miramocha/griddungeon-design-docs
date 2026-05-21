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

- Bar set to **100%** when party enters the labyrinth from hub (ready for first Protocol of the dive).
- Navigator auras may modify gain rate (e.g. `guild_handler` +5%).

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
- **Between battles** on the same floor: bar **persists**.
- **Return to hub:** bar reset to 100%.

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
