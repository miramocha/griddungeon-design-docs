# ADR 015 — Combat

**Status:** Accepted  
**Date:** 2026-05-20  
**Amended:** 2026-05-23 — enemy formation aligned to **Etrian Odyssey IV+** (≤3 front + ≤3 back; **6** occupied max). Replaces prior **5** max / **≤2** back cap.

## Decisions (launch)

1. **Enemy layout:** **Front + back rows** (like party) — up to **6** slots total (**≤3** per row) per encounter design; melee targets enemy **front** before back unless pierce.
2. **Battle camera:** **Three-quarter** fixed angle on arena rig ([ADR 013](013-combat-scene-rendering.md)).
3. **Presentation:** All skills **`Fixed`**; cinematic/QTE stubbed ([combat presentation](../docs/02-systems/combat-presentation.md)). optional+ cinematics use Timeline events per [ADR 027](027-combat-cinematic-timeline-events.md).
4. **ADR 005 / mid-battle join:** **Off at launch** — FOEs frozen on grid during fights; ships in **Optional** ([ADR 005](005-foe-combat-patrol.md), [ADR 010](010-chain-foe-battle.md)).
5. **Pause (`Esc` in combat):** Pause menu — **Resume** / **Settings** only. **No** abandon fight or return to hub from pause; use **Flee** command.
6. **Random encounter flee:** Succeed/fail per roll; on success, party stays on **same cell** (no pushback). FOE flee uses [ADR 011](011-foe-flee-retreat.md).
7. **Damage pipeline:** Locked formulas in [combat](../docs/02-systems/combat.md#damage-pipeline-mvp1) — 3 elements (fire, ice, volt); physical + pierce/slash tags; hit/evasion clamp 5–95%.
8. **Status (launch) subset):** Poison, Sleep, Panic, Head Bind, Arm Bind, Offense/Defense Up & Down, Blind, Guard. **DoT can kill.** No leg bind, paralysis, burn, speed mods at launch.
9. **Synchro tuning:** Use draft charge table in [synchro-protocol](../docs/02-systems/synchro-protocol.md) as (launch) baseline; **one** Navigator (`guild_handler`) + **two** Protocol skills playable.

## Related

- [(launch) spec](../docs/00-release-scope.md)
- [Combat status & buffs](../docs/02-systems/combat-status-and-buffs.md)
