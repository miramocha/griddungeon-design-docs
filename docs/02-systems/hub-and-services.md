# Hub & Services (Guild town)

Exploration alternates with a **fixed hub** at the labyrinth entrance — not an open overworld. EO's town loop: prepare, dive one stratum, return before overextending.

## Hub locations (MVP1)

| Service | Function |
|---------|----------|
| **Explorers Guild** | Create/recruit **core** characters; register **6-member** party; **skill trees** ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)) |
| **Navigator Office** | View **unlocked** Navigators; assign **active** Navigator for next dive; preview aura + Protocol kit — **2D portrait roster** in UI ([navigator § Office presentation](navigator.md#presentation-at-navigator-office-locked-direction-for-explore)); **not** the labyrinth bottom-right 3D rig ([navigator § Consider / explore](navigator.md#consider--explore--navigator-3d-presence)) |
| **Shop** | Buy/sell weapons, armor, consumables |
| **Hospital** | Restore HP/MP; cure **all standard combat ailments/debuffs**; revive fallen members (fee) — see [status & buffs](combat-status-and-buffs.md) |
| **Inn / Camp desk** | Save game (**primary save point** — MVP1 has no autosave on exploration pause quit-to-title; see [ADR 014 §7](../../decisions/014-mvp1-exploration-map.md)) |
| **Quest counter** | Accept kill/gather/floor reach quests (optional MVP1) |
| **Synthesis** (**MVP2**) | Fuse dungeon materials → equipment — requires [gathering & fishing](gathering-and-fishing.md) |
| **Side expedition** (**MVP3**) | Travel to unlocked **non-strata** grid maps — [side dungeons](side-dungeons.md), [ADR 022](../../decisions/022-side-dungeons-mvp3.md) |

No real-time hub walking — **menu tree stays the interaction model**. A **single full-screen 3D guild-town** backdrop (same scene from first hub visit) with **root-menu camera pans** post-MVP1 gives place identity without avatar locomotion (see [Hub environment presentation](#hub-environment-presentation)).

### Service UI motion

Hub menus use the same **reactive, blocking** bar as combat and exploration ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)).

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Open / close service screen | Panel **fade/slide** | No — navigation only |
| Inn save | Brief **confirm flash** + text | Yes — before another service action |
| Hospital heal / revive | HP/MP bars **lerp**; ailment icons **fade out** | Yes |
| Shop buy / sell | Gold + stock row **pulse**; inventory slot update | Yes |
| Guild assign slot / spend skill point | Portrait **slide** into slot; skill node **highlight** | Yes |
| Navigator Office pick active | Portrait **glow**; aura preview **fade in** on core-six preview strip — **2D list only** (no corner 3D; see [navigator § Office presentation](navigator.md#presentation-at-navigator-office-locked-direction-for-explore)) | Yes |
| Return to hub (exploration gate `stairsUp`) | **Floor transition** fade/vignette via `TryReturnToHub` ([floor transition](floor-transition.md), [ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md)) | Yes — until hub phase ready |
| Leave hub → stratum | **Floor transition vignette** or fade fallback ([floor transition](floor-transition.md), [ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md)) | Yes — until exploration phase ready |
| Menu item **focus** (hover / scroll) | Background camera **pans** to service building ([§ below](#hub-environment-presentation)) — **post-MVP1** | No — navigation stays live |

### Guild vs Navigator Office

| | **Explorers Guild** | **Navigator Office** |
|---|---------------------|------------------------|
| **Who** | Six **core** guild members | **Navigators** (party leads, off-formation) |
| **Recruitment** | Yes — create/recruit core roster | **No** — unlock via strata / quests / events |
| **Party prep** | Formation, equipment, skill trees (hub) | Pick **one active** Navigator + aura/Protocol preview |
| **In labyrinth** | Fight, explore, earn XP; **skill trees** via party menu when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)) | Protocol execution + passives only |

Prepare roster and Navigator before a dive when convenient; **skill points** need not wait for hub return.

## Hub environment presentation

**Design direction:** the hub is a **readable 3D environment** (guild town at the labyrinth gate) behind the UI. The player still **picks services from menus** — no free-roam walking, no grid movement ([vision — non-goals](../00-vision.md)). **Menu focus** on the **root hub list** drives the camera so each service feels anchored in the world.

### Locked decisions

| Topic | Decision |
|-------|----------|
| **When focus → pan ships** | **Post-MVP1** — MVP1 hub is menus + services; camera pan is the first hub presentation pass after MVP1 |
| **Town layout** | **One environment** from the first hub visit (S1 Act 2) — same guild-town scene throughout; services unlock via menu, not by swapping hub maps |
| **Layout** | **Full-screen** 3D backdrop with **UI Toolkit overlay** on top (not split-pane) |
| **Sub-menus** | **No camera pans** inside service screens (shop tabs, guild skill tree, hospital actions, etc.) — panning applies only to the **root hub menu** |
| **Inside a service** | Camera **holds** the last root-menu anchor for that service; no tighter framing or secondary anchors on sub-menus |
| **Hub entry default shot** | **TBD** — leaning toward a **wide establishing** town view until the player moves root-menu focus; not locked yet |
| **Locked / unavailable root rows** | **No pan** — focus on a greyed-out service does not move the camera (avoids teasing buildings the player cannot use yet) |
| **Enter Stratum** (multiple strata unlocked) | **One shared gate** anchor — all **Enter Stratum** *N* entries use the same labyrinth  plaza camera pose |
| **Rapid root-menu scroll** | **Debounced settle** — pan only after root focus stays on one row ~**150–300 ms** (tune in playtest); no interruptible chase mid-scroll |
| **Ambient scene life** (NPCs, smoke, flags) | **Light ambient** motion in the backdrop — **later than MVP1** (author with post-MVP1 hub presentation or polish pass) |
| **Hub audio bed** | **Probably no** looping town ambience / music stem tied to the 3D backdrop — service UI SFX from [Service UI motion](#service-ui-motion) still apply |
| **Camera stack** | **Cinemachine 3** virtual cameras + session `CinemachineBrain` — **not** DOTween on a manual camera rig ([ADR 033](../../decisions/033-hub-environment-cinemachine.md)) |

**Reference synthesis (EO + Mary Skelter):** [game references — hub & town](../00-game-references.md#etrian-odyssey--hub--town-loop).

### Debounced pan (rapid scroll)

**Locked:** **debounced settle** — the camera does **not** chase every focus tick while the player scrolls the **root** list.

| Rule | Detail |
|------|--------|
| **Trigger** | Start pan only when the same root row stays focused for ~**150–300 ms** (default **200 ms** until playtest) |
| **During scroll** | Focus changes before the timer expires **reset** the debounce; no partial pan to skipped rows |
| **After settle** | One smooth lerp to that row’s anchor (cancel any in-flight pan from a *previous* settled target if focus moved again after debounce fired) |
| **Rejected** | **Interruptible chase** (immediate retarget on every focus change) — too busy when flicking Shop → Hospital |

Tune duration post-MVP1 if keyboard taps feel laggy or fast gamepad flicks never show a building.

### Menu focus → camera pan (post-MVP1)

| Input | Behavior |
|-------|----------|
| **Hover** (mouse / gamepad focus on **root** menu row) | After [debounce](#debounced-pan-rapid-scroll), pan to that service’s **anchor** |
| **Scroll / move selection** (keyboard, D-pad, stick on **root** hub list) | Same — debounced on **current highlighted root row** |
| **Confirm** (open service) | Open service UI; camera **stays** on that service’s root anchor — **no** sub-menu pans or zoom |
| **Back** (close service to root list) | Resume pan from **current root highlight**; if none focused, use entry default ([TBD](#locked-decisions), lean wide town) |

After debounce, **`HubEnvironmentPresenter`** blends via **Cinemachine 3** — raise the target service vcam **priority** (session brain on; exploration FPV rig off). Use brain blend settings or default Cinemachine blend; tune duration in playtest ([ADR 033](../../decisions/033-hub-environment-cinemachine.md)).

**Rejected for this model:** requiring the player to walk an avatar to a door before the shop opens — that is “full 3D hub walk,” out of scope for early versions.

### Service → backdrop anchor (targets)

Each hub menu entry maps to an **authored camera pose** (and optional look-at) aimed at a recognizable building or district in the scene.

| Hub menu / service | Backdrop focal point (example) |
|--------------------|--------------------------------|
| **Explorers Guild** | Guild hall / training yard |
| **Navigator Office** | Navigator lodge or guild annex |
| **Shop** | Shop front / market stall row |
| **Hospital** | Hospital / clinic building |
| **Inn / Camp desk** | Inn or camp desk exterior |
| **Quest counter** | Notice board / guild quest hall wing |
| **Enter Stratum** *N* (any *N*) | **One shared** labyrinth gate plaza — same anchor for every stratum entry row |
| **Side expedition** (MVP3) | Caravan yard / expedition board ([side dungeons](side-dungeons.md)) |
| **Synthesis** (MVP2) | Workshop / forge annex |

Anchors are **authored `CinemachineCamera` poses** in the hub town scene (one per root slot + optional establishing wide shot), mapped to `HubRootMenuSlot` in presenter data so layout artists tune framing in Inspector without code changes ([ADR 033](../../decisions/033-hub-environment-cinemachine.md)).

### Presentation vs gameplay lock

Camera pan on menu focus is **ambient presentation** — it must **not** take the global [UI presentation lock](../04-tech-notes.md#ui-reactivity) used for inn save, shop confirm, or hospital heal. The player can scroll the menu while the camera moves.

Service screens may still use the **Service UI motion** table above for panel tweens and blocking confirms.

### Implementation sketch (game repo)

| Piece | Role |
|-------|------|
| `HubEnvironmentPresenter` | Hub phase: enable session `CinemachineBrain`, disable `ExplorationCameraRig`; after debounce, `PanToAnchor(HubRootMenuSlot)` via **vcam priority** |
| Hub town scene | `CinemachineCamera` per service + optional `CM_Establishing_Wide`; shared gate vcam for **Enter Stratum** |
| `HubHudView` / root focus | Emits slot focus changes (`MenuFocusNavigator` + `HubRootMenuSlot`); no pan while service panel open |
| `HubPhaseController` | Enables backdrop + presenter on enter; tears down on exit |
| `ExplorationCameraSession` | Brain on/off coordinated with floor-transition lock so vignette and hub do not fight |

Pattern parallels **floor transition** ([ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md)) for brain + priority, and **combat arena presentation** ([combat presentation](combat-presentation.md), [ADR 013](../../decisions/013-combat-scene-rendering.md)) for phase-owned lifecycle.

**Cinemachine detail:** [ADR 033](../../decisions/033-hub-environment-cinemachine.md).

### Release scope

| Phase | Hub backdrop & camera |
|-------|------------------------|
| **MVP1** | Menu tree + services (required). **Same** guild-town environment art/layout from first hub visit is fine to author early; **static** or simple backdrop OK if pan is not wired yet. **No** focus → pan |
| **Post-MVP1** | Wire **root-menu focus → pan**; full-screen 3D + UI overlay; anchors per service table above |
| **Defer** | Polished building pass; **light ambient** scene life (NPC idle, VFX); avatar walk-up; sub-menu camera moves; hub **looping ambience** (likely cut) |

**Acceptance (post-MVP1, when pan is wired):** scrolling the **root** list from **Shop** to **Hospital** reframes the environment to each building; opening shop/hospital sub-menus does **not** move the camera again.

## Macro loop (EO-aligned)

```
Hub → Guild (party/skills) + Navigator Office (active lead) + shop/equip
    → Enter stratum — spawn rule per stratum; Synchro **100%** on exit except S1 before first FOE ([synchro](synchro-protocol.md#s1-tutorial-gating-first-foe))
    → Explore (auto-map) → Fight (random + FOE) → Gather loot
    → Retreat via first-floor stairs up (gate) or Return thread when low
    → Hospital + shop + guild + Navigator Office → Repeat
    → (MVP3) Side expedition — optional non-strata maps; exit → hub only ([side dungeons](side-dungeons.md))
```

**New game exception:** Stratum 1 starts with **Act 1 on `s1_B1F`** (movement, no hub yet) — see [S1 campaign intro](../03-content/campaign/s1-intro.md).

## Stratum 1 intro

Full three-act flow, save flags, and entry rules: **[campaign/s1-intro.md](../03-content/campaign/s1-intro.md)**.

**Act 2 (this doc):** first hub visit after Act 1 — unlock services, **Explorers Guild** fills **6 core** slots, **Navigator Office** assigns `guild_handler`, inn save; enable **Enter Stratum 1** when `s1_party_ready`. Hub only — no labyrinth grid, no combat.

**Act 3 from hub:** **Enter Stratum 1** → always **B1F gate** `(10, 11)` (`stairsUp`); Synchro **0%** until mid–first FOE on B2F ([synchro § S1 gating](synchro-protocol.md#s1-tutorial-gating-first-foe)).

## Stratum structure

- Labyrinth divided into **strata** (biome-themed zones), each with multiple **floors**.
- Example: Stratum 1 "Fallen District" — floors B1F–B5F (MVP1: B1F–B3F + boss on B3F).
- **Stratum entry (locked):** party always starts at the **beginning** of a stratum (entrance floor). **S1:** no warp gate — hub **Enter Stratum 1** → B1F gate; **S2+:** hub entry only after that stratum’s **warp gate** is unlocked in-world, then warp to the gate cell on the entrance floor ([dungeons](../03-content/dungeons-and-encounters.md#stratum-entry--warp-gates-locked)).
- **First-floor gate `stairsUp`:** → **hub** only (all strata).

## Quests (optional MVP1)

| Type | Objective | Example reward |
|------|-----------|----------------|
| Hunt | Kill N of enemy type | Gold, item |
| Survey | Reach floor | Unlock shop stock |
| Gather | Bring materials | Synthesis unlock |

## Save model (EO-aligned)

- **Save at hub** (inn) — primary.
- **No save in labyrinth** for classic feel; optional **camp item** rare consumable for mid-stratum save (late feature).
- Wipe → GAME OVER → load last hub save; **map data for strata already visited persists**.

## Hub travel (stratum vs side)

| Destination | Hub action | Entry API (draft) |
|-------------|------------|-------------------|
| **Stratum** labyrinth | **Enter Stratum** *N* | `LeaveHub(stratumId, floorId)` |
| **Side dungeon** (MVP3) | **Side expedition** → pick location | `EnterSideDungeon(locationId, floorId)` |

Strata: warp-gate unlock + beginning-only hub entry (S2+); S1 gate entry. Side dungeons use **menu entry only** and **hub-only** exit — see [side dungeons](side-dungeons.md).

## Related docs

- [Side dungeons (MVP3)](side-dungeons.md)
- [Release scope](../00-release-scope.md)
- [Gathering & fishing (MVP2)](gathering-and-fishing.md)
- [01 — Core loop](../01-core-loop.md)
- [Character progression](character-progression.md)
- [Navigator](navigator.md)
- [Synchro Protocol (team bar)](synchro-protocol.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
