# Tech Notes (Unity / URP)

EO alignment drives **auto-reveal map**, **FOE entities**, and **AGI combat queue** as first-class systems. **No map drawing tools.**

## High-level modules

```
GameState (hub | exploration | combat)
├── HubServices          — guild, shop, hospital, inn save
├── DungeonExplorer      — grid step, facing, interact
├── DungeonView          — FPV cell rendering
├── MapSystem            — auto-reveal layer, fog, read-only UI
├── FoeSystem            — spawn, visibility, step patrol, contact
├── PartyRuntime         — 6 core + 0–2 aux combatants, skills
├── CombatController     — AGI queue (core + aux + enemies), turn resolution
├── CodexSystem          — enemy knowledge / weaknesses
├── ContentDatabase      — strata, floors, FOE, encounters
└── SaveSystem           — hub save + per-floor revealed map + FOE state
```

## Map system

- **Revealed layer** (saved per floor):
  - `visited` floor tiles
  - `wallMask` per cell edge (set on bump + perimeter reveal)
  - `features`: door state, stairs, chest opened, trap triggered
  - `foeIcons`: last known FOE cell when in LOS
- **Truth layer** — designer collision (editor only); never sent to client as full download
- **UI:** read-only grid; pan/zoom; no edit raycasts
- `MapReveal.OnPartyEnteredCell`, `OnBumpWall(side)`, `OnInteract(type)`

## FOE system

- `FoeInstance` — id, grid pos, patrol path index, tier, encounter group
- `OnPartyStep()` → increment floor step count; FOEs with `stepsPerMove` advance patrol index
- Line-of-sight check for map icon reveal
- Collision → `CombatController.StartBattle(foeId)`
- **Optional later:** `TickCombatRound()` — 1 patrol cell per FOE per combat round ([ADR 005](../decisions/005-foe-combat-patrol.md)); flag-gated

MVP: step patrol system in core; early floors mostly `stepsPerMove: 0` or 1-cell paths. No combat-round FOE movement.

## Combat

- `TurnQueueBuilder.Build(combatants)` sorted by AGI
- UI binds to queue head; advance on action complete
- `CombatSimulator` pure C# for tests

## Combat presentation

- `BattleCameraRig` — fixed angle default ([combat presentation](02-systems/combat-presentation.md))
- `SkillDefinition.presentation`: `Fixed` (default) | `Cinematic`
- `Fixed` — VFX at slots; optional subtle zoom to primary target, then reset
- `Cinematic` — Timeline / scripted camera; blocks until complete or skip
- MVP: all skills `Fixed`; cinematic pipeline stub for later

## Grid / content

- `StratumFloor` ScriptableObject: grid, spawns, FOE list, encounter rate
- Labels: `B1F` within `Stratum01`

## Save format (EO-oriented)

```json
{
  "hub": { "gold": 0, "unlockedFloors": { "s1": "B3F" } },
  "party": [ /* 6 characters + skill allocations */ ],
  "maps": {
    "s1_B2F": { "visited": [], "walls": [], "features": [], "foeIcons": [] }
  },
  "foeState": {
    "s1_B2F": [{ "id": "stalker", "cell": [12,9], "alive": true }]
  },
  "exploration": null
}
```

When in labyrinth, `exploration` holds position, facing, floor id.

## UI layout (PC prototype)

```
┌─────────────────────┬──────────────┐
│   FPV dungeon view  │  Map (view)  │
│                     │  read-only   │
├─────────────────────┴──────────────┤
│  Log / party strip (HP, status)    │
└────────────────────────────────────┘
```

Combat replaces layout with turn order + **4+4 rows** (core + aux).

## Combatant types

```csharp
enum CombatantKind { Core, Summon, Guest, Enemy }
```

- `PartyRuntime` — 6 core, always
- `CombatController` — spawns aux from skills/scripts; clears on battle end

## Performance

- 60 FPS exploration with map visible
- FOE patrol: ≤10 active FOEs per floor
- Floor size: 40×40 soft max (EO floors vary)

## Open technical decisions

- [ ] Wall reveal: bump-only vs also reveal perimeter on cell entry
- [ ] Default `stepsPerMove` per stratum (tune 2–5)
- [ ] Custom Unity editor for FOE patrol paths + `stepsPerMove`

## Related docs

- [Mapping](02-systems/mapping.md)
- [ADR 002](../decisions/002-mapping-model.md)
- [ADR 003](../decisions/003-foe-step-patrol.md)
