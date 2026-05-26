---
name: stratum-floor-layout-check
description: >-
  Validates Grid Dungeon authored StratumFloor ASCII layouts (row width,
  walkability BFS, Act 1 funnel and tutorial gates) using griddungeon-game
  Tools/layout_grid_check.py. Use when editing floor layout ASCII in design-docs,
  reviewing s1_B1F map specs, or debugging path bypasses to stairsDown.
---

# Stratum floor layout check (design-docs)

Layout **implementation** and scripts live in **griddungeon-game**. This skill applies when you edit MVP1 ASCII or campaign funnel rules here; run checks in the game repo.

## When to use

- Editing [dungeons — s1_B1F ASCII](../docs/03-content/dungeons-and-encounters.md#s1_b1f--outskirts-gate-intro--gate) or [s1-intro](../docs/03-content/campaign/s1-intro.md)
- Reviewing whether doc coordinates match playable geometry
- Layout review before game implementation PR

## Workflow

1. Update ASCII in **design-docs** (keep rows **20 characters**, north-up, y=0 south — same as game builder).
2. Implement the same rows in game repo `S1B1FLayoutBuilder.cs` + `Tools/layout_grid_check.py` → `S1_B1F_ROWS`.
3. From **griddungeon-game** root:

```powershell
python Tools/layout_grid_check.py
python Tools/layout_grid_check.py --bfs 4,2 10,17
```

4. Full agent workflow: read game repo skill  
   `griddungeon-game/.cursor/skills/stratum-floor-layout-check/SKILL.md`  
   (coordinate table, built-in regressions, C# test parity).

## Doc ↔ code checklist

| Doc field | Game authority |
|-----------|----------------|
| `partyEntryIntro` `(4,2)` | `S1CampaignResolver.B1FIntroSpawn` |
| Gate / `stairsUp` `(10,11)` | `B1FGateSpawn`, `StairsUp` |
| `stairsDown` `(10,17)` | `StairsDown` |
| Tutorial blocker `X` `(10,13)` | `B1FTutorialBlockerCell` + `S1TutorialDiveStarted` walkability |

## Related

- Game implementation skill: [stratum-floor-layout-check](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-layout-check) (canonical)
- Asset sync: [stratum-floor-asset-sync](https://github.com/miramocha/griddungeon-game/tree/main/.cursor/skills/stratum-floor-asset-sync)
