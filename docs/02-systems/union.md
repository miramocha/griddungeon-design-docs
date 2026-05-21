# Union (Team Bar)

Working name: **Union**. Rename later when setting/voice is fixed.

Party-wide **team resource** for coordinated **Union skills**, executed by the active **[Navigator](navigator.md)**. Inspired by *Etrian Odyssey V* Union skills; implemented as a **single shared bar**.

## Union bar

| Property | Rule |
|----------|------|
| **Range** | 0–100% (one bar for the whole party) |
| **UI** | Prominent combat meter (label: Union until renamed) |
| **Charge** | **Core six** combat actions only |
| **Spend** | **Navigator** invokes Union skill when bar is 100% |

## Charging the bar

### When leaving hub

- Bar set to **100%** when party enters the labyrinth from hub (ready for first Union of the dive).
- Navigator auras may modify gain rate (e.g. Scout Navigator +3%).

### During combat

While bar is below 100%, **core formation members** add to the shared bar:

| Event | Union gain (MVP1 baseline — tune in data) |
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

Exploration steps do **not** charge Union.

## Spending — Union skills (Navigator)

| Rule | Detail |
|------|--------|
| **Executor** | Active **Navigator** only ([navigator.md](navigator.md)) |
| **Cost** | Bar → **0%** after use |
| **Threshold** | Bar must be **100%** |
| **Participants** | Living **core six** per skill min/max; downed excluded |
| **Aux** | Do not participate (MVP1) |
| **Skill list** | Navigator kit + guild-unlocked common Union skills |

### Timing — core turn action (MVP1)

When the Union bar is **100%**, a **core member** on their AGI turn may use **Union** instead of attack/guard/skill/item:

1. Player picks a Union skill from the **Navigator’s** available list (Navigator executes; living core join per skill rules).
2. Resolve effects; bar → **0%**; that character’s turn ends (normal queue advance).
3. Other core/enemy/summon turns continue in AGI order.

Only **one Union use** while the bar is full (spend resets the bar).

```
Combat round:
  AGI turn phase (core may choose Union when bar = 100%)
  → End of round
```

## Union skill list (draft)

**Common** (guild unlock) + **Navigator-specific** extras per character:

| Skill | Participants | Effect |
|-------|----------------|--------|
| **Union Strike** | 2+ | Participants attack one enemy |
| **Union Guard** | 3+ | Party damage reduction 1 turn |
| **Union Mend** | 2+ | Heal all living core |
| **Union Retreat** | 4+ | High chance flee to floor entrance |
| **Union Scan** | 1+ | Register enemy in codex |

## Presentation

- Navigator portrait leads Union phase ([combat presentation](combat-presentation.md)).
- Highlight participating core portraits.

## MVP1

- [ ] Union bar + Navigator skill picker at 100%
- [ ] Default Navigator executes **Union Strike**, **Union Mend**
- [ ] Core actions charge bar; Navigator off-formation

## Not in scope (MVP1)

- Per-character Union gauges
- Aux in Union skills
- **Boost/Break**

## Related docs

- [Navigator](navigator.md)
- [Combat](combat.md)
- [Party & classes](party-and-classes.md)
- [ADR 006 — Union team bar](../../decisions/006-union-team-bar.md)
- [ADR 007 — Navigator role](../../decisions/007-navigator-role.md)
