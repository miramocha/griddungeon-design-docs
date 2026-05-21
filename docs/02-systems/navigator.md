# Navigator

**Party lead** who sits **outside** the 3+3 combat formation. They command [Synchro Protocol](synchro-protocol.md) skills and provide **passive buffs** to the active core six.

## Role summary

| | Navigator | Core party (6) | Aux summon/guest |
|---|-----------|----------------|------------------|
| **Formation** | Off-formation | 3 front + 3 back | +1 front / +1 back |
| **AGI turns** | No | Yes | Yes (if living) |
| **Protocol skills** | **Executes** when Synchro 100% | **Participate** per skill rules | No |
| **Passive buffs** | **Grants** to core six | Receive | No (MVP1) |
| **Exploration grid** | No | Yes (party blob) | No |
| **Swappable** | **Hub only** | Hub bench (core) | N/A |

```
[ Navigator — off formation, portrait + passives + Protocol command ]

[ Core front ×3 ] [ Aux front ×1 ]
[ Core back  ×3 ] [ Aux back  ×1 ]
```

## Active Navigator

- Exactly **one** Navigator is **active** per labyrinth dive (assigned at **Navigator Office** before entry).
- **Unlock pool:** Navigators are **not recruited** at Explorers Guild. New Navigators **unlock** as the campaign progresses; unlocked Navigators are listed at **Navigator Office**.
- **Switch:** **hub only** (Navigator Office) — assign active Navigator before entering or when returning to hub. **No** mid-dungeon switch (no camp/inn swap in labyrinth).

### How Navigators unlock

| Source | Example |
|--------|---------|
| **Stratum progress** | Beat Stratum 1 boss → unlock Scout Navigator |
| **Side quests** | Rescue NPC → unlock Hierophant |
| **Events** | Story scene after floor gimmick → unlock Tactician |
| **Optional milestones** | 100% map on B2F, FOE codex entries, etc. |

- Each Navigator has an `unlockCondition` in data (flag, quest id, stratum id).
- **Starting Navigator:** one Navigator available from game start (tutorial default).
- Locked Navigators are visible at **Navigator Office** as **silhouettes + unlock hint** (optional UX).

## Passive buffs (auras)

While a Navigator is active, the **core six** receive that Navigator’s **aura** — always on in combat and exploration.

| Example Navigator | Aura (draft) |
|-------------------|--------------|
| **Tactician** | +5% accuracy to core |
| **Hierophant** | −5% MP cost on core heals |
| **Scout** | +3% Synchro bar gain from core actions |
| **Quartermaster** | +8% gold from battles |

- Auras stack only from **one** Navigator (no multi-navigator stack).
- **Fixed per Navigator** — no levels, tiers, or upgrades. New power only by **unlocking a different Navigator**.
- **Starter:** one Navigator at new game with a simple +max HP aura; more unlock via strata / quests / events.

## Protocol execution

Only the **active Navigator** executes Protocol skills when [Synchro](synchro-protocol.md) is full:

1. Synchro bar must be **100%** on a **core** combatant’s turn.
2. Player picks a Protocol skill from the Navigator’s **kit** (`protocol_strike`, `protocol_mend` in MVP1).
3. Navigator “calls” the protocol; living **core** members participate per skill min/max.
4. Bar → 0%; Navigator does not consume an AGI turn.

Navigator **does not** fill the Synchro bar themselves (no combat turns). Core six actions still charge the team bar.

## Combat targeting (locked)

Navigators are **never combat targets**:

- **Not targetable** by enemies — normal attacks, skills, and **boss** abilities.
- **No direct combat interaction** — no HP, no damage, no status, no heals aimed at Navigator.
- **No AGI turn** — enemies and allies do not “hit” or buff Navigator in the turn system.
- UI: Navigator portrait **without HP bar**; present for Protocol + aura only.

Bosses cannot bypass this with “hit all party” — those effects apply to **core (+ aux)** only.

## Progression (simple)

Navigators do **not** progress like core party members:

- **No XP**, **no levels**, **no skill points**, **no aura tiers**
- **No equipment**
- Each Navigator is a **fixed package**: one aura + fixed Protocol skill list, defined in data
- **Only growth path:** unlock another Navigator with different aura/skills

Out of scope: Navigator leveling, trees, gear, or scaling auras.

## Hub — Navigator Office

Separate from **Explorers Guild** ([hub & services](hub-and-services.md)). Guild handles core six; Navigator Office handles party leads only.

| Action | Detail |
|--------|--------|
| **Browse** | All Navigators — unlocked (selectable) vs locked (silhouette + hint) |
| **Assign** | Set **active** Navigator for the next labyrinth dive |
| **Preview** | Aura summary on core six; list of Protocol skills in this Navigator’s kit |
| **Switch** | Change active Navigator among unlocked pool — **hub only** |

No recruitment, no skill points, no equipment — unlock + assign only.

## UI

- Navigator **portrait + name** above or beside formation (not in front/back rows).
- Aura icons on core portraits (small badge from active Navigator).
- Protocol use: Navigator voice line / portrait pulse; skill picker shows **Navigator’s** Protocol list.

## MVP1 content (placeholder)

| Navigator | Unlock | Aura (MVP1) |
|-----------|--------|-------------|
| `guild_handler` | Day one | Synchro gain +5% |

Additional Navigators unlock via strata/quests post-MVP1.

## MVP1

- [ ] One default Navigator + one aura
- [ ] Navigator selects Protocol skill when Synchro is 100%
- [ ] **Navigator Office:** pick active Navigator from **unlocked** pool (starter + 1 stratum unlock)
- [ ] Not in formation rows or AGI queue

## Resolved decisions

- **Switch:** hub only
- **Targeting:** never — including bosses
- **Progression:** unlock-only — no XP, tiers, or equipment

## Related docs

- [Synchro Protocol (team bar)](synchro-protocol.md)
- [Party & classes](party-and-classes.md)
- [Combat](combat.md)
- [ADR 007 — Navigator role](../../decisions/007-navigator-role.md)
