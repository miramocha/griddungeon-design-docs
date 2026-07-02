---
tags:
  - path/docs/03-content
  - type/content
  - scope/required
  - status/accepted
  - domain/campaign/s1
---
# Content IDs (locked)

String IDs stable across **code**, **ScriptableObject assets**, and **save data**. Do not rename without team intent (pre-release — no migration shims).

**Schema / asset folders:** [content schema](content-schema.md). **Per-domain detail:** [class skills](class-skills.md), [enemy roster](enemy-roster.md), [character progression § launch equipment](../02-systems/character-progression.md#launch-equipment-locked).

---

<a id="content-ids-locked"></a>

| Type | ID | Notes |
|------|----|-------|
| Class | `vanguard`, `breaker`, `medic`, `summoner`, `marksman`, `tactician` | Day-one roster |
| Navigator | `guild_handler` | Sortie Lead; day one; aura: `synchroGainBonus = 0.05` — [navigator](../02-systems/navigator.md) |
| Protocol skill | `protocol_strike`, `protocol_mend` | Damage all enemies / heal all living core — [synchro-protocol](../02-systems/synchro-protocol.md) |
| Summon | `scout_drone` | Summoner-only; 3 rounds; **player-controlled** kit |
| Summon deploy skill | `deploy_scout_drone` | Summoner tree only; `SkillType.Deploy` → `scout_drone`, aux back ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| Summon skill | `volt_burst` | On `scout_drone` summon kit only — not on Summoner class tree |
| Stratum | `s1` | Stratum 1 |
| Floors | `s1_B1F`, `s1_B2F`, `s1_B3F` | Save/map keys |
| Items | `patch_kit`, `stim_draft`, `trauma_kit`, `return_thread`, `analysis_glass` | Starter consumables |
| Equipment | `guild_shortsword`, `leather_coif`, `leather_jacket`, `leather_boots`, `scout_charm` | Launch shop slice — [progression — launch equipment](../02-systems/character-progression.md#launch-equipment-locked) |
| Status | `poison`, `sleep`, `panic`, `bind_head`, `bind_arm` | Launch subset |
| Stat mods | `offense_up`, `offense_down`, `defense_up`, `defense_down`, `magic_up`, `magic_down`, `speed_up`, `speed_down`, `blind`, `regen` | |
| Enemy | `stray_hound`, `rust_mite`, `gutter_crow`, `scrapling`, `shackle_rat`, `venom_slime`, `alley_thug`, `rubble_guard`, `s1_warden` | [enemy-roster](enemy-roster.md) |
| Enemy skill | `enemy_attack`, `atk_peck_volt`, `atk_bind_arm`, `atk_poison_spit`, `atk_heavy_swing`, `atk_guard_slam`, `atk_warden_bind`, `atk_warden_venom` | Enemy pool only |
| Encounter group | `grp_alley_stalker`, `grp_alley_stalker_tutorial`, `grp_s1_warden`, `grp_b1_chaff_hound`, `grp_b1_chaff_mite`, `grp_b2_chaff`, `grp_b2_shackle_rat`, `grp_b2_venom_slime`, `grp_b3_mix_hounds`, `grp_b3_rubble_pair`, `grp_b3_control` | Slot layouts in roster doc |
| Random encounter table | `enc_s1_none`, `enc_s1_b1_chaff`, `enc_s1_act2_mid`, `enc_s1_act3_deep`, `enc_s1_stub` | Shared table SOs; floors reference by id ([dungeons § random encounter table](dungeons-and-encounters.md#random-encounter-table)) |
| FOE entity | `foe_alley_stalker`, `foe_s1_warden` | Map keys; not `EnemyDefinition` ids |

### Class skills (3 per class — locked)

**Full skill kit (targeting, effects, stubs):** [launch class skills](class-skills.md).

| Class | `skill_id` | `skill_id` | `skill_id` |
|-------|------------|------------|------------|
| Vanguard | `vanguard_guard` | `vanguard_shield_bash` | `vanguard_protect` |
| Breaker | `breaker_power_slash` | `breaker_cleave` | `breaker_pierce_drive` |
| Medic | `medic_heal` | `medic_purify` | `medic_revive` |
| Summoner | `summoner_volt_bolt` | `deploy_scout_drone` | `summoner_focus` |
| Marksman | `marksman_aimed_shot` | `marksman_bind_shot` | `marksman_volley` |
| Tactician | `tactician_rally` | `tactician_weaken` | `tactician_field_mend` |

All class skills: **`presentation: Fixed`** ([combat presentation](../02-systems/combat-presentation.md)).

**Optional side dungeon IDs (draft, optional — not required slice):** `sd01`, floors `sd01_F1`, `sd01_F2` — [side dungeons](../02-systems/side-dungeons.md).

---

## Related docs

- [Content schema](content-schema.md)
- [03 — Content index](README.md)
- [05 — Class design](../05-class-design.md) — C# types and assemblies
