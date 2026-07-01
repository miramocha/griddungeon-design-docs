---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/accepted
  - domain/combat
---
# launch class skills (content kit)

**Status:** Locked at launch ContentDB ([design-docs #3](https://github.com/miramocha/griddungeon-design-docs/issues/3), [game #12](https://github.com/miramocha/griddungeon-game/issues/12))  
**Authority:** Skill IDs and targeting here; implementation types in [05 — class design](../05-class-design.md).

---

## Conventions

| Rule | Detail |
|------|--------|
| **ID format** | `{class_id}_{snake_name}` — stable in `SkillDefinition.skillId` and save data |
| **Presentation** | **Fixed** for every launch class skill ([combat presentation](../02-systems/combat-presentation.md), [ADR 015](../../decisions/015-mvp1-combat.md)) |
| **Deploy** | **Summoner only** — `deploy_scout_drone` per [ADR 016](../../decisions/016-summon-control-mvp1.md); targets **aux back** |
| **Summon turns** | **Player-controlled** — minimal kit on `SummonDefinition` ([summons & guests](../02-systems/summons-and-guests.md)) |
| **Tree** | Flat **3 nodes** per class — no prerequisite chain; 1 skill point per node when allowed ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)) |
| **Use picker tabs** | **All** (default) + one tab per non-empty `SkillType` ([ADR 035](../../decisions/035-skill-use-picker.md)); **Type** column below = `SkillType` |
| **Numbers** | `mpCost`, `powerByRank[]`, inflict `%` — **tuning** in data; structure locked |
| **Descriptions** | `descriptionEn` on every `SkillDefinition` — **mechanical summary only**, no exact MP/power/% in prose ([game #149](https://github.com/miramocha/griddungeon-game/issues/149)) |
| **Picker display** | Row **`CostLabel`** (`{n} MP` from data); **`descriptionEn`** in focused detail panel only — see [custom skill picker UI](../04-dev/custom-skill-picker-ui.md) |

### Targeting (`TargetKind`)

| Column | Meaning |
|--------|---------|
| **Target** | `TargetingRule.kind` |
| **Back** | `canTargetBack` — ranged/spell/pierce may hit enemy back row when front empty or skill allows |
| **Pierce** | `pierce` — ignores front-row melee gate ([combat](../02-systems/combat.md)) |

---

## Master table — 18 class skills

| `skill_id` | Display name | `descriptionEn` | Class | Type | Target | Back | Pierce | Effect stub |
|------------|--------------|-----------------|-------|------|--------|------|--------|-------------|
| `vanguard_guard` | Guard Stance | Raise your defense for a short time. | Vanguard | Buff | Self | — | — | `defense_up` 2 turns on caster |
| `vanguard_shield_bash` | Shield Bash | Strike one enemy and may bind an arm. | Vanguard | Physical | SingleEnemy | — | — | Slash damage; 25% `bind_arm` |
| `vanguard_protect` | Protect Ally | Guard one ally on your formation row for one turn. | Vanguard | Buff | SingleAlly | — | — | **Guard** battle mod on **one** ally sharing caster `FormationRow` (core or aux), 1 turn |
| `breaker_power_slash` | Power Slash | Deal slash damage to one enemy. | Breaker | Physical | SingleEnemy | — | — | Slash damage (single-hit bread-and-butter) |
| `breaker_cleave` | Cleave | Deal slash damage to all occupied enemy slots. | Breaker | Physical | AllEnemies | — | — | Slash damage to **all occupied enemy slots** |
| `breaker_pierce_drive` | Pierce Drive | Piercing attack that can reach the back row. | Breaker | Physical | SingleEnemy | yes | yes | Pierce damage; may hit back row per pierce rules |
| `medic_heal` | Patch | Restore HP to one living ally. | Medic | Heal | SingleAlly | — | — | HP restore (`skillPower + TEC`); **living** allies only |
| `medic_purify` | Purify | Remove control and poison effects from one ally. | Medic | Heal | SingleAlly | — | — | Cleanse **Control** + **DoT** categories on ally |
| `medic_revive` | Revive | Revive a downed ally with a portion of max HP. | Medic | Heal | SingleAlly | — | — | **Downed** allies only → 25% max HP |
| `summoner_volt_bolt` | Volt Bolt | Deal volt damage to one enemy; may hit the back row. | Summoner | Elemental | SingleEnemy | yes | — | Volt damage (weak personal bolt) |
| `deploy_scout_drone` | Deploy Scout Drone | Deploy a scout drone to the aux back slot for limited rounds. | Summoner | Deploy | AuxBack | — | — | Spawn `scout_drone` aux back, **3** rounds; queue OK if occupied, fail on resolve if still occupied ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| `summoner_focus` | Focus | Raise your magic offense for a short time. | Summoner | Buff | Self | — | — | `magic_up` 2 turns on caster |
| `marksman_aimed_shot` | Aimed Shot | Piercing shot that can reach the back row. | Marksman | Physical | SingleEnemy | yes | yes | Pierce-tagged physical shot |
| `marksman_bind_shot` | Bind Shot | Piercing shot that may bind an enemy arm. | Marksman | Physical | SingleEnemy | yes | yes | Pierce damage; 30% `bind_arm` |
| `marksman_volley` | Volley | Piercing damage to all occupied enemy slots. | Marksman | Physical | AllEnemies | yes | — | Pierce damage to all occupied enemy slots |
| `tactician_rally` | Rally | Raise offense for all living allies and aux units. | Tactician | Buff | AllAllies | — | — | `offense_up` 2 turns on **living core six + aux** summons/guests |
| `tactician_weaken` | Demoralize | Lower one enemy's offense for a short time. | Tactician | Debuff | SingleEnemy | — | — | `offense_down` 2 turns |
| `tactician_field_mend` | Field Mend | Restore a small amount of HP to one living ally. | Tactician | Heal | SingleAlly | — | — | Minor HP restore (lower `skillPower` than `medic_heal`) |

---

## Per-class kits

### Vanguard (`vanguard`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `vanguard_guard` | Self mitigation — teaches Guard-adjacent buffs |
| 2 | `vanguard_shield_bash` | Single-target control pressure |
| 3 | `vanguard_protect` | Row partner protection (single ally, same row) |

### Breaker (`breaker`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `breaker_power_slash` | Reliable front-target DPS |
| 2 | `breaker_cleave` | AoE physical for choke points |
| 3 | `breaker_pierce_drive` | Back-row access via pierce |

### Medic (`medic`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `medic_heal` | Primary HP restore |
| 2 | `medic_purify` | Cleanse launch ailments ([status subset](../02-systems/combat-status-and-buffs.md)) |
| 3 | `medic_revive` | Post-fight recovery enabler (downed → fighting) |

### Summoner (`summoner`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `summoner_volt_bolt` | Personal ranged volt (no Elementalist at launch) |
| 2 | `deploy_scout_drone` | **Only** launch aux deploy — aux **back**, `scout_drone` |
| 3 | `summoner_focus` | Self buff before deploy / bolt spam |

**Deploy skill data:**

```yaml
skill_id: deploy_scout_drone
skill_type: Deploy
targeting: { kind: AuxBack }
presentation: Fixed
summon_definition_id: scout_drone
# Occupied aux back: fail cast, no MP spent
```

**Deploy vs traps:** Only Summoner has aux deploy skills at launch. Future Marksman **floor traps** are a separate exploration system — not aux-slot allies ([party & classes](../02-systems/party-and-classes.md#summon-skills--summoner-only)).

### Marksman (`marksman`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `marksman_aimed_shot` | Pierce single target |
| 2 | `marksman_bind_shot` | Control + damage |
| 3 | `marksman_volley` | AoE ranged |

### Tactician (`tactician`)

| Node | `skill_id` | Role in kit |
|------|------------|-------------|
| 1 | `tactician_rally` | Party-wide physical buff |
| 2 | `tactician_weaken` | Enemy debuff |
| 3 | `tactician_field_mend` | Light sustain (not a full Medic replacement) |

---

## Summon kit (`scout_drone`)

Not on guild class trees. Listed on `SummonDefinition.skillIds` for **player** command menu on drone turns ([ADR 016](../../decisions/016-summon-control-mvp1.md)).

| Command | `skill_id` / action | Target | Effect stub |
|---------|---------------------|--------|-------------|
| Attack | *(built-in)* | Per attack rules | Standard attack |
| Guard | *(built-in)* | Self | Guard |
| Skill | `volt_burst` | SingleEnemy | Volt damage |

| `skill_id` | Display name | `descriptionEn` | Type | Notes |
|------------|--------------|-----------------|------|-------|
| `volt_burst` | Volt Burst | Deal volt damage to one enemy; may hit the back row. | Elemental | `SkillDefinition` in ContentDB; **not** allocatable on Summoner tree |

---

## Locked implementation rules

**Locked 2026-05-22** — game implementation: [griddungeon-game #52](https://github.com/miramocha/griddungeon-game/issues/52).

| Rule | Detail |
|------|--------|
| **`medic_revive`** | Target validator: **downed allies only**; reject living |
| **`vanguard_protect`** | **Single** `SingleAlly` target; must share caster **`FormationRow`**; Guard mod on that ally only (core or aux) |
| **`deploy_scout_drone`** | May queue while aux back occupied; on AGI resolve if still occupied → **fail**, **no MP** |
| **`AllAllies`** | Living **core six + aux** summons/guests (not Navigator) |
| **`AllEnemies`** | All **occupied** enemy slots; after **row collapse**, shifted enemies count as front for melee |
| **Row collapse** | On enemy death, survivors shift forward ([combat](../02-systems/combat.md)) |
| **Inflict order** | **Damage**, then status roll if still alive |
| **Summon control** | Player command phase; **no** `SummonScriptRunner` for `scout_drone` |
| **MP / power** | Stub `powerByRank[0]` until balance pass |

---

## Related

- [Party & classes](../02-systems/party-and-classes.md) — roster, deploy rules
- [Summons & guests](../02-systems/summons-and-guests.md) — aux slots, `scout_drone` kit
- [Combat](../02-systems/combat.md) — damage pipeline, targeting, row collapse
- [05 — class design § content IDs](../05-class-design.md#content-ids-locked)
- [release scope](../00-release-scope.md) — checklist row
- [ADR 016](../../decisions/016-summon-control-mvp1.md) — summon player control
