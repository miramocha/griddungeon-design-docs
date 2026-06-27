# Input Bindings (PC)

**Platform:** PC first ([ADR 008](../../decisions/008-campaign-defaults.md)). Keyboard + mouse primary; **gamepad deferred**.

Bindings use **Unity 6** + **Input System** (`com.unity.inputsystem`) action maps: `Exploration`, `Combat`, `UI`, `Map` ([ADR 012](../../decisions/012-unity-6-stack.md)). Runtime routing: `InputRouter` → handlers ([exploration UI](exploration-ui.md#input-routing), [game phase](game-phase.md#input-maps-per-phase)).

## Universal PC UI vocabulary

**Authority:** [ADR 009 § Universal UI vocabulary (2026-06)](../../decisions/009-input-bindings-pc.md#amendment-2026-06--universal-ui-vocabulary). Hub, combat command UI, party menu, and tabbed pickers share one **menu vocabulary**. Phase sections below add detail; when a modal or overlay owns input, this table wins over exploration movement.

| Role | Keyboard | Mouse | Input System (menu surfaces) |
|------|----------|-------|------------------------------|
| **Navigate / focus** | `W`/`A`/`S`/`D` + arrows | Hover + LMB on focusable control | `MenuNavigate` (2D vector) |
| **Confirm** | `Z` | LMB on focused or clicked control | `MenuConfirm` |
| **Cancel / back** | `X` | RMB | `MenuCancel` |
| **Tab cycle** | `Q` / `E` | LMB on tab chip | `*TabPrev` / `*TabNext` (scoped per overlay) |
| **Menu / pause** | `Tab` / `Esc` | — | `PartyMenu` / `Pause` (phase-specific) |

**Gamepad-ready clustering:** new binds should prefer **`WASD`**, face row **`Z` / `X` / `C` / `V`**, and **`Q` / `E`** ([§ Gamepad-ready layout](#gamepad-ready-keyboard-layout-deferred-implementation)). **`V`** = combat log. **`C`** = expanded-map autopilot. **`Tab` / `Esc`** → **Menu** / **Options**; **`M`** → **View** (Xbox) / **touchpad click** (DualSense). No **`Space`** / **`Enter`** in `GridDungeon.inputactions` — use **`Z`**. Full PC vs pad table: [§ PC vs console reference](#pc-vs-console-reference-locked-intent).

**Mouse parity:** UITK `Button` controls activate on **LMB** without an extra `Z`. Keyboard **`Z`** is the **focus-then-confirm** path on the same control. Combat focus-nav surfaces share **hover highlight** with keyboard focus; LMB on a command or valid target still **instant-queues** (no extra confirm) per [ADR 026](../../decisions/026-combat-menu-focus-navigation.md) ([2026-06 pointer amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)).

### Overlay ownership

When a **party menu**, **skill/item picker**, **hub service panel**, or other modal owns input:

- Universal vocabulary applies (`MenuNavigate`, `MenuConfirm`, `MenuCancel`, scoped `Q`/`E` tab actions).
- Exploration **turn** (`Q`/`E`) and **movement** (`W`/`A`/`S`/`D`) are **gated** — `InputRouter` enables tab actions only on the active pane and does not emit exploration turn while overlays are open ([party menu § Scope](#party-menu-tab), [skill picker § Scope](#skill-use-picker-modal)).

### Exploration FPV exception

With **no** overlay owning input, labyrinth FPV uses `W`/`A`/`S`/`D` and arrows for **grid displacement** (not menu focus), and **`Q`/`E`** for **90° turn** (not tab cycle). See [Exploration](#exploration) below. Map **autopilot destination pick** reuses universal navigate (`WASD` / arrows = cursor, **`C` / LMB** = arm pick + confirm destination, **`X`** = cancel pick). **`Z`** stays **`Interact`** while the expanded map is open (stairs, doors, gather) — autopilot does **not** steal universal confirm on that surface.

### Menu / pause (`Tab` / `Esc`) by phase

| Phase | `Tab` | `Esc` |
|-------|-------|-------|
| **Hub** | Toggle party menu when safe | Toggle party menu when safe (same as `Tab`) |
| **Exploration** | Toggle party / pause menu when safe | Priority stack: cancel autopilot → exit fullscreen map → close menu if open → open menu ([autopilot](#autopilot-mvp2), [map](#map-read-only)) |
| **Combat** | Not party menu (legacy `CycleTarget` bind deferred) | **Pause** when pause UI ships ([ADR 015](../../decisions/015-mvp1-combat.md)); **not** LIFO Back |

### Design principles (phase summary)

- **Exploration:** grid actions on keyboard; no mouse movement in FPV; exception table above when overlays closed.
- **Combat:** instance of universal vocabulary on command bar + target list + pickers ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)).
- **Map:** mouse pan/zoom when map panel focused or fullscreen.
- **Rebindable** in settings menu At launch: ship with defaults below; store overrides in player prefs).

---

## Exploration

Active during labyrinth FPV (not in combat, not in modal menus).

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move forward** | `W` | Displacement |
| **Move backward** | `S` | Displacement |
| **Strafe left** | `A` | Displacement (trial layout — was EO `Q`) |
| **Strafe right** | `D` | Displacement (trial layout — was EO `E`) |
| **Turn left** | `Q` | No step events (trial layout — was EO `A`) |
| **Turn right** | `E` | No step events (trial layout — was EO `D`) |
| **Interact** | `Z` | Door, chest, stairs, gather, hub gate, stratum transitions |
| **Toggle map** | `M` | Side panel ↔ fullscreen map |
| **Party / pause menu** | `Tab` or `Esc` | Same overlay when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md), [ADR 036](../../decisions/036-party-inventory-model.md)): **Inventory**, **Equipment**, **Quit to title** (hub + exploration; confirm pane → `RequestQuitToTitle`, no inn save). **Skills** / **Tutorial codex** deferred ([guided-tutorial](guided-tutorial.md#codex), [ADR 029](../../decisions/029-guided-tutorial.md)). Exploration: `Esc` cancels autopilot / exits fullscreen map **first**; when pause shell is open, **Esc closes** the menu (`Exploration.Pause` stays enabled while menu open). | Global hint on shell: `[Esc] Close` ([shared menu § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints)). |

**Arrow keys** duplicate `W/S` (forward/back) and left/right arrows (turn). Strafe (`A`/`D`) has no arrow duplicate.

**Movement (`W`/`S`/`A`/`D` and forward/back arrows)** and **turn (`Q`/`E` and left/right arrows)** use **hold** for repeat ([ADR 001](../../decisions/001-grid-movement.md)):

- While an explorer **lerp** is playing (durations per [ADR 018](../../decisions/018-exploration-animation-speed.md) preset; Normal: step ~0.32s, turn ~0.26s): **no** new commit of that action type and **no** buffered input.
- When the lerp **ends**, re-check `IsPressed` on held actions; if a movement key is still held, take **one** displacement (priority over turn); else if a turn key is still held, take **one** 90° turn.
- A tap during lerp only leads to another step/turn if the key is **still held** when the lerp finishes (no mid-lerp queue).
- **Turn** does not fire step events (no FOE tick, no random encounter).

**Settings (deferred):** Exploration animation speed — Slow / Normal / Fast / Very Fast ([ADR 018](../../decisions/018-exploration-animation-speed.md)); stored in player prefs when the settings UI ships.

### Autopilot

| Action | Input | Notes |
|--------|-------|-------|
| **Arm destination pick** | **`C`** on fullscreen map | Enter cursor mode ([autopilot](autopilot.md), [ADR 021](../../decisions/021-autopilot-mvp2.md)) |
| **Confirm destination** | **`C`** or click revealed walkable cell | Pathfind + walk; expanded map only (side minimap pick deferred) |
| **Cancel autopilot** | `Esc`, any move/turn/interact, or disengage pick (**X**) | Immediate; `Esc` also closes pause menu when shell open |

**`Z` interact** (stairs, doors, chests, gather) remains available while the expanded map is open — autopilot arm/confirm uses **`C`** so it does not conflict with confirm on the same key.

---

## Map (read-only)

Active when map panel is visible or fullscreen (`M`).

| Action | Input | Notes |
|--------|-------|-------|
| **Pan** | Mouse drag (LMB hold) | Move view over grid |
| **Zoom in** | Mouse wheel up | Clamp min/max zoom |
| **Zoom out** | Mouse wheel down | |
| **Recenter on party** | `Home` or `P` | Snap view to party cell |
| **Close fullscreen map** | `M` or `Esc` | Return to exploration layout |
| **Arm / confirm autopilot** | **`C`** or LMB on revealed walkable cell | Expanded map only; see [Autopilot](#autopilot) |
| **Disengage destination pick** | **`X`** | Exit cursor mode without walking |

Map does not capture `W/A/S/D` while fullscreen unless focus explicitly on map-only mode — **default:** fullscreen map still allows movement keys to pass through to exploration (map stays visible). **`Z` interact** also passes through while fullscreen (stairs, doors, etc.). Alternative: movement disabled in fullscreen — **use pass-through** for EO-like flow.

---

## Combat

**Authority:** [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md). Global combat UI keys: **arrows or `W`/`A`/`S`/`D`** = move focus (`W`↑ `S`↓ `A`← `D`→, same as arrows), **`Z`** = confirm, **`X`** = cancel / Back, **`V`** = toggle battle log, **`Esc`** = pause (no-op until pause UI ships). **`R`** is not used for Back. Exploration `W`/`S`/`A`/`D` do **not** apply while the Combat map is active.

### Command bar (planning + player-controlled turns)

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move focus** | Arrow keys or `W` / `A` / `S` / `D` | Active scope: command bar or target list; WASD mirrors arrows ([ADR 026 amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-05-23-wasd-menu-navigate)) |
| **Confirm** | `Z` | Queue focused command, confirm target, or activate **Back button** |
| **Cancel / Back** | `X` | Cancel targeting, or LIFO undo last queued command when planning |
| **Toggle battle log** | `V` | Log modal; **`X`** also closes while open |
| **Pause** | `Esc` | Pause menu (incl. **Tutorial codex** when unlocked — [ADR 029](../../decisions/029-guided-tutorial.md)); no-op until UI ships ([ADR 015](../../decisions/015-mvp1-combat.md)) |

| Action | Mouse | Notes |
|--------|-------|-------|
| **Move focus** | Hover command button | Shares highlight with keyboard focus ([ADR 026 amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)) |
| **Command** | LMB on bar button | **Instant** queue (no extra `Z`) |
| **Back button** | LMB | Same as `X` when enabled |

**Command bar items (focus order):** Attack → Guard → Skill → Item → Flee → **Back button**. Default focus when a core’s planning starts: **Attack**. Skip disabled/hidden entries.

**Planning flow:** One command per living core in **formation order** ([game #58](https://github.com/miramocha/griddungeon-game/issues/58)); auto-advance after each confirm. **No roster arrow-nav** — use **`X`** / **Back button** to LIFO undo ([game #61](https://github.com/miramocha/griddungeon-game/issues/61)). **Pointer** hover / LMB on a living core may re-select that core or refresh the skill picker when Skill flow is active ([ADR 026 amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)).

### Protocol (Synchro 100%)

On the **synchro bar** (bottom center) when **Synchro Charge = 100%** and **unlocked** ([synchro-protocol](synchro-protocol.md)). **`C`** or **LMB** on the bar queues Protocol when rules allow — not on the command rail. Global hint adds **`[C] Protocol`** while ready during core command planning. **`1`–`9` hotkey skill slots** deferred ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+) — not the tabbed **Skill** modal ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](../04-dev/custom-skill-picker-ui.md)).

### Command planning — targeting

After **Attack** or single-target **Skill** ([#60](https://github.com/miramocha/griddungeon-game/issues/60)):

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move target focus** | Arrow keys or `W` / `A` / `S` / `D` | Valid slots only; first valid slot highlighted on enter |
| **Confirm target** | `Z` | Queue command with `TargetId`; advance to next core |
| **Cancel targeting** | `X` or **Back button** (+ `Z` on focused Back) | No command queued; return to command bar (default focus Attack) |

**Path B:** entering targeting **moves focus to the target list**; command bar **`Z`** is ignored until targeting ends.

| Action | Mouse | Notes |
|--------|-------|-------|
| **Move target focus** | Hover valid slot | Shares highlight with keyboard focus ([ADR 026 amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-06--pointer-parity-menu-surfaces-within-combat)) |
| **Pick target** | LMB on valid slot | Instant confirm ([#60](https://github.com/miramocha/griddungeon-game/issues/60), keyboard [#70](https://github.com/miramocha/griddungeon-game/issues/70)) |

### AGI turn phase (default at launch)

Living cores already queued during planning — **no** per-core command bar on AGI slots. **Summon** and legacy per-slot control use the same **focus + `Z` / `X`** model ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md), [ADR 016](../../decisions/016-summon-control-mvp1.md)).

### Round-end confirm (separate)

Optional **confirm all assignments** before AGI playback — [#44](https://github.com/miramocha/griddungeon-game/issues/44); **not** the same as per-command **`Z`** confirm.

### Skill use picker (modal)

When the **skill use picker** is open ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](../04-dev/custom-skill-picker-ui.md)) — after **Skill** on the command bar (shipped [#138](https://github.com/miramocha/griddungeon-game/issues/138)) or **Use skill** in field UI ([#140](https://github.com/miramocha/griddungeon-game/issues/140) deferred):

| Action | Keyboard at launch | Notes |
|--------|-----------------|-------|
| **Previous tab** | **`Q`** | Cycles visible tabs (wrap); default tab **All** |
| **Next tab** | **`E`** | |
| **Move row focus** | Arrows or `W` / `A` / `S` / `D` | Active tab’s skill list only |
| **Confirm skill** | `Z` | Then combat targeting or field apply |
| **Cancel picker** | `X` | Close modal; no command queued |
| **Pick tab (optional)** | LMB on tab | Same tabs as Q/E cycle |

**Deferred:** gamepad — **`L1`/`R1`** tab cycle and shoulder/d-pad row nav when platform gamepad support ships ([ADR 009](../../decisions/009-input-bindings-pc.md)); not required for picker at launch.

**Scope:** `InputRouter` enables **`SkillPickerTabPrev` / `SkillPickerTabNext`** only while the picker is open. **`Q`/`E`** must **not** emit exploration turn events during this overlay (combat has no exploration map; field picker runs under pause/party modal with movement already blocked).

### Party menu (`Tab`)

When the **party menu** is open ([ADR 036](../../decisions/036-party-inventory-model.md), [items & inventory](items-and-inventory.md)) — **`Tab`** in hub or exploration when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)):

#### Shell (always while menu open)

| Action | Keyboard at launch | Notes |
|--------|-----------------|-------|
| **Open / close menu** | **`Tab`** | Toggle |
| **Open active pane** | **`Z`** | Shows Inventory or Equipment body (section nav stays visible) |
| **Previous section** | **`W`** or **↑** | **Inventory** ↔ **Equipment** (v1 only); works on shell and when pane is open but **not** engaged |
| **Next section** | **`S`** or **↓** | Pane swaps immediately when section changes (hub service style) |
| **Back** | **`X`** | Hide pane → shell; from shell, closes entire menu |

**Scope:** section navigation uses **`MenuNavigate`** vertical axis — **not** `Q`/`E` at shell level. While a pane is **engaged** (bag rows, worn slots, or equipment sub-picker), **W/S** navigate inside the pane instead of sections.

#### Inventory pane (when section = Inventory)

| Action | Keyboard at launch | Notes |
|--------|-----------------|-------|
| **Previous category tab** | **`Q`** | Cycles **All** / Consumables / Equipment (Materials MVP2); default **All** |
| **Next category tab** | **`E`** | |
| **Move slot focus** | Arrows or `W` / `A` / `S` / `D` | Active category’s bag rows only |
| **Confirm** | `Z` | Use consumable when implemented; **no equip** from bag in v1 |
| **Pick tab (optional)** | LMB on tab | Same tabs as Q/E |

#### Equipment pane (when section = Equipment)

| Action | Keyboard at launch | Notes |
|--------|-----------------|-------|
| **Previous member** | **`Q`** | Active party cores only (wrap); updates **member tab** strip |
| **Next member** | **`E`** | |
| **Pick member (optional)** | LMB on member tab | Same members as Q/E |
| **Move worn-slot focus** | Arrows or `W` / `S` | Weapon / Head / Body / Legs / Accessory (after **Z** engage) |
| **Confirm slot** | `Z` | Open **bag sub-picker** filtered to slot + class |
| **Sub-picker: confirm row** | `Z` | Equip, **Replace**, or **Remove** |
| **Sub-picker: cancel** | `X` | Back to worn-slot grid |

**Scope:** `InputRouter` enables **`InventoryBagTabPrev` / `InventoryBagTabNext`** **only** while the **Inventory** pane is active; routes **`Q`/`E`** to **member cycle** while **Equipment** pane is active. **`Q`/`E`** must **not** emit exploration **turn** events on F2 while the party menu is open.

**Deferred:** gamepad **`L1`/`R1`** — same as skill picker ([ADR 009](../../decisions/009-input-bindings-pc.md)); Skills / Formation party-menu sections.

### Combat UI (any time in fight)

| Action | Input | Notes |
|--------|-------|-------|
| **Toggle combat log** | `V` or click preview row | Opens/closes `combat-log-modal`; **`X`** / Back closes modal before pickers (`CombatPlayerCommandGate.TryBack` order). Global hint: **`[V]` / `[X]` Close** when open ([shared menu & picker UI § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints)) |
| **Toggle map** | `M` | Read-only floor map |
| **Pause** | `Esc` | When pause UI ships — all phases ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)) |

### Cinematic QTE

During **`CinematicQTE`** skills only ([combat presentation](combat-presentation.md)). Exploration/combat command maps are **paused**.

| Action | Input | Notes |
|--------|-------|-------|
| **QTE prompt** | Shown on HUD (`Space`, `1`–`5`, or `LMB`) | Must match prompt; timing window per beat |
| **Skip cinematic** | `Esc` | After first clear or 0.5s delay; resolves at **base** tier |
| **Skip (alt)** | Hold `Space` 0.5s | Optional duplicate bind for skip |

Enemy **`Cinematic`** (no QTE): `Esc` skip only. Settings: **Auto QTE** (Good tier), **Skip all cinematics** — accessibility.

---

## Global input hints

Bottom-right overlay chip (`InputHintPresenter`, `sortingOrder` 300) shared across hub, combat, exploration minimap, party menu, and post-battle victory. Hosts publish **input bind copy only** — `[Key] Verb` segments (e.g. `[Z] Confirm`, `[M] Map`) — via `InputHints.Publish(gameState, text)`; clear on overlay close or phase exit.

**Integrator:** [centralized UI services](../04-dev/centralized-ui-services.md) — presenter/facade pattern, sort stack, bootstrap.

**Not on this strip:** map legend, party cell/facing, status numbers, lore, or save warnings (those stay on HUD labels or modal body / `hud-overlay__hint`).

**Removed per-panel bind footers:** `cmd-input-hint`, `hub-input-hint`, `party-menu-hint`, `tabbed-picker__hint`, `item-list-picker-hint`, `skill-picker-hint`, party equipment detail bind footer, `map-view-hint`, `battle-reward-hint`.

Copy constants: `TabbedPickerRailHints` — full table in [shared menu & picker UI § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints). Exploration minimap uses `ForExplorationMapPanel` / `ForExplorationMapFullscreen` — `[Z] Open` when a chest is in the **facing** cell ahead, `[Z] Gather` when standing on a gather node; refreshes on turn-in-place and after interact.

---

## Hub & menus

**Implemented** in hub phase ([game #98](https://github.com/miramocha/griddungeon-game/issues/98), [ADR 026 hub addendum](../../decisions/026-combat-menu-focus-navigation.md#hub-implemented)). Same **arrows / WASD / `Z` / `X`** pattern as combat; `GamePhase.Hub` only — no grid movement.

| Action | Input |
|--------|--------|
| Navigate | Mouse, arrows, `W`/`A`/`S`/`D` (`Hub.MenuNavigate`) |
| Confirm | `Z` or LMB on focused control |
| Cancel / back | `X` or RMB (`Hub.MenuCancel`; closes service panel; root menu unchanged) |
| Party menu | `Tab` or `Esc` when safe (same toggle as exploration) |
| Assign party / skills | Mouse or keyboard focus at **Explorers Guild** |

Presentation lock blocks navigate/confirm while hub reactive beats run ([hub-and-services](hub-and-services.md#service-ui-motion)).

---

## Action map summary (implementation)

```
Exploration
  MoveForward, MoveBack, StrafeLeft, StrafeRight
  TurnLeft, TurnRight
  Interact, ToggleMap, PartyMenu, Pause

Map
  Pan, Zoom, RecenterParty, CloseFullscreen
  CursorMove, ConfirmDestination, SetDestination, CancelAutopilot, DisengageDestinationPick   # expanded map — C arm/confirm, X disengage, LMB set, Esc cancel/close

Combat
  MenuNavigate, MenuConfirm, MenuCancel   # ADR 026 — arrows + WASD / Z / X / RMB on MenuNavigate composite
  SkillPickerTabPrev, SkillPickerTabNext    # ADR 035 — Q / E at launch; L1 / R1 deferred; only while picker open
  InventoryBagTabPrev, InventoryBagTabNext  # ADR 036 — Q / E on Inventory pane OR member cycle on Equipment pane
  ProtocolMenu, ConfirmProtocol           # legacy names; map to focus confirm when implemented
  CmdAttack, CmdGuard, CmdSkill, CmdItem, CmdFlee   # deprecate direct fire — focus list drives Submit
  CycleTarget                             # deferred; targeting uses MenuNavigate on roster
  ToggleLog, ToggleMap, Pause             # Esc → Pause when UI ships

Hub
  MenuNavigate, MenuConfirm, MenuCancel   # Z / X / RMB; Tab + Esc → PartyMenu
  PartyMenu, InventoryBagTabPrev, InventoryBagTabNext

UI
  Navigate, Submit, Cancel, Point, Click
```

---

## Gamepad-ready keyboard layout (deferred implementation)

**Goal:** PC keyboard defaults should map cleanly to a future gamepad scheme without rebinding every action. **No gamepad control scheme ships yet** — this section is layout policy + audit only.

### Core mapping (locked intent)

| Keyboard slot | Role | Gamepad (Xbox names) | Notes |
|---------------|------|----------------------|-------|
| **`W` / `A` / `S` / `D`** (+ arrows) | Move / navigate / map cursor | **Left stick** or **D-pad** | Arrows = D-pad alias on PC |
| **`Z`** | Confirm / interact (primary) | **A** (south) | Sole confirm key in `GridDungeon.inputactions` |
| **`X`** | Cancel / back | **B** (east) | RMB = `MenuCancel` alias on PC |
| **`C`** | Secondary confirm / context action | **X** (west) | Expanded-map autopilot arm + confirm only |
| **`V`** | Tertiary face action | **Y** (north) | Combat / battle log toggle |
| **`Q` / `E`** | Tab prev/next **or** exploration turn | **L1** / **R1** (shoulder bumpers) | Same keys, phase-gated (`InputRouter`) |

PlayStation / Switch: same **positions** (Cross/Circle/Square/Triangle; B/A/Y/X on Switch) — bind by **action**, not by letter on the plastic.

### Face row semantics

Same physical tier on gamepad; different **roles** on keyboard:

| Face slot | Keyboard | Gamepad (Xbox) | Class | Typical phases |
|-----------|----------|----------------|-------|----------------|
| South | `Z` | **A** | **Verb** — confirm / interact | Global |
| East | `X` | **B** | **Verb** — cancel / back | Menus, map pick cancel |
| West | `C` | **X** | **Verb** — context confirm | Expanded-map autopilot only |
| North | `V` | **Y** | **Overlay** — read-only UI | Combat battle log (not a confirm key) |

### Map toggle — `M`, not `C`

**Locked PC default:** **`M`** toggles side minimap ↔ fullscreen map (exploration + combat read-only) — [ADR 014](../../decisions/014-mvp1-exploration-map.md), Mary Skelter 2 **`[M] TOGGLE MAP DISPLAY`** ([map-ui refs](../refs/map-ui.md)).

| Reference | Map open key | Notes |
|-----------|--------------|-------|
| **Mary Skelter 2** (PC) | **`M`** | HUD copy: toggle map display / expanded overlay |
| **Etrian / DRPG lane** (general) | **`M`** or map menu item | Class of Heroes 3 uses map as dedicated screen; floor pills use other keys |
| **Labyrinth of Galleria** (map screen) | **`C`** / **`V`** | **On the map UI only** — treasure list / legend — not global map toggle |

**Do not move map toggle to `C`.** **`C`** is committed to expanded-map **autopilot** (face-row west / Xbox **X**).

**Gamepad map toggle (locked default):** **`M`** → Xbox **View** (`<Gamepad>/selectButton`); DualSense **touchpad click** (`DualShockGamepad.touchpadButton` — **not** Create / `selectButton`). Not **Menu** (party / pause), not **L3** (MSK2 pad uses stick click — we pass for one global scheme).

### Genre cross-check (FPV DRPG / EO lane)

Compared against [00 — Game references](../00-game-references.md) primary (**Etrian Odyssey**) and secondary (**Mary Skelter**), plus [map-ui refs](../refs/map-ui.md) (Galleria, CoH3, MSK2). Sources: [StrategyWiki EO controls](https://strategywiki.org/wiki/Etrian_Odyssey/Controls), [MSK2 PC controls](https://www.gamenguides.com/mary-skelter-2-pc-keyboard-and-gamepad-controls) (Jan 2022 PC port).

| Action | **Grid Dungeon** | **Etrian Odyssey** (PC / Origins) | **Mary Skelter 2** (PC) | **Verdict** |
|--------|------------------|-----------------------------------|-------------------------|-------------|
| **Move** | `WASD` + arrows | `WASD` | `WASD` + arrows | Aligned |
| **Strafe** | `A` / `D` | `Q` / `E` | `Q` / `E` (sidestep) | **Trial swap** — we strafe on `A`/`D`, turn on `Q`/`E` ([§ Exploration](#exploration)); EO/MSK invert that pair |
| **Turn** | `Q` / `E` | (via `A`/`D` in EO PC table) | `A` / `D` (with move) | Same trial swap; bumpers still map cleanly |
| **Confirm / interact** | **`Z`** | **`Space`** | **`Space` / `Enter`** | **Diverges** from EO/MSK PC — intentional: one key → gamepad **A**; MSK uses **`Z`** for dialog skip only |
| **Cancel / back** | **`X`** | **`R`** | **Backspace / Shift** | **Diverges** from EO **`R`** — our **`X`** matches east-face / Nintendo cancel on keyboard |
| **Menu / pause** | **`Tab` / `Esc`** | **`Tab`** (main menu) | **`Esc`** (system / log history) | Aligned intent → gamepad **Start** |
| **Map toggle** | **`M`** | Map side panel + draw mode (no single **`M`** in EO table) | **`M`** (pad: **L3** in MSK2) | **PC `M` locked**; gamepad **`View`/`Select`** (not L3) |
| **Battle / event log** | **`V`** (combat) | — | **`F`** (pad: **Y**) | Same **north face** tier as MSK log (**Y**); letter differs (**V** vs **F**) |
| **Map screen extras** | **`C`** = autopilot pick | **`C`** = icon list; **`V`** = tool confirm | — | **`C`/`V` on map** common in NIS lane — we use for **autopilot** / **log**, not draw tools ([ADR 002](../../decisions/002-mapping-model.md) no drawing) |
| **Mouse** | Combat target, map pan, hub | Full mouse + draw | Supported | PC-first — matches EO Origins PC pitch |

**Takeaways**

1. **`M` for map** — MSK PC match; gamepad **`View`/`Select`** locked (MSK pad uses **L3** — we standardize on **View** for `ToggleMap`).
2. **`Z` not `Space`** — Western EO/MSK default; we pick **JP-style `Z`/`X` face row** + pad **A**/**B** over EO **`Space`**/**`R`** — document in tutorials / first hub hint if EO migrants complain.
3. **`Q`/`E` turn vs strafe** — Only major movement divergence from EO/MSK; locked as trial layout in [input-bindings § Exploration](#exploration); bumpers (**L1**/**R1**) still work for tab/turn.
4. **`C` for autopilot** — Not a global map key in genre; Galleria **`C`** is **in-map UI** (treasure list). Safe as secondary face action while **`M`** owns toggle.
5. **No `Space`/`Enter` in action maps** — Stricter than EO/MSK; rebind screen (deferred) can restore western defaults without changing gamepad layout.

### System tier

**Intentionally outside the `ZXCV` face row** — center / meta buttons, not confirm/cancel:

| Keyboard | Action(s) | Xbox | PlayStation | Switch |
|----------|-----------|------|-------------|--------|
| **`Tab` / `Esc`** | Party menu, pause, close map, cancel autopilot | **Menu** (Start) | **Options** | **+** |
| **`M`** | Toggle map (exploration + combat) | **View** | **Touchpad click** | **−** (or View equiv.) |
| **Mouse** | Pan, zoom, click targets, hub hover | R stick (deferred) | R stick | R stick |

**PlayStation note:** Unity maps Xbox **View** to `Gamepad.selectButton` (= **Create** on DualSense). Grid Dungeon **map** uses **touchpad click** instead so **Create stays free**. Codex / journal deferred to pause menu — not View.

### PC vs console reference (locked intent)

Policy for a future `Gamepad` control scheme in `GridDungeon.inputactions`. **PC column matches shipped keyboard binds today.**

| Action | PC keyboard | PC mouse | Xbox | PlayStation | Status |
|--------|-------------|----------|------|-------------|--------|
| **Move / navigate** | `WASD`, arrows | — | L stick, D-pad | Same | PC wired |
| **Confirm / interact** | `Z` | LMB (context) | **A** | **Cross** | PC wired |
| **Cancel / back** | `X` | RMB (`MenuCancel`) | **B** | **Circle** | PC wired |
| **Map autopilot** (expanded) | `C` | LMB (set dest.) | **X** (west) | **Square** | PC wired |
| **Battle log** (combat) | `V` | — | **Y** (north) | **Triangle** | PC wired |
| **Tab / turn** | `Q` `E` | Tab chips (LMB) | **L1** **R1** | L1 R1 | PC wired |
| **Party menu** | `Tab` | — | **Menu** | **Options** | PC wired |
| **Pause / overlay stack** | `Esc` | — | **Menu** | **Options** | PC wired |
| **Toggle map** | `M` | — | **View** | **Touchpad click** | PC wired; pad deferred |
| **Map pan** | — | Drag | R stick (deferred) | R stick | Deferred |
| **Map zoom** | — | Wheel | L2/R2 (deferred) | L2/R2 | Deferred |
| **Recenter map** | `Home` / `P` | — | L3 long-press? (deferred) | L3? | Audit only |
| **Combat target** | — | Click cell | Pointer / stick (deferred) | Same | PC wired |

**PC ↔ pad asymmetry (documented):** map letter **`M`** on keyboard; pad uses **View / touchpad**, not west face **`C`**. Confirm **`Z`** only on PC — no **`Space`** / **`Enter`** in gameplay action maps.

### Audit — current `GridDungeon.inputactions` (2026-06)

**In pattern**

| Key | Action map | Action |
|-----|------------|--------|
| WASD + arrows | Exploration, Combat, Hub, Map | Move, `MenuNavigate`, `CursorMove` |
| Z | Exploration, Combat, Hub | `Interact`, `MenuConfirm` |
| X | Combat, Hub, Map | `MenuCancel`, `DisengageDestinationPick` |
| C | Map | `ConfirmDestination`, `ToggleAutopilotSelect` |
| V | Combat | `ToggleLog` |
| Q / E | Exploration, Combat, Hub | Turn (FPV), `*TabPrev` / `*TabNext`, `SkillPickerTab*` |

**Outside pattern — document before adding more**

| Key | Action map | Action | Gamepad note |
|-----|------------|--------|--------------|
| **`M`** | Exploration, Combat | `ToggleMap` | **View** / **Select** — locked (not L3) |
| **`Tab`** | Exploration, Hub, Combat | `PartyMenu`, `CycleTarget` (deferred) | **Start** with **`Esc`** |
| **`Esc`** | Exploration, Hub, Map | `Pause`, `PartyMenu`, `CloseFullscreen`, `CancelAutopilot` | **Start** |
| **`Home` / `P`** | Map | `RecenterParty` | Map utility — stick-click or long-press map |

**Removed from action maps:** **`Space`** / **`Enter`** — use **`Z`** for confirm / interact. (Deferred QTE / cinematic beats may document their own keys when implemented.)

**Dev / editor only (not player binds):** `F1`–`F10` in `GamePhaseDevShortcuts`; Floor Editor `KeyCode` — ignore for gamepad policy.

### Agent / PR checklist (new binds)

1. Prefer **`WASD`**, **`Z`/`X`/`C`/`V`**, or **`Q`/`E`** before other keys.
2. If you must use another key, add a row to the audit table above with proposed gamepad home.
3. Do not add **`Space`** / **`Enter`** to `GridDungeon.inputactions` for gameplay — use **`Z`**.
4. Map toggle stays **`M`** (gamepad **View**) — not **`C`**.

---

## Gamepad (deferred)

Ship PC first. When a `Gamepad` control scheme is added to `GridDungeon.inputactions`, mirror the [PC vs console reference](#pc-vs-console-reference-locked-intent) — one action per role, not one binding per key letter.

**Implementation notes (Unity Input System):**

| Action | Xbox bind | PlayStation bind |
|--------|-----------|------------------|
| `ToggleMap` | `<Gamepad>/selectButton` (View) | `<DualShockGamepad>/touchpadButton` |
| `PartyMenu` / `Pause` | `<Gamepad>/startButton` | Same path (Options) |
| Face row actions | `<Gamepad>/buttonSouth` … `buttonNorth` | Same paths (position-based) |
| `Q`/`E` tier | `<Gamepad>/leftShoulder`, `rightShoulder` | Same |

Mouse pan/zoom stays PC-primary; map zoom may later use triggers. DualSense **Create** (`selectButton`) remains unbound unless a future feature needs the Xbox View slot on Sony pads without touchpad.

**Previously:** “document in separate pass” — layout pass is above; implementation still deferred ([release scope](../00-release-scope.md)).

---

## launch checklist

- [ ] `Exploration` map with defaults above
- [ ] `Combat` map + mouse target raycast
- [ ] `Map` pan/zoom on panel
- [ ] Rebind screen (optional at launch — can ship fixed defaults)

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [02 — Combat](combat.md)
- [02 — Mapping](mapping.md)
- [04 — Tech notes](../04-tech-notes.md)
- [ADR 001 — Grid movement](../../decisions/001-grid-movement.md)
- [ADR 018 — Exploration animation speed](../../decisions/018-exploration-animation-speed.md)
- [ADR 021 — Autopilot MVP2](../../decisions/021-autopilot-mvp2.md)
- [Autopilot (optional)](autopilot.md)
- [ADR 008 — Campaign defaults](../../decisions/008-campaign-defaults.md)
- [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md)
