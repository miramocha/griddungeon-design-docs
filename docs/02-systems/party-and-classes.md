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

## Class roster (modern guild)

Expedition-guild roles — readable job titles, not medieval fantasy. **Code IDs** (snake_case) are stable for skills/data.

| Class | `class_id` | Row | Role | Signature | EO analogue |
|-------|------------|-----|------|-----------|-------------|
| **Vanguard** | `vanguard` | Front | Tank | Mitigation, party guard, intercept | Protector |
| **Breaker** | `breaker` | Front | Physical DPS | Blades, axes, multi-hit | Landsknecht |
| **Medic** | `medic` | Back | Healing | HP restore, **cleanse ailments**, revive | Medic |
| **Elementalist** | `elementalist` | Back | Magic DPS | Fire / ice / volt; infusions | Alchemist (elements only) |
| **Summoner** | `summoner` | Back | Summon specialist | **Aux deploys**, summon buffs, weak personal bolts | Necromancer / soloist (EO-adjacent) |
| **Marksman** | `marksman` | Back/Front | Ranged / control | Bow, traps, bind skills | Survivalist |
| **Tactician** | `tactician` | Back | Support | Party buffs, minor heals, debuffs | Troubadour |
| **Saboteur** | `saboteur` | Front | Control | Bind, bonus vs disabled targets | Dark Hunter |
| **Overdriver** | `overdriver` | Front | Glass cannon | Charge attacks, self-buff surges | Ronin |

**MVP1 roster:** Vanguard, Breaker, Medic, **Summoner**, Marksman, Tactician (six core slots).

**Post-MVP1 unlock:** Elementalist, Saboteur, Overdriver.

**Note:** MVP1 has no **Elementalist** — fire/ice/volt specialist joins later; Summoner covers weak ranged bolts + summons only.

## Summon skills — Summoner only

**Only the Summoner class** may learn skills that **deploy aux allies** ([summons & guests](summons-and-guests.md), [ADR 016](../../decisions/016-summon-control-mvp1.md)).

| Rule | Detail |
|------|--------|
| **Deploy skills** | Summoner tree only — target aux **front** or **back** |
| **Other classes** | No aux summons (Vanguard, Breaker, Medic, Elementalist, Marksman, Tactician, etc.) |
| **Marksman traps** | Separate system — not aux slot allies |
| **Items / bosses** | Rare exceptions; not on core class trees |

**MVP1:** one test skill — `deploy_test_drone` (aux back, 3 turns, scripted actions).

**Party build:** Up to **two** deploys if both aux rows filled and Summoner has the skills.

## Navigator

See [navigator.md](navigator.md). Swappable party lead; executes [Union](union.md) skills; grants auras to core six. **Unlocked** through progression; assigned at **Navigator Office** (MVP1).

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
- Class unlocked as player progresses stratum (MVP1: all **six MVP1 classes** available day one; Elementalist / Saboteur / Overdriver later).

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
