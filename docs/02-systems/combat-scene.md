# Combat Scene & Enemy Rendering

How encounters **leave exploration FPV** and present **enemies** during AGI combat. Locked: **battle arena + fixed backdrop** ([ADR 013](../../decisions/013-combat-scene-rendering.md)), not fighting inside the live dungeon geometry.

## Two modes (exploration vs combat)

```
┌─────────────────────────────────────────────────────────────┐
│  EXPLORATION (FPV)                                          │
│  Dungeon grid mesh, party anchor, FOE sprites on grid       │
│  Camera: blobber FPV rig                                    │
└───────────────────────────┬─────────────────────────────────┘
                            │ encounter
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  COMBAT (battle arena)                                      │
│  Themed backdrop + enemy slot rig + party UI strip          │
│  Camera: BattleCameraRig (fixed angle; see presentation doc)│
│  Dungeon FPV: hidden or heavily dimmed (still loaded)       │
└─────────────────────────────────────────────────────────────┘
```

| | Exploration | Combat |
|---|-------------|--------|
| **World** | Real floor cells | **Abstract stage** — not the cell mesh |
| **Enemies** | FOE icon/mesh on **grid cell** | Enemy art on **slot anchors** (0–4) |
| **Party** | Abstract (6 as one anchor) | Portraits + optional 3D silhouettes on UI row |
| **Camera** | Step/turn FPV | Fixed battle camera |

---

## Battle arena composition

### Backdrop (fixed background)

- **Full-screen or stage-framed** environment art per **stratum biome** (forest, cave, hall, etc.).
- Variants: `random`, `FOE`, `boss` optional overlays on same biome.
- Implementation options (pick per art budget):
  - **2D illustrated plate** (EO classic) — quad behind slots, URP unlit or lit
  - **3D set piece** — simple floor + skybox + props; camera never leaves rig
- **Not** a live render of the dungeon cell behind the party (rejected for MVP1).

`BattleBackground` ScriptableObject: `id`, `biome`, `prefab`, `lightingProfile`, `ambientAudio`.

### Enemy slots

Enemies are **not** placed at world `(x, y)` from the grid.

**Two layers — do not conflate:**

| Layer | What it is | MVP1 |
|-------|------------|------|
| **Tactical formation** | Front + back rows for targeting, melee, row collapse | **≤3 front + ≤2 back** (5 occupied max) — locked in [combat](combat.md#battle-layout), [ADR 015](../../decisions/015-mvp1-combat.md), `EncounterGroup.frontRow` / `backRow` |
| **Arena rig** | Backdrop-stage **anchors** where battle sprites/models attach | Up to **5 anchors** on one stage lineup; empty anchors hidden |

Combat UI and rules use **front/back rows** (like the party). The arena is **not** “enemies have only one tactical row” — it is a **fixed stage** with slot transforms instead of dungeon cells. Anchors may use depth offset or a single horizontal line; presentation follows occupied tactical slots.

```
   tactical front (≤3)     [ anchor 0 ] [ 1 ] [ 2 ]
   tactical back  (≤2)     [ anchor 3 ] [ 4 ]        ← may sit deeper on stage
        ─────────────────────────────────────────
                    backdrop
        ─────────────────────────────────────────
        [ Party UI: 3+3 core + aux + Navigator strip ]
```

| Anchor / slot | Content |
|---------------|---------|
| `0..4` | One arena transform per **occupied** enemy from `EncounterGroup` (front row fills left-to-right, then back — same order as combat UI per [mvp1-enemy-roster](../03-content/mvp1-enemy-roster.md)) |
| Join mid-fight | Next free **tactical** slot (front first, else back); slide-in on matching anchor ([chain FOE](chain-foe-battle.md)) |

**Enemy render mode** (per enemy definition, same slot rig):

| Mode | When | Notes |
|------|------|-------|
| **Sprite stack** | MVP1 default | 2D/2.5D billboard or layered sprite (EO HD style) |
| **3D model** | MVP1+ optional | Model on slot; idle + hit reacts |
| **Hybrid** | Bosses | 3D body + 2D VFX overlay |

Slot transform drives facing, hit flash, VFX spawn, and **cinematic** focus ([combat presentation](combat-presentation.md)).

### Party presentation

- **Primary:** UI portraits + HP/MP/status (readable AGI play).
- **Optional:** Low-poly 3D party silhouettes on near plane or omitted in MVP1.
- Navigator: strip only — not in slot row ([navigator](navigator.md)).

---

## Encounter transition

### Entry

| Trigger | Transition | Backdrop pick |
|---------|------------|---------------|
| **Random** | White flash / radial wipe ~0.4s | `floor.randomBattleBackground` |
| **FOE contact** | Stronger flash + FOE sting SFX | `foe.battleBackgroundOverride` ?? floor default |
| **Boss** | Longer wipe + optional title card | `boss.cinematicBackground` |

Sequence:

1. Freeze exploration input; store `fightAnchor` (cell, facing).
2. Hide or dim `DungeonView` (disable FPV camera, optional blur on last frame capture — cosmetic).
3. Enable `CombatLayer`: load backdrop, spawn enemies on slots from `EncounterGroup`.
4. Fade in battle UI + `BattleCameraRig` default pose.
5. Start AGI round (Protocol on core turn when Synchro is 100%).

### Exit

| Result | Transition |
|--------|------------|
| Victory / flee | Arena fade out → restore FPV at `fightAnchor` (flee may apply retreat cell per [foe-encounters](foe-encounters.md)) |
| Wipe | GAME OVER flow → hub (arena may cut to black) |

Exploration **FOE grid sprites** unchanged during fight (patrol paused); defeated FOEs update grid **after** exit resolve.

---

## World space — why not (reference)

**In-world combat** would:

- Reparent camera to a battle offset in the dungeon scene
- Spawn enemy meshes in the corridor in front of the party
- Require every cell to be combat-camera-safe

**Pros:** Spatial continuity, FOE “right there” feel.  
**Cons:** Clipping, lighting breaks, conflicts with **fixed battle camera** and **cinematic Timeline** rig; higher environment art cost.

Deferred unless a future **“immersive combat”** experiment flag is approved.

---

## Integration with other systems

| System | Arena behavior |
|--------|----------------|
| **Fixed / cinematic skills** | VFX target `EnemySlot` transforms; zoom toward slot center |
| **Cinematic QTE** | Full-stage Timeline; backdrop can dim UI edges |
| **FOE mid-battle join** | Spawn into slot; no FPV FOE walk-in |
| **Summons** | Aux slot in UI + optional sprite on party side of stage |
| **Map** | MVP1: `M` toggles read-only floor map (exploration data), not live arena — persistent map during fight **not locked** ([mapping § Consider / explore](mapping.md#consider--explore--map-during-combat)) |

---

## Content authoring

```yaml
# EncounterGroup (authoring — tactical rows, not grid cells)
battle_background: forest_clearing
front_row:
  - enemy_id: forest_wolf
  - enemy_id: forest_wolf
back_row: []   # optional second row; CombatScenePresenter maps rows → arena anchors

# FoeDefinition
foe_id: red_raptor
battle_background_override: forest_raptor_nest   # optional
grid_sprite: foe_raptor
encounter_group: raptor_pair
```

Grid `grid_sprite` (exploration) and `battle_prefab` / `battle_sprite` (combat) are **separate assets** linked by one enemy id.

---

## Tech (Unity 6)

- **`CombatScenePresenter`** — owns backdrop instance, slot rig, enemy spawn (presentation only; [ADR 017](../../decisions/017-game-phase-controller.md))
- Invoked from **`CombatPhaseController.OnEnter`**; torn down on `OnExit`
- `CombatEntryContext` → `ResolveBackground()`, `SpawnEncounter(EncounterGroup)`
- `DungeonView.SetVisible(false)` / `BattleCameraRig.enabled = true`
- Additive scene `CombatArena` or enabled root under `GameRoot`
- MVP1: one biome backdrop + sprite enemies on 5 slots

---

## Scope

| Milestone | Deliverable |
|-----------|-------------|
| **MVP1** | Arena transition, 1 backdrop, sprite slots, random + FOE entry |
| **MVP2** | Extra biome plates; optional 3D enemy on boss slot |
| **Later** | Blurred FPV snapshot plate; in-world experiment flag |

---

## Related docs

- [ADR 013 — Combat scene rendering](../../decisions/013-combat-scene-rendering.md)
- [Combat presentation](combat-presentation.md)
- [Combat](combat.md)
- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [FOE encounters](foe-encounters.md)
- [04 — Tech notes](../04-tech-notes.md)
