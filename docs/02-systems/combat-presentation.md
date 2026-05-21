# Combat Presentation (Spells & Skills)

How skills look and feel in battle — camera, animation, and VFX. Separate from [exploration FPV](../02-dungeon-navigation.md#camera--presentation).

## Default: fixed camera

**Most spells and skills** use the standard **fixed battle camera**:

- Single established angle for the encounter (side-on or three-quarter — art direction TBD).
- Camera **does not** cut, orbit, or change angle per cast.
- Optional **slight zoom** toward the primary enemy target on hit — subtle punch-in, then ease back to default framing before the next action.
- No dramatic camera moves; zoom is short and repeatable (tuned per skill or global default).
- Feedback = character portrait flash, slot VFX, screen shake (light), combat log, numeric popups.
- Fast to resolve; keeps AGI pacing readable.

Applies to: basic attacks, common elemental spells, heals, buffs, most enemy skills.

## Exception: cinematic skills

**Some spells** use **dynamic animation and camera**:

- Short scripted sequence: camera move, caster/enemy animation, full-screen or in-scene VFX.
- Used sparingly for impact — stratum bosses, ultimates, key story skills, rare party skills.
- Longer **presentation duration**; may hold input until sequence completes or skippable after first play (TBD).

## Authoring (data-driven)

Each skill references a **presentation profile**:

| Profile | Camera | Animation | MVP |
|---------|--------|-----------|-----|
| `Fixed` (default) | Same angle; optional slight zoom to target | Simple cast + VFX at targets | Yes — all skills |
| `Cinematic` | Scripted camera + timing | Custom clip / Timeline | 1–2 examples post-MVP |

```yaml
skill_id: alchemist_fire_burst
presentation: Fixed
vfx_prefab: vfx_fire_burst
zoom_to_target: true   # optional; slight punch-in on primary enemy

skill_id: stratum1_boss_eruption
presentation: Cinematic
cinematic_asset: cin_boss_eruption
skippable: true
```

## Combat flow integration

1. Player confirms skill + targets.
2. If `Fixed` → play VFX; optional target zoom; apply rules when VFX hits or on frame event; restore default framing.
3. If `Cinematic` → `CombatPresentationController` takes over camera rig; on complete → apply damage/effects.
4. Resume AGI queue.

**Rule:** Only one cinematic at a time; queue or block additional commands until done.

## UI / readability

- Fixed presentation must not obscure turn order strip or row HP.
- Cinematic may temporarily hide non-essential UI; restore before next player command.
- Combat log always records the mechanical result (even if player skipped cinematic).

## Tech sketch

- `BattleCameraRig` — default pose; `NudgeZoomToTarget(duration, strength)` for Fixed skills; handoff to cinematic sub-rig for Cinematic
- `SkillDefinition.presentation` → `Fixed | Cinematic`
- `CinematicSkillPlayer` — Unity Timeline or AnimationTrack per asset
- Exploration `DungeonView` camera **unchanged** — presentation system is combat-scene only

## MVP

- [ ] Fixed camera rig + one generic `Fixed` VFX pipeline for party and enemies
- [ ] All MVP skills use `Fixed`
- [ ] Cinematic pipeline stubbed; first cinematic skill in milestone 2

## Related docs

- [Combat](combat.md)
- [04 — Tech notes](../04-tech-notes.md)
- [02 — Dungeon navigation](../02-dungeon-navigation.md)
