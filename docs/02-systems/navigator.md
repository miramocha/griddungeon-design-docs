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
| **Stratum progress** | Beat Stratum 1 boss → unlock **Sync Relay** |
| **Side quests** | Rescue NPC → unlock **Wellness Lead** |
| **Events** | Story scene after floor gimmick → unlock **Route Analyst** |
| **Optional milestones** | 100% map on B2F, FOE codex entries → **Ledger Chief**, etc. |

- Each Navigator has an `unlockCondition` in data (flag, quest id, stratum id).
- **Starting Navigator:** one Navigator available from game start (tutorial default).
- Locked Navigators are visible at **Navigator Office** as **silhouettes + unlock hint** (optional UX).

## Passive buffs (auras)

While a Navigator is active, the **core six** receive that Navigator’s **aura** — always on in combat and exploration.

| Example Navigator | `navigator_id` | Aura (draft) | Notes |
|-------------------|----------------|--------------|-------|
| **Sortie Lead** | `guild_handler` | +5% Synchro bar gain (MVP1 starter) | Expedition flight lead; executes [Protocol](synchro-protocol.md) |
| **Route Analyst** | `route_analyst` | +5% accuracy to core | Course / grid planning — not combat targeting |
| **Wellness Lead** | `wellness_lead` | −5% MP cost on core heals | Crew care; pairs with **Medic** kits, not the `medic` class |
| **Sync Relay** | `sync_relay` | +3% Synchro bar gain from core actions | Comms loop for team Synchro; stratum unlock candidate |
| **Ledger Chief** | `ledger_chief` | +8% gold from battles | Post-sortie accounts / manifest payouts |

Draft naming: **soft sci-fi expedition flight** (≤2 words, non-battle). Same hub-lead layer as [party classes](party-and-classes.md) field jobs — do not reuse core `class_id` labels (`tactician`, `medic`, …).

- Auras stack only from **one** Navigator (no multi-navigator stack).
- **Fixed per Navigator** — no levels, tiers, or upgrades. New power only by **unlocking a different Navigator**.
- **Starter:** **Sortie Lead** (`guild_handler`) at new game; more unlock via strata / quests / events.

## Protocol execution

When [Synchro](synchro-protocol.md) is **100%**, a **core member** on their AGI turn may invoke a Protocol (`CombatCommand.Protocol`) — that core **spends their turn**. The **active Navigator** **executes** the skill off-formation (calls the protocol; does not take an AGI turn):

1. Synchro bar must be **100%** on the invoking core’s turn.
2. Player picks a Protocol from the Navigator’s **kit** (`protocol_strike`, `protocol_mend` in MVP1; post-MVP1 includes `protocol_deploy` per [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)).
3. Navigator executes; living **core** members participate per skill min/max.
4. Bar → **0%**; invoking core’s turn ends; queue advances.

Navigator **does not** fill the Synchro bar themselves (no combat turns). Core six actions still charge the team bar.

## Combat targeting (locked)

Navigators are **never combat targets**:

- **Not targetable** by enemies — normal attacks, skills, and **boss** abilities.
- **No direct combat interaction** — no HP, no damage, no status, no heals aimed at Navigator.
- **No AGI turn** — enemies and allies do not “hit” or buff Navigator in the turn system.
- UI: Navigator portrait **without HP bar**; present for Protocol + aura only.

Bosses cannot bypass this with “hit all party” — those effects apply to **core (+ aux summons/guests)** only. A **navigator sortie summon** from Protocol Deploy is aux and **is** targetable; the off-formation Navigator is not ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)).

## Progression (simple)

Navigators do **not** progress like core party members:

- **No XP**, **no levels**, **no skill points**, **no aura tiers**
- **No equipment**
- Each Navigator is a **fixed package**: one aura + fixed Protocol skill list, defined in data
- **Only growth path:** unlock another Navigator with different aura/skills

Out of scope: Navigator leveling, trees, gear, or scaling auras.

### Post-MVP1 Protocol skills

| Skill | Summary | ADR |
|-------|---------|-----|
| **Protocol Deploy** (`protocol_deploy`) | Sortie **aux summon** in empty slot; scripted turns; Navigator name on portrait | [023](../../decisions/023-protocol-deploy-sortie-summon.md) |
| **Protocol Transform** (`protocol_transform`) | **Slot-replace** one living core with Navigator **transform profile**; hybrid commands; **Revert** / duration / HP→0 revert safe; label **profile + “via [Core]”** | [024](../../decisions/024-protocol-transform.md) |

Shared: **core** spends AGI turn at Synchro 100%; Navigator **executes** off-formation; **aura on**; **multiple** Protocols per battle when Synchro **recharges** — blocked only while sortie or transform is **active**.

**Same-fight Deploy + Transform** is uncommon: kit is fixed at hub for the whole dive; only possible if this Navigator’s data lists **both** skills ([synchro-protocol § Kit + hub lock](synchro-protocol.md#kit--hub-lock-practical)). Prefer **one** mode skill per Navigator in content.

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
| **Sortie Lead** (`guild_handler`) | Day one | Synchro gain +5% |

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
- [ADR 023 — Protocol Deploy sortie summon](../../decisions/023-protocol-deploy-sortie-summon.md)
- [ADR 024 — Protocol Transform](../../decisions/024-protocol-transform.md)
