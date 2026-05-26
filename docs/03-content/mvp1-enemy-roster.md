# MVP1 enemy roster (Stratum 1)

**Tracking:** [design-docs #2](https://github.com/miramocha/griddungeon-design-docs/issues/2) · **Implementation:** [game #12](https://github.com/miramocha/griddungeon-game/issues/12) (`ContentDatabase` + `EnemyDefinition` / `EncounterGroup` SOs)

**Authority split:**

| Topic | Doc |
|-------|-----|
| Floor grids, FOE YAML, per-floor random weights | [dungeons — MVP1 §](dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f) |
| Campaign acts, save flags, tutorial FOE rules | [campaign/s1-intro](campaign/s1-intro.md) · [foe-encounters — tutorial](../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker) |
| **This file** | Locked enemy IDs, stats stubs, skills, encounter groups, FOE ↔ group mapping |

Tuning numbers may move in data ([mvp1-spec §6](../mvp1-spec.md#6-open-for-tuning-only-locked-structure)); **IDs and group compositions are locked** for MVP1.

---

## Enemy definitions (9 types)

Combat uses `CharacterBaseStats` at spawn (no level scaling in MVP1). **ATK** in tables = **STR** for physical enemies; **TEC** for elemental skills. Resistances default **1.0** unless noted (`1.5` weak, `0.5` resist).

| Enemy ID | Display | Row | HP | MP | STR | TEC | AGI | VIT | LUC | Skill pool | Status immunities | XP | Notes |
|----------|---------|-----|----|----|-----|-----|-----|-----|-----|------------|-------------------|-----|-------|
| `stray_hound` | Stray Hound | Front | 36 | 0 | 9 | 2 | 8 | 4 | 3 | `enemy_attack` | — | 8 | Chaff melee |
| `rust_mite` | Rust Mite | Front | 28 | 0 | 6 | 2 | 6 | 3 | 2 | `enemy_attack` | — | 6 | Chaff weak; **Pierce 0.5** |
| `gutter_crow` | Gutter Crow | Back | 30 | 0 | 5 | 6 | 11 | 3 | 4 | `enemy_attack`, `atk_peck_volt` | — | 7 | Chaff flyer; **Pierce 1.5** |
| `scrapling` | Scrapling | Front | 22 | 0 | 7 | 1 | 9 | 2 | 2 | `enemy_attack` | — | 5 | Chaff swarm |
| `shackle_rat` | Shackle Rat | Front | 38 | 0 | 8 | 3 | 7 | 5 | 3 | `enemy_attack`, `atk_bind_arm` | — | 10 | Teaches `bind_arm` |
| `venom_slime` | Venom Slime | Front | 42 | 0 | 7 | 5 | 5 | 6 | 2 | `enemy_attack`, `atk_poison_spit` | — | 10 | Teaches `poison` |
| `alley_thug` | Alley Thug | Front | 58 | 0 | 13 | 2 | 7 | 7 | 3 | `enemy_attack`, `atk_heavy_swing` | — | 14 | Mid bruiser; FOE escort body |
| `rubble_guard` | Rubble Guard | Front | 72 | 0 | 14 | 1 | 4 | 12 | 2 | `enemy_attack`, `atk_guard_slam` | — | 16 | FOE escort tank |
| `s1_warden` | District Warden | Front | 200 | 0 | 16 | 8 | 9 | 14 | 5 | `enemy_attack`, `atk_warden_bind`, `atk_warden_venom` | `bind_head`, `poison` (immune) | 80 | Boss; `noFlee: true` on definition |

**Element resistances (non-default only):**

| Enemy ID | Slash | Pierce | Fire | Ice | Volt |
|----------|-------|--------|------|-----|------|
| `rust_mite` | 1.0 | **0.5** | 1.0 | 1.0 | 1.0 |
| `gutter_crow` | 1.0 | **1.5** | 1.0 | 1.0 | 1.0 |
| `venom_slime` | 1.0 | 1.0 | 1.0 | **1.5** | 1.0 |
| `s1_warden` | 1.0 | 1.0 | **0.5** | 1.0 | **1.5** |

**Loot (stub):** chaff enemies → empty or 5% `patch_kit` (tune in SO); `s1_warden` → guaranteed `patch_kit` ×1 + 50% `stim_draft` (post–[game #31](https://github.com/miramocha/griddungeon-game/issues/31)).

---

## Enemy skill stubs

Shared physical baseline plus per-enemy skills. Maps to `SkillDefinition` / `SkillData` ([05 — Class design](../05-class-design-mvp1.md#skills)); enemy AI picks from `skillIds` (MVP1: weighted random or cycle — implementation in game #12).

| Skill ID | Type | Element | Body | MP | Power (rank 1) | Target | On-hit status | Used by |
|----------|------|---------|------|----|----------------|--------|---------------|---------|
| `enemy_attack` | Physical | Slash | None | 0 | 10 | Single enemy | — | All |
| `atk_peck_volt` | Elemental | Volt | None | 0 | 8 | Single enemy | — | `gutter_crow` |
| `atk_bind_arm` | Physical | Slash | Arm | 0 | 6 | Single enemy | `bind_arm` 40%, 2 turns | `shackle_rat` |
| `atk_poison_spit` | Elemental | Ice | None | 0 | 6 | Single enemy | `poison` 50%, 3 turns | `venom_slime` |
| `atk_heavy_swing` | Physical | Slash | Arm | 0 | 14 | Single enemy | — | `alley_thug` |
| `atk_guard_slam` | Physical | Slash | None | 0 | 12 | Single enemy | — | `rubble_guard` |
| `atk_warden_bind` | Physical | Slash | Head | 0 | 10 | Single enemy | `bind_head` 35%, 2 turns | `s1_warden` |
| `atk_warden_venom` | Elemental | Ice | None | 0 | 12 | All enemies | `poison` 25%, 3 turns | `s1_warden` |

Status magnitudes follow [combat status & buffs](../02-systems/combat-status-and-buffs.md). `bind_*` blocks skills tagged with matching `BodyPart`.

---

## Encounter groups

`EncounterGroup` SO: `groupId`, `frontRow[]`, `backRow[]` (≤3 front / ≤3 back), optional `backgroundId`, `tutorialUnbeatable`, `noFlee` ([05 — enemies & encounters](../05-class-design-mvp1.md#enemies--encounters)). Slot order = left-to-right in combat UI.

### FOE & boss (authored spawns)

| Group ID | Front row | Back row | Flags | FOE / use |
|----------|-----------|----------|-------|-----------|
| `grp_alley_stalker` | `alley_thug`, `scrapling` | — | — | Standard alley patrol (post-tutorial replay; optional) |
| `grp_alley_stalker_tutorial` | `alley_thug` | — | `tutorialUnbeatable: true`, `noFlee: true` | `foe_alley_stalker` on `s1_B2F` only |
| `grp_s1_warden` | `s1_warden` (required) | — | `noFlee: true` | `foe_s1_warden` on `s1_B3F` |

### Random — `s1_B1F` (Act 3 only)

| Group ID | Front row | Back row | Floor weight |
|----------|-----------|----------|--------------|
| `grp_b1_chaff_hound` | `stray_hound`, `stray_hound` | — | 60 |
| `grp_b1_chaff_mite` | `rust_mite`, `rust_mite` | — | 40 |

`baseEncounterRate: 0.05` — see [B1F §](dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--gate).

### Random — `s1_B2F`

| Group ID | Front row | Back row | Floor weight | Teaches |
|----------|-----------|----------|--------------|---------|
| `grp_b2_chaff` | `stray_hound` | `gutter_crow` | 35 | Mixed rows |
| `grp_b2_shackle_rat` | `shackle_rat` | `scrapling` | 35 | `bind_arm` |
| `grp_b2_venom_slime` | `venom_slime` | — | 30 | `poison` |

`baseEncounterRate: 0.10` — [B2F §](dungeons-and-encounters.md#s1_b2f--collapsed-avenues-bind--poison--patrol-foe).

### Random — `s1_B3F`

| Group ID | Front row | Back row | Floor weight | Teaches |
|----------|-----------|----------|--------------|---------|
| `grp_b3_mix_hounds` | `stray_hound`, `stray_hound` | — | 45 | Chaff spike |
| `grp_b3_rubble_pair` | `rubble_guard`, `scrapling` | — | 35 | Bruiser + swarm |
| `grp_b3_control` | `shackle_rat` | `venom_slime` | 20 | Bind + poison mix |

`baseEncounterRate: 0.12` — [B3F §](dungeons-and-encounters.md#s1_b3f--flooded-underpass-stratum-boss).

---

## FOE vs random placement (per floor)

| Floor | Random encounters | FOE spawns | Notes |
|-------|-------------------|------------|-------|
| `s1_B1F` | Act 1: **off** (`rate 0`). Act 3: `grp_b1_chaff_hound` / `grp_b1_chaff_mite` @ **0.05** | **None** | FOE teaching starts B2F |
| `s1_B2F` | `grp_b2_chaff` / `grp_b2_shackle_rat` / `grp_b2_venom_slime` @ **0.10** | **`foe_alley_stalker`** → `grp_alley_stalker_tutorial` | Patrol `(12,11)` loop; B3F blocked until tutorial flag |
| `s1_B3F` | `grp_b3_mix_hounds` / `grp_b3_rubble_pair` / `grp_b3_control` @ **0.12** | **`foe_s1_warden`** → `grp_s1_warden` | Boss `(10,16)`; MVP1 win condition |

**FOE entity IDs** (map / save keys — not enemy definition IDs):

| FOE ID | Floor | Encounter group |
|--------|-------|-----------------|
| `foe_alley_stalker` | `s1_B2F` | `grp_alley_stalker_tutorial` |
| `foe_s1_warden` | `s1_B3F` | `grp_s1_warden` |

---

## ContentDatabase checklist (game #12)

Author under `Assets/Content/Enemies/` and `Assets/Content/Encounters/` per [05 — folder structure](../05-class-design-mvp1.md#folder-structure-game-repo).

| Asset kind | Count | IDs |
|------------|-------|-----|
| `EnemyDefinition` | 9 | All rows in [enemy definitions](#enemy-definitions-9-types) |
| `SkillDefinition` | 8 | `enemy_attack` + 7 `atk_*` (class skills are separate — [design #3](https://github.com/miramocha/griddungeon-design-docs/issues/3)) |
| `EncounterGroup` | 11 | All rows in [encounter groups](#encounter-groups) |

Wire floor `EncounterTable` / `FoeSpawnConfig.encounterGroupId` to match [dungeons YAML](dungeons-and-encounters.md#mvp1--stratum-1-b1fb3f). `EncounterGroup.tutorialUnbeatable` must be honored in combat ([foe-encounters](../02-systems/foe-encounters.md#tutorial-foe-s1--foe_alley_stalker)).

**Already aligned in game (verify when landing SOs):** `S1B2FLayoutBuilder` random table uses `grp_b2_*` weights 35/35/30; tutorial FOE uses `grp_alley_stalker_tutorial`.

---

## Issue #2 acceptance (documentation)

| Criterion | Status |
|-----------|--------|
| Enemy IDs documented (9 types) | ✅ [table](#enemy-definitions-9-types) |
| Encounter groups incl. `grp_alley_stalker`, `grp_alley_stalker_tutorial`, `grp_s1_warden` | ✅ [FOE & boss](#foe--boss-authored-spawns) |
| Stats/skills stubs for MVP1 fights | ✅ [stats](#enemy-definitions-9-types) · [skills](#enemy-skill-stubs) |
| FOE vs random per floor | ✅ [placement table](#foe-vs-random-placement-per-floor) · [dungeons](dungeons-and-encounters.md#mvp1-floor-summary) |
| Locked IDs in [05 — content IDs](../05-class-design-mvp1.md#mvp1-content-ids-locked) | ✅ (enemies, groups, skills, FOEs) |
| Unity SOs / `ContentDatabase` | ⬜ **game #12** |

---

## Related

- [mvp1-spec — combat content](../mvp1-spec.md#combat-adr-015)
- [combat scene — enemy slots](../02-systems/combat-scene.md)
- [synchro — S1 first FOE](../02-systems/synchro-protocol.md#s1-tutorial-gating-first-foe)
