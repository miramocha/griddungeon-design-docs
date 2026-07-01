---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/draft
  - domain/combat
---
# Combat Status, Buffs & Debuffs

Rules for **ailments**, **stat modifiers**, and **battle modifiers** during AGI combat. EO-first: limb **binds**, turn-skipping control, timed **Boost/Down** stats, end-of-round ticks. **Boost/Break** (EO2 Force) remains out of scope — see [Synchro Protocol](synchro-protocol.md).

## Who can be affected

| Combatant | Status? | Notes |
|-----------|---------|-------|
| **Core (6)** | Yes | Primary targets; hospital cures between fights |
| **Summon / guest (aux)** | Yes | Same rules; summon dismissed on death |
| **Enemies** | Yes | Bosses may have immunity flags |
| **Navigator** | **No** | Not targetable ([ADR 007](../../decisions/007-navigator-role.md)) |

Auras from Navigator are **passive grants**, not combat status instances on Navigator.

---

## Timing model

### When effects apply

| Moment | What runs |
|--------|-----------|
| **On hit** (skill lands) | Roll inflict chance; apply ailment or stat mod if not blocked |
| **On action start** | Check skip (sleep, paralysis), panic reroll, bind filter on skill list |
| **On action resolve** | Guard mitigation, damage, on-hit secondary effects |
| **End of combat round** | DoT ticks, regen ticks, duration −1, remove expired, summon duration −1 |

Order at **end of combat round** (after last AGI turn):

```
1. Regen / MP regen (buffs) — heal before DoT for readability
2. Poison / Burn DoT — HP loss; **can reduce to 0** At launch: Poison only; Burn MVP2)
3. Decrement durations on all buffs, debuffs, ailments
4. Remove expired instances
5. FOE patrol / mid-battle join (if enabled)
6. Rebuild AGI queue for next round
```

**Between fights:** most combat statuses **clear** on battle end. **Persistent** ailments (curse, rare story flags) are content-tagged — default **none** at launch.

**Hub hospital:** clears **all standard ailments** and restores HP/MP; does not remove permanent story debuffs if any exist later.

---

## Categories

| Category | Examples | Competes with |
|----------|----------|----------------|
| **Ailment — control** | Sleep, Panic, Paralysis | One **control** slot per target (see stacking) |
| **Ailment — bind** | Head / Arm / Leg bind | **Per limb** — multiple binds can coexist |
| **Ailment — DoT** | Poison, Burn | One slot per **DoT type** (Poison + Burn OK) |
| **Stat buff** | Offense Up, Defense Up, Speed Up | Same stat: **refresh** duration, no magnitude stack |
| **Stat debuff** | Offense Down, Defense Down, Blind | Same stat: refresh; Blind uses debuff slot |
| **Battle modifier** | Guard, Charge (Overdriver), Taunt (future) | Skill-defined; may coexist with stats |

---

## Ailments (locked set)

### Control

| ID | Name | On turn start | Duration | Inflict resist |
|----|------|---------------|----------|----------------|
| `sleep` | Sleep | **Skip turn** (no action) | Turns; ends early if **damaged** | `SleepRes` |
| `paralysis` | Paralysis | **Skip turn** (no wake on hit) | Turns | `ParaRes` |
| `panic` | Panic | **Random command** (attack random enemy/ally, skill, or guard) | Turns | `PanicRes` |

**Control slot:** only **one** of Sleep / Paralysis / Panic at a time. New inflict **replaces** the old control ailment (refresh duration if same type).

### Limb bind (EO-style)

Binds **disable skill categories** tied to body parts — not basic **Attack** unless a skill tags `RequiresArm`.

| ID | Name | Blocks |
|----|------|--------|
| `bind_head` | Head Bind | Skills tagged `Body: Head` (most spells, head skills) |
| `bind_arm` | Arm Bind | Skills tagged `Body: Arm` (most weapon skills) |
| `bind_leg` | Leg Bind | Skills tagged `Body: Leg` (kicks, some mobility skills) |

- **Multiple limb binds** on one target allowed (e.g. Head + Arm).
- **Attack** command: allowed if weapon skill is not Arm-tagged; default weapon attack = `Body: Arm` → **blocked by Arm Bind**.
- **Items / Guard / Flee:** allowed unless a specific bind or panic blocks (Panic overrides).

### Damage over time

| ID | Name | End of round | Duration | Notes |
|----|------|--------------|----------|-------|
| `poison` | Poison | **Max HP %** loss (e.g. 5%) | Turns | Refresh duration if re-applied |
| `burn` | Burn | **Fixed fire damage** + optional `-FireRes` | Turns | Separate from Poison |

**DoT slot:** Poison and Burn can coexist. Re-applying same DoT **refreshes** duration; does not stack damage tiers at launch.

### Death

| ID | Name | Behavior |
|----|------|----------|
| `death` | Death / KO | Remove from AGI queue; core needs revive (skill/item/hospital); summon **dismissed** |

Death is a **state**, not a cleansable ailment. Guests/summons leave combat on KO.

---

## Stat buffs & debuffs

EO-style **Boost / Down** modifiers — timed, visible on portrait strip.

### Party & enemy stats at launch

| ID | Name | Effect (example tuning) | Duration |
|----|------|-------------------------|----------|
| `offense_up` | Offense Boost | Physical damage dealt **×1.25** | 3 turns |
| `offense_down` | Offense Down | Physical damage dealt **×0.75** | 3 turns |
| `defense_up` | Defense Boost | Physical damage taken **×0.75** | 3 turns |
| `defense_down` | Defense Down | Physical damage taken **×1.25** | 3 turns |
| `magic_up` | Magic Boost | Elemental damage dealt **×1.25** | 3 turns |
| `magic_down` | Magic Down | Elemental damage dealt **×0.75** | 3 turns |
| `speed_up` | Speed Boost | **+20% effective AGI** for queue order | 3 turns |
| `speed_down` | Slow | **−20% effective AGI** | 3 turns |
| `blind` | Blind | **−30% hit rate** (accuracy stage) | 3 turns |
| `regen` | Regen | **% max HP** heal end of round | 3 turns |

**Stacking rule (same ID):** if target already has `offense_up`, reapply → **refresh duration**, do not add a second stack. Different IDs (Offense Up + Defense Up) **stack**.

**Up + Down on same axis:** net to **neutral** (cancel) or stronger magnitude wins — **At launch: cancel to neutral** when opposite applied.

### Elemental resistance mods (optional)

| ID | Example |
|----|---------|
| `fire_res_up` / `fire_res_down` | ±25% fire damage taken |
| `ice_res_up`, `volt_res_up`, … | Per element |

launch combat uses **3 elements** (fire, ice, volt) in damage pipeline; resistance buffs can ship after core ailments.

---

## Battle modifiers (non-ailment)

Applied by **commands or skills**, separate from Boost/Down table.

| Source | Effect | Expires |
|--------|--------|---------|
| **Guard** | Damage taken **×0.5** (tune) until actor’s **next turn** starts | Consumed on hit or turn start |
| **Charge** (Overdriver, etc.) | Next attack **×1.5** damage | Until released or turn skipped |
| **Taunt** (future) | AI targets this slot | 1–2 turns |

These live in `BattleModifier` list, not the ailment control slot.

---

## Infliction & resistance

### Inflict pipeline

```
skill.InflictStatus?
  → roll vs target.StatusResist(stat)
  → if bind: check limb already bound (refresh duration)
  → if control: replace existing control ailment
  → apply instance { id, duration, sourceSkillId }
```

- **Chance:** skill defines `inflictChance` (0–100%) and `duration` (turns).
- **Boss immunity:** `StatusImmune: sleep, panic` flags per encounter.
- **Cleanse:** Medic skills, items, Protocol skills (if designed) remove by category or specific ID.

### Resistance sources

| Source | Example |
|--------|---------|
| Class passive | Medic **+PoisonRes** |
| Equipment | Boots `+BindLegRes` |
| Navigator aura | Small party-wide resist (not a combat status on Navigator) |
| Enemy rank | FOE “immune to panic” |

Resist reduces **inflict chance**, not damage (unless a debuff specifically says otherwise).

---

## Interaction with combat systems

| System | Interaction |
|--------|-------------|
| **AGI queue** | Speed Up/Down recalculates **effective AGI** when queue is built each round |
| **Protocol (core turn)** | Protocol skills on a core turn when Synchro is 100%; Navigator executes; not stripped by Panic (Navigator not panicking) |
| **Targeting** | Sleep/Paralysis: target still **valid** but skips turn; dead excluded |
| **FOE mid-battle join** | Joining enemy enters with **no** party debuffs; can be buffed by enemy skills same round |
| **Flee** | Allowed unless Panic randomizes away; binds do not block Flee |
| **Codex** | Weakness icons separate; status resist not required at launch codex |

---

## UI

| Element | Shows |
|---------|-------|
| Portrait strip | Icon per ailment + buff/debuff (max 4–6 icons; overflow “+N”) |
| Turn queue | Sleep/para icon on portrait; greyed when skipping |
| Combat log | `"{name} is poisoned!"` / `"{name} woke up!"` / bind messages |
| Targeting | Debuffed enemies show Down icons; hidden until identified (optional) |
| Tooltip | Name, turns remaining, short rule text |

**Color coding (suggestion):** ailments purple, buffs blue, debuffs red, Guard yellow outline.

---

## Data model (Unity 6)

```csharp
// ScriptableObject per status definition
class StatusDefinition {
  string id;
  StatusCategory category; // Control, BindLimb, DoT, StatBuff, StatDebuff, BattleMod
  int defaultDurationTurns;
  float magnitude;       // % or multiplier per id
  BodyPart? bindPart;    // Head, Arm, Leg
  bool removedOnDamage;  // sleep
  string[] immuneTags;
}

class StatusInstance {
  string definitionId;
  int turnsRemaining;
  int appliedRound;
  string sourceCombatantId;
}

class CombatantState {
  List<StatusInstance> statuses;
  List<BattleModifier> battleMods;
  bool IsDead => hp <= 0;
}
```

Skills reference `inflictStatusId`, `chance`, `durationOverride`. Skills tag `bodyPart` for bind checks.

---

## Launch vs later

| Launch | Later |
|-----|-------|
| Poison, Sleep, Panic, Head/Arm Bind | Leg bind, Paralysis |
| Offense/Defense Up & Down | Elemental res up/down |
| Blind | Curse, petrify, charm |
| End-of-round tick + duration | Speed Boost in queue ([combat](combat.md) optional note) |
| Hospital full cure | Field items mid-dungeon |
| Medic cleanse skill (1–2) | Full bind + leg skill trees |

---

## Related docs

- [Combat](combat.md) — round flow, damage pipeline
- [Party & classes](party-and-classes.md) — who inflicts binds/buffs
- [Hub & services](hub-and-services.md) — hospital cure
- [Navigator](navigator.md) — not status-targetable
- [04 — Tech notes](../04-tech-notes.md)
