# Input Bindings (PC)

**Platform:** PC first ([ADR 008](../../decisions/008-campaign-defaults.md)). Keyboard + mouse primary; **gamepad deferred**.

Bindings use **Unity 6** + **Input System** (`com.unity.inputsystem`) action maps: `Exploration`, `Combat`, `UI`, `Map` ([ADR 012](../../decisions/012-unity-6-stack.md)). Runtime routing: `InputRouter` → handlers ([exploration UI](exploration-ui.md#input-routing), [game phase](game-phase.md#input-maps-per-phase)).

## Universal PC UI vocabulary

**Authority:** [ADR 009 § Universal UI vocabulary (2026-06)](../../decisions/009-input-bindings-pc.md#amendment-2026-06--universal-ui-vocabulary). Hub, combat command UI, party menu, and tabbed pickers share one **menu vocabulary**. Phase sections below add detail; when a modal or overlay owns input, this table wins over exploration movement.

| Role | Keyboard | Mouse | Input System (menu surfaces) |
|------|----------|-------|------------------------------|
| **Navigate / focus** | `W`/`A`/`S`/`D` + arrows | Hover + LMB on focusable control | `MenuNavigate` (2D vector) |
| **Confirm** | `Z` (+ `Enter` alias) | LMB on focused or clicked control | `MenuConfirm` |
| **Cancel / back** | `X` | RMB | `MenuCancel` |
| **Tab cycle** | `Q` / `E` | LMB on tab chip | `*TabPrev` / `*TabNext` (scoped per overlay) |
| **Menu / pause** | `Tab` / `Esc` | — | `PartyMenu` / `Pause` (phase-specific) |

**Mouse parity:** UITK `Button` controls activate on **LMB** without an extra `Z`. Keyboard **`Z`** is the **focus-then-confirm** path on the same control. LMB on a combat command or valid target still **instant-queues** (no extra confirm) per [ADR 026](../../decisions/026-combat-menu-focus-navigation.md).

### Overlay ownership

When a **party menu**, **skill/item picker**, **hub service panel**, or other modal owns input:

- Universal vocabulary applies (`MenuNavigate`, `MenuConfirm`, `MenuCancel`, scoped `Q`/`E` tab actions).
- Exploration **turn** (`Q`/`E`) and **movement** (`W`/`A`/`S`/`D`) are **gated** — `InputRouter` enables tab actions only on the active pane and does not emit exploration turn while overlays are open ([party menu § Scope](#party-menu-tab), [skill picker § Scope](#skill-use-picker-modal)).

### Exploration FPV exception

With **no** overlay owning input, labyrinth FPV uses `W`/`A`/`S`/`D` and arrows for **grid displacement** (not menu focus), and **`Q`/`E`** for **90° turn** (not tab cycle). See [Exploration](#exploration) below. Map **autopilot destination pick** reuses universal navigate (`WASD` / arrows = cursor, `Z` / LMB = confirm, `X` = cancel pick).

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
- **Rebindable** in settings menu (MVP1: ship with defaults below; store overrides in player prefs).

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
| **Interact** | `Space` or `Z` | Door, chest, stairs, gather, hub gate, stratum transitions |
| **Toggle map** | `M` | Side panel ↔ fullscreen map |
| **Party / pause menu** | `Tab` or `Esc` | Same overlay when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md), [ADR 036](../../decisions/036-party-inventory-model.md)): **Inventory**, **Equipment**, **Quit to title** (hub + exploration; confirm pane → `RequestQuitToTitle`, no inn save). **Skills** / **Tutorial codex** deferred ([guided-tutorial](guided-tutorial.md#codex), [ADR 029](../../decisions/029-guided-tutorial.md)). Exploration: `Esc` cancels autopilot / exits fullscreen map **first**; when pause shell is open, **Esc closes** the menu (`Exploration.Pause` stays enabled while menu open). Global hint on shell: `Esc Close` ([shared menu § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints)). |

**Arrow keys** duplicate `W/S` (forward/back) and left/right arrows (turn). Strafe (`A`/`D`) has no arrow duplicate.

**Movement (`W`/`S`/`A`/`D` and forward/back arrows)** and **turn (`Q`/`E` and left/right arrows)** use **hold** for repeat ([ADR 001](../../decisions/001-grid-movement.md)):

- While an explorer **lerp** is playing (durations per [ADR 018](../../decisions/018-exploration-animation-speed.md) preset; Normal: step ~0.32s, turn ~0.26s): **no** new commit of that action type and **no** buffered input.
- When the lerp **ends**, re-check `IsPressed` on held actions; if a movement key is still held, take **one** displacement (priority over turn); else if a turn key is still held, take **one** 90° turn.
- A tap during lerp only leads to another step/turn if the key is **still held** when the lerp finishes (no mid-lerp queue).
- **Turn** does not fire step events (no FOE tick, no random encounter).

**Settings (deferred):** Exploration animation speed — Slow / Normal / Fast / Very Fast ([ADR 018](../../decisions/018-exploration-animation-speed.md)); stored in player prefs when the settings UI ships.

### Autopilot (MVP2)

| Action | Input | Notes |
|--------|-------|-------|
| **Arm destination pick** | **Z** on fullscreen map | Enter cursor mode ([autopilot](autopilot.md), [ADR 021](../../decisions/021-autopilot-mvp2.md)) |
| **Confirm destination** | **Z** or click revealed walkable cell | Pathfind + walk; expanded map only (side minimap pick deferred) |
| **Cancel autopilot** | `Esc`, any move/turn/interact, or disengage pick (**X**) | Immediate; `Esc` also closes pause menu when shell open |

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

Map does not capture `W/A/S/D` while fullscreen unless focus explicitly on map-only mode — **default:** fullscreen map still allows movement keys to pass through to exploration (map stays visible). Alternative: movement disabled in fullscreen — **use pass-through** for EO-like flow.

---

## Combat

**Authority:** [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md). Global combat UI keys: **arrows or `W`/`A`/`S`/`D`** = move focus (`W`↑ `S`↓ `A`← `D`→, same as arrows), **`Z`** = confirm (`Enter` alias), **`X`** = cancel / Back, **`Esc`** = pause (no-op until pause UI ships). **`R`** is not used for Back. Exploration `W`/`S`/`A`/`D` do **not** apply while the Combat map is active.

### Command bar (planning + player-controlled turns)

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move focus** | Arrow keys or `W` / `A` / `S` / `D` | Active scope: command bar or target list; WASD mirrors arrows ([ADR 026 amendment](../../decisions/026-combat-menu-focus-navigation.md#amendment-2026-05-23-wasd-menu-navigate)) |
| **Confirm** | `Z` or `Enter` | Queue focused command, confirm target, or activate **Back button** |
| **Cancel / Back** | `X` | Cancel targeting, or LIFO undo last queued command when planning |
| **Pause** | `Esc` | Pause menu (incl. **Tutorial codex** when unlocked — [ADR 029](../../decisions/029-guided-tutorial.md)); no-op until UI ships ([ADR 015](../../decisions/015-mvp1-combat.md)) |

| Action | Mouse | Notes |
|--------|-------|-------|
| **Command** | LMB on bar button | **Instant** queue (no extra `Z`) — keyboard cursor unchanged |
| **Back button** | LMB | Same as `X` when enabled |
| **Protocol** | LMB | Instant when visible and ready |

**Command bar items (focus order):** Attack → Guard → Skill → Item → Flee → Protocol (if visible) → **Back button**. Default focus when a core’s planning starts: **Attack**. Skip disabled/hidden entries.

**Planning flow:** One command per living core in **formation order** ([game #58](https://github.com/miramocha/griddungeon-game/issues/58)); auto-advance after each confirm. **No roster keyboard** — use **`X`** / **Back button** to LIFO undo ([game #61](https://github.com/miramocha/griddungeon-game/issues/61)). Roster LMB re-select ([#58](https://github.com/miramocha/griddungeon-game/issues/58) follow-up) optional.

### Protocol (Synchro 100%)

On command bar when **Synchro Charge = 100%** and **unlocked** ([synchro-protocol](synchro-protocol.md)). Confirm with **`Z`** (not a separate `U` one-shot). **`1`–`9` hotkey skill slots** on the Protocol bar deferred ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+) — not the tabbed **Skill** modal ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](../04-dev/custom-skill-picker-ui.md)).

### Command planning — targeting

After **Attack** or single-target **Skill** ([#60](https://github.com/miramocha/griddungeon-game/issues/60)):

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move target focus** | Arrow keys or `W` / `A` / `S` / `D` | Valid slots only; first valid slot highlighted on enter |
| **Confirm target** | `Z` or `Enter` | Queue command with `TargetId`; advance to next core |
| **Cancel targeting** | `X` or **Back button** (+ `Z` on focused Back) | No command queued; return to command bar (default focus Attack) |

**Path B:** entering targeting **moves focus to the target list**; command bar **`Z`** is ignored until targeting ends.

| Action | Mouse | Notes |
|--------|-------|-------|
| **Pick target** | LMB on valid slot | Instant confirm ([#60](https://github.com/miramocha/griddungeon-game/issues/60), keyboard [#70](https://github.com/miramocha/griddungeon-game/issues/70)) |

### AGI turn phase (default MVP1)

Living cores already queued during planning — **no** per-core command bar on AGI slots. **Summon** and legacy per-slot control use the same **focus + `Z` / `X`** model ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md), [ADR 016](../../decisions/016-summon-control-mvp1.md)).

### Round-end confirm (separate)

Optional **confirm all assignments** before AGI playback — [#44](https://github.com/miramocha/griddungeon-game/issues/44); **not** the same as per-command **`Z`** confirm.

### Skill use picker (modal)

When the **skill use picker** is open ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](../04-dev/custom-skill-picker-ui.md)) — after **Skill** on the command bar (shipped [#138](https://github.com/miramocha/griddungeon-game/issues/138)) or **Use skill** in field UI ([#140](https://github.com/miramocha/griddungeon-game/issues/140) deferred):

| Action | Keyboard (MVP1) | Notes |
|--------|-----------------|-------|
| **Previous tab** | **`Q`** | Cycles visible tabs (wrap); default tab **All** |
| **Next tab** | **`E`** | |
| **Move row focus** | Arrows or `W` / `A` / `S` / `D` | Active tab’s skill list only |
| **Confirm skill** | `Z` or `Enter` | Then combat targeting or field apply |
| **Cancel picker** | `X` | Close modal; no command queued |
| **Pick tab (optional)** | LMB on tab | Same tabs as Q/E cycle |

**Deferred:** gamepad — **`L1`/`R1`** tab cycle and shoulder/d-pad row nav when platform gamepad support ships ([ADR 009](../../decisions/009-input-bindings-pc.md)); not required for picker MVP1.

**Scope:** `InputRouter` enables **`SkillPickerTabPrev` / `SkillPickerTabNext`** only while the picker is open. **`Q`/`E`** must **not** emit exploration turn events during this overlay (combat has no exploration map; field picker runs under pause/party modal with movement already blocked).

### Party menu (`Tab`)

When the **party menu** is open ([ADR 036](../../decisions/036-party-inventory-model.md), [items & inventory](items-and-inventory.md)) — **`Tab`** in hub or exploration when safe ([ADR 034](../../decisions/034-skill-point-allocation-outside-combat.md)):

#### Shell (always while menu open)

| Action | Keyboard (MVP1) | Notes |
|--------|-----------------|-------|
| **Open / close menu** | **`Tab`** | Toggle |
| **Open active pane** | **`Z`** | Shows Inventory or Equipment body (section nav stays visible) |
| **Previous section** | **`W`** or **↑** | **Inventory** ↔ **Equipment** (v1 only); works on shell and when pane is open but **not** engaged |
| **Next section** | **`S`** or **↓** | Pane swaps immediately when section changes (hub service style) |
| **Back** | **`X`** | Hide pane → shell; from shell, closes entire menu |

**Scope:** section navigation uses **`MenuNavigate`** vertical axis — **not** `Q`/`E` at shell level. While a pane is **engaged** (bag rows, worn slots, or equipment sub-picker), **W/S** navigate inside the pane instead of sections.

#### Inventory pane (when section = Inventory)

| Action | Keyboard (MVP1) | Notes |
|--------|-----------------|-------|
| **Previous category tab** | **`Q`** | Cycles **All** / Consumables / Equipment (Materials MVP2); default **All** |
| **Next category tab** | **`E`** | |
| **Move slot focus** | Arrows or `W` / `A` / `S` / `D` | Active category’s bag rows only |
| **Confirm** | `Z` | Use consumable when implemented; **no equip** from bag in v1 |
| **Pick tab (optional)** | LMB on tab | Same tabs as Q/E |

#### Equipment pane (when section = Equipment)

| Action | Keyboard (MVP1) | Notes |
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
| **Toggle combat log** | `L` or click preview row | Opens/closes `combat-log-modal`; **`X`** / Back closes modal before pickers (`CombatPlayerCommandGate.TryBack` order). Global hint: **L or X Close** when open ([shared menu & picker UI § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints)) |
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

Bottom-right overlay chip (`InputHintPresenter`, `sortingOrder` 300) shared across hub, combat, exploration minimap, party menu, and post-battle victory. Hosts publish **input bind copy only** — key/button names and actions (`Z Confirm`, `M Fullscreen`) — via `InputHints.Publish(gameState, text)`; clear on overlay close or phase exit.

**Integrator:** [centralized UI services](../04-dev/centralized-ui-services.md) — presenter/facade pattern, sort stack, bootstrap.

**Not on this strip:** map legend, party cell/facing, status numbers, lore, or save warnings (those stay on HUD labels or modal body / `hud-overlay__hint`).

**Removed per-panel bind footers:** `cmd-input-hint`, `hub-input-hint`, `party-menu-hint`, `tabbed-picker__hint`, `item-list-picker-hint`, `skill-picker-hint`, party equipment detail bind footer, `map-view-hint`, `battle-reward-hint`.

Copy constants: `TabbedPickerRailHints` — full table in [shared menu & picker UI § Global input hints](../04-dev/shared-menu-picker-ui.md#global-input-hints).

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
  MapSetAutopilotDestination, CancelAutopilot   # MVP2 (map LMB + Esc)

Combat
  MenuNavigate, MenuConfirm, MenuCancel   # ADR 026 — arrows + WASD / Z / X / RMB on MenuNavigate composite
  SkillPickerTabPrev, SkillPickerTabNext    # ADR 035 — Q / E (MVP1); L1 / R1 deferred; only while picker open
  InventoryBagTabPrev, InventoryBagTabNext  # ADR 036 — Q / E on Inventory pane OR member cycle on Equipment pane
  ProtocolMenu, ConfirmProtocol           # legacy names; map to focus confirm when implemented
  CmdAttack, CmdGuard, CmdSkill, CmdItem, CmdFlee   # deprecate direct fire — focus list drives Submit
  CycleTarget                             # deferred; targeting uses MenuNavigate on roster
  ToggleLog, ToggleMap, Pause             # Esc → Pause when UI ships

Map
  Pan, Zoom, RecenterParty
  SetAutopilotDestination   # MVP2 — LMB on revealed walkable cell

Hub
  MenuNavigate, MenuConfirm, MenuCancel   # Z / X / RMB; Tab + Esc → PartyMenu
  PartyMenu, InventoryBagTabPrev, InventoryBagTabNext

UI
  Navigate, Submit, Cancel, Point, Click
```

---

## Gamepad (deferred)

Ship PC first. Later: left stick = forward/back strafe optional; right stick disabled in FPV; face buttons for interact/confirm. Document in separate pass when controller map is scoped.

---

## MVP1 checklist

- [ ] `Exploration` map with defaults above
- [ ] `Combat` map + mouse target raycast
- [ ] `Map` pan/zoom on panel
- [ ] Rebind screen (optional MVP1 — can ship fixed defaults)

## Related docs

- [02 — Dungeon navigation](../02-dungeon-navigation.md)
- [02 — Combat](combat.md)
- [02 — Mapping](mapping.md)
- [04 — Tech notes](../04-tech-notes.md)
- [ADR 001 — Grid movement](../../decisions/001-grid-movement.md)
- [ADR 018 — Exploration animation speed](../../decisions/018-exploration-animation-speed.md)
- [ADR 021 — Autopilot MVP2](../../decisions/021-autopilot-mvp2.md)
- [Autopilot (MVP2)](autopilot.md)
- [ADR 008 — Campaign defaults](../../decisions/008-campaign-defaults.md)
- [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md)
