# Party & Classes

## Party size & formation

**Locked — core party:** **6 guild members** in labyrinth (3 front / 3 back).

**Locked — combat aux:** **+1 front / +1 back** for **summon or guest** only ([summons & guests](summons-and-guests.md), [ADR 004](../../decisions/004-auxiliary-slots.md)).

**Locked — Navigator:** **1 active party lead** off-formation; Union + passives ([navigator.md](navigator.md), [ADR 007](../../decisions/007-navigator-role.md)). **Not** one of the six grid/combat line slots.

| Row | Core slots | Aux slot |
|-----|------------|----------|
| **Front** | 3 | 1 (summon or guest) |
| **Back** | 3 | 1 (summon or guest) |

Exploration uses **core 6 only** as one grid anchor. Navigator and aux are **not** on the grid blob. Aux exists **in combat UI only**.

Bench: recruit additional characters at guild; swap only at hub (MVP1).

## Class roster (EO archetypes)

Use EO-inspired roles; rename for original IP when setting firms up.

| Class | Row | Role | Signature |
|-------|-----|------|-----------|
| **Protector** | Front | Tank | Damage mitigation, party guard |
| **Landsknecht** | Front | Physical DPS | Swords, axes, multi-hit |
| **Medic** | Back | Healing | HP restore, **cleanse ailments**, revive |
| **Alchemist** | Back | Magic DPS | Fire/ice/volt, infusions; **summon** skills (aux) |
| **Survivalist** | Back/Front | Ranged / control | Bow, traps, bind skills |
| **Troubadour** | Back | Support | Party buffs, minor heals |
| **Dark Hunter** | Front | Control | Bind, damage vs disabled foes |
| **Ronin** | Front | Glass cannon | Charged attacks, self-buffs |

**MVP1 roster:** Protector, Landsknecht, Medic, Alchemist, Survivalist, Troubadour (six core slots).

## Navigator

See [navigator.md](navigator.md). Swappable party lead; executes [Union](union.md) skills; grants auras to core six. **Unlocked** through progression; assigned at **hub** (MVP1).

## Union skills

Coordinated team skills via [Union bar](union.md); **Navigator executes**, core six **participate**. Each Navigator has a **fixed** Union kit; guild-common Union skills may unlock via quests/strata (separate from Navigator unlocks).

## Skill trees (EO model)

- Each class has a **skill tree** (tabs or tiers).
- **Skill points** on level up; allocate at hub only.
- Skills cost **levels** in prerequisites; some grant passives.
- Summon skills target **aux front** or **aux back** per definition.
- No multiclass in MVP1.

See [character progression](character-progression.md).

## Character creation

- Name, class, portrait
- Base stats per class template (STR, VIT, AGI, LUC, TEC — EO-like split)
- Starting weapon + one skill point tutorial

## Guild recruitment

- Create custom characters or use **premade** guild roster (EO gimmick optional).
- Class unlocked as player progresses stratum (MVP1: all six core classes available day one).

## Death

- **Core — in fight:** downed until end of fight; revive skills if party wins.
- **Core — wipe:** GAME OVER; reload hub save — characters not deleted.
- **Summon:** dismissed on death or duration end.
- **Guest:** downed for fight; quest script handles story failure/retreat.

## Related docs

- [Navigator](navigator.md)
- [Summons & guests](summons-and-guests.md)
- [Union (team bar)](union.md)
- [Combat](combat.md)
- [Character progression](character-progression.md)
- [Hub & services](hub-and-services.md)
