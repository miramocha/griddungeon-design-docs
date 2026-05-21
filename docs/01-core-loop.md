# 01 — Core Loop

## Macro loop (EO-style)

```
Hub (Explorers Guild, Navigator Office, save, heal, shop)
    → Enter labyrinth at deepest unlocked floor
    → Explore: step grid + auto-map reveals + avoid/bait FOEs
    → Random battles + FOE fights + loot
    → Retreat (stairs up / return item) when resources low
    → Hub: sell, synthesize (**MVP2**), allocate skill points
    → Push next floor or next stratum
```

See [Hub & services](02-systems/hub-and-services.md) for facility list.

## Micro loop (exploration)

```
Input: move (forward / back / strafe) | turn | interact | toggle map view | menu
    → Step resolves (trap, random encounter roll)
    → Auto-reveal map (floor, walls on bump, etc.); on step: resolve FOE patrol (ADR 003)
    → Combat if random proc or FOE contact
```

**Map is read-only** — players consult it during exploration; nothing to draw.

## Micro loop (combat)

```
Combat start (identify FOE vs random for loot/XP tuning)
    → Build turn queue by AGI (see combat doc)
    → Each actor: command → resolve → deaths
    → Repeat until win, wipe, or flee
    → XP / loot → resume exploration
```

## Session arc (45–90 min EO-like)

| Phase | Player focus |
|-------|----------------|
| Hub prep (10 min) | Party/skills, active Navigator, gear, consumables, quest pick |
| Floor push (30–60 min) | Map new area, FOE routing, resource spend |
| Retreat (5 min) | Reach safe stairs or use return item |
| Hub payout (10 min) | Heal, shop, skill allocation, save |

## Exploration limits

**Unlimited steps** in the labyrinth — no TP, food, or clock limiting grid movement ([ADR 008](../decisions/008-campaign-defaults.md)). Tension comes from FOEs, encounters, and HP/MP resources, not step count.

## Risk / reward knobs

| Knob | Risk | Reward |
|------|------|--------|
| Depth | FOE tiers, encounter rate | Materials, gear, quest flags |
| FOE engagement | Hard fights | Better drops, shortcuts unlocked |
| Exploration coverage | Time in labyrinth | More map revealed, faster return routes |
| Resource spend | Gold, consumables | Safer boss/FOE attempts |

## Modes of play

| Mode | Description |
|------|-------------|
| **Exploration** | FPV dungeon + read-only map panel |
| **Combat** | Turn UI; exploration frozen |
| **Map view** | Larger read-only map (pan/zoom) |
| **Hub menus** | Explorers Guild, Navigator Office, shop, hospital, inn save |
| **Gather / fish** (**MVP2**) | Minigame at dungeon nodes → materials — [gathering & fishing](02-systems/gathering-and-fishing.md) |

## Win / lose

- **Stratum progress:** Defeat stratum boss or reach story floor gate.
- **Wipe:** GAME OVER → load last **inn save** at hub. Map for explored floors **retained**.
- **No permadeath** of roster by default (characters persist; hospital revives fallen after wipe load if needed).

## Related docs

- [Release scope](00-release-scope.md)
- [Hub & services](02-systems/hub-and-services.md)
- [Mapping](02-systems/mapping.md)
- [02 — Dungeon navigation](02-dungeon-navigation.md)
- [03 — Dungeons & encounters](03-content/dungeons-and-encounters.md)
