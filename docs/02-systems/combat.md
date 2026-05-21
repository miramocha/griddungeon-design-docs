# Combat

Turn-based battles: readable **AGI turn order**, **3+3 core rows** plus **+1+1 auxiliary** slots for summons/guests.

## Battle layout

```
[ Enemies — up to 5 targets, may have front/back or single row per design ]

[ Core front ×3 ] [ Aux front ×1 ]   summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   summon or guest
```

- **Core (6):** guild party; always present in combat if alive.
- **Aux (0–2):** optional [summon or guest](summons-and-guests.md) per row.
- **Melee** without pierce targets **front row** (core + aux front) before back.
- **Ranged / spells** — per skill targeting rules.

## Turn structure — AGI order (EO-style)

**Not** strict "all party then all enemies."

### Combat round vs turn

| Term | Meaning |
|------|---------|
| **Turn** | One actor’s action when they reach their slot in the AGI queue |
| **Combat round** | Full cycle: every living combatant (party, aux, enemies) takes **one turn**; then end-of-round effects run |

FOE grid movement during battle ([ADR 005](../../decisions/005-foe-combat-patrol.md)) triggers **once per combat round**, not per individual turn.

### Round flow

1. Build **turn queue**: all living **core + aux + enemies** sorted by **AGI**.
2. Display queue icons (portraits; aux uses distinct frame).
3. **Turn phase** — each actor takes one action in AGI order.
4. **End of combat round** — status ticks, summon duration −1; optional FOE patrol tick ([ADR 005](../../decisions/005-foe-combat-patrol.md)); check wipe/victory; rebuild queue if fight continues.

Optional later: **Speed Boost** / **Slow** modify effective AGI.

## Commands (core party)

| Command | Notes |
|---------|-------|
| Attack | Weapon hit; target enemy slot |
| Guard | Damage reduction until next turn |
| Skill | Class skill; may **place summon** in aux slot |
| Item | Usable consumables |
| Flee | May fail; aux units left behind (summons dismissed; guest script TBD) |

## Commands (summon / guest)

| Command | Notes |
|---------|-------|
| Attack / Skill | Per entity definition |
| Guard | If granted |
| — | Guests flagged **NPC** use AI instead of player input |

## Commands (enemy)

- Attack, skill, debuff, buff allies, **summon adds** (may fill enemy aux or extra slots), flee (rare).

## Damage pipeline (draft)

```
hit = accuracy vs evasion (+ blind, etc.)
if miss → end
damage = skill/weapon base + stat − mitigation
apply resistances (slash, pierce, fire, ice, volt, …) — start with 3 elements for MVP
apply to HP; on-hit statuses
```

## Status effects (EO starter set)

| Effect | Behavior |
|--------|----------|
| Poison | Damage each turn |
| Sleep / Panic | Skip or random action |
| Bind / Head bind | Disable arms / head skills |
| Buff / Debuff | Timed stat mods |
| Death | Core downed; summon dismissed; guest downed |

## FOE vs random fights

| | Random | FOE |
|---|--------|-----|
| Trigger | Step roll | Grid contact |
| Difficulty | Floor table | Designed spawn; higher XP/drops |
| Repeat | Common | FOE respawns on floor reset rules (TBD) |

## Optional later: FOE movement during combat

**Not MVP.** When enabled ([ADR 005](../../decisions/005-foe-combat-patrol.md)):

- Party stays on the **exploration cell** where the fight started; grid exploration remains frozen.
- At **end of each combat round** (step 4 above — not per AGI turn), each FOE on the floor moves **1 cell** along its patrol path.
- FOEs **do not join** the current encounter when they reach the party cell (no mid-battle merge by default).
- After victory, optional **chain FOE battle** if an FOE shares the party cell — tune when feature ships.

Exploration patrol ([ADR 003](../../decisions/003-foe-step-patrol.md)) is paused for the duration of combat; combat-round patrol replaces it.

## Victory / defeat

- **Victory:** XP to **core party only**; drops; quest progress.
- **Wipe:** GAME OVER → hub load; see [hub](hub-and-services.md).
- **Flee:** Return to exploration; summons end; guest per script.

## Presentation (spells & skills)

- **Most skills:** [fixed battle camera](combat-presentation.md) — same battle angle; optional slight zoom to target; no cinematic cuts.
- **Some skills:** dynamic animation + **cinematic camera** (bosses, ultimates, highlights); longer lockout, data-flagged per skill.

See [combat presentation](combat-presentation.md).

## UI requirements

- Turn order strip — core, aux, enemies mixed by AGI
- **4+4 row layout** — six core portraits + two aux slots (empty aux hidden or dimmed)
- Aux label: Summon / Guest
- Command phase: one action per living **player-controlled** combatant per round
- Target selection with valid highlights
- Combat log
- Enemy weakness icons when identified

## Related docs

- [Combat presentation](combat-presentation.md)
- [Party & classes](party-and-classes.md)
- [Summons & guests](summons-and-guests.md)
- [Character progression](character-progression.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
