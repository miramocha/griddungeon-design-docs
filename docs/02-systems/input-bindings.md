# Input Bindings (PC)

**Platform:** PC first ([ADR 008](../../decisions/008-campaign-defaults.md)). Keyboard + mouse primary; **gamepad deferred**.

Bindings use **Unity 6** + **Input System** (`com.unity.inputsystem`) action maps: `Exploration`, `Combat`, `UI`, `Map` ([ADR 012](../../decisions/012-unity-6-stack.md)).

## Design principles

- **Exploration:** grid actions on keyboard; no mouse movement in FPV.
- **Combat:** **menu focus** on command bar (+ target list when targeting) — arrows move focus, **`Z`** confirm, **`X`** cancel/Back; **mouse** still one-click queue and LMB targets ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)).
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
| **Interact** | `Space` | Door, chest, stairs, gather |
| **Toggle map** | `M` | Side panel ↔ fullscreen map |
| **Party / menu** | `Tab` | Inventory, formation summary (exploration-safe) |
| **Pause** | `Esc` | Pause menu: **Resume** / **Quit to title** (confirm; **does not save** — inn/hub only). **No** return to hub from pause — use in-dungeon exits ([game phase](game-phase.md#return-to-hub-exploration-only)) |

**Arrow keys** duplicate `W/S` (forward/back) and left/right arrows (turn). Strafe (`A`/`D`) has no arrow duplicate.

**Movement (`W`/`S`/`A`/`D` and forward/back arrows)** and **turn (`Q`/`E` and left/right arrows)** use **hold** for repeat ([ADR 001](../../decisions/001-grid-movement.md)):

- While an explorer **lerp** is playing (durations per [ADR 018](../../decisions/018-exploration-animation-speed.md) preset; Normal: step ~0.28s, turn ~0.26s): **no** new commit of that action type and **no** buffered input.
- When the lerp **ends**, re-check `IsPressed` on held actions; if a movement key is still held, take **one** displacement (priority over turn); else if a turn key is still held, take **one** 90° turn.
- A tap during lerp only leads to another step/turn if the key is **still held** when the lerp finishes (no mid-lerp queue).
- **Turn** does not fire step events (no FOE tick, no random encounter).

**Settings (deferred):** Exploration animation speed — Slow / Normal / Fast / Very Fast ([ADR 018](../../decisions/018-exploration-animation-speed.md)); stored in player prefs when the settings UI ships.

### Autopilot (MVP2)

| Action | Input | Notes |
|--------|-------|-------|
| **Set destination** | `LMB` on revealed walkable map cell | Pathfind + walk ([autopilot](autopilot.md), [ADR 021](../../decisions/021-autopilot-mvp2.md)) |
| **Cancel autopilot** | `Esc`, any move/turn/interact, or `LMB` party cell | Immediate |

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

**Authority:** [ADR 026 — Combat menu focus navigation](../../decisions/026-combat-menu-focus-navigation.md). Global combat UI keys: **arrows** = move focus, **`Z`** = confirm (`Enter` alias), **`X`** = cancel / Back, **`Esc`** = pause (no-op until pause UI ships). **`R`** is not used for Back.

### Command bar (planning + player-controlled turns)

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move focus** | Arrow keys | Active scope: command bar or target list (see targeting) |
| **Confirm** | `Z` or `Enter` | Queue focused command, confirm target, or activate **Back button** |
| **Cancel / Back** | `X` | Cancel targeting, or LIFO undo last queued command when planning |
| **Pause** | `Esc` | Any phase when pause menu ships ([ADR 015](../../decisions/015-mvp1-combat.md)); no-op until then |

| Action | Mouse | Notes |
|--------|-------|-------|
| **Command** | LMB on bar button | **Instant** queue (no extra `Z`) — keyboard cursor unchanged |
| **Back button** | LMB | Same as `X` when enabled |
| **Protocol** | LMB | Instant when visible and ready |

**Command bar items (focus order):** Attack → Guard → Skill → Item → Flee → Protocol (if visible) → **Back button**. Default focus when a core’s planning starts: **Attack**. Skip disabled/hidden entries.

**Planning flow:** One command per living core in **formation order** ([game #58](https://github.com/miramocha/griddungeon-game/issues/58)); auto-advance after each confirm. **No roster keyboard** — use **`X`** / **Back button** to LIFO undo ([game #61](https://github.com/miramocha/griddungeon-game/issues/61)). Roster LMB re-select ([#58](https://github.com/miramocha/griddungeon-game/issues/58) follow-up) optional.

### Protocol (Synchro 100%)

On command bar when **Synchro Charge = 100%** and **unlocked** ([synchro-protocol](synchro-protocol.md)). Confirm with **`Z`** (not a separate `U` one-shot). **`1`–`9` skill picker** deferred ([#35](https://github.com/miramocha/griddungeon-game/issues/35)+).

### Command planning — targeting

After **Attack** or single-target **Skill** ([#60](https://github.com/miramocha/griddungeon-game/issues/60)):

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Move target focus** | Arrow keys | Valid slots only; first valid slot highlighted on enter |
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

### Combat UI (any time in fight)

| Action | Input | Notes |
|--------|-------|-------|
| **Toggle combat log** | `L` | Expand/collapse |
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

## Hub & menus

**Deferred** until hub service UI ships ([#36](https://github.com/miramocha/griddungeon-game/issues/36)). When built, use the same **arrows / `Z` / `X`** pattern as combat ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md) hub addendum).

| Action | Input (target) |
|--------|----------------|
| Navigate | Mouse, arrows |
| Confirm | `Z` (`Enter` alias) |
| Cancel / back | `X` or mouse |
| Assign party / skills | Mouse at **Explorers Guild** (until guild UI ships) |

No grid movement in hub.

---

## Action map summary (implementation)

```
Exploration
  MoveForward, MoveBack, StrafeLeft, StrafeRight
  TurnLeft, TurnRight
  Interact, ToggleMap, PartyMenu, Pause
  MapSetAutopilotDestination, CancelAutopilot   # MVP2 (map LMB + Esc)

Combat
  MenuNavigate, MenuConfirm, MenuCancel   # ADR 026 — arrows / Z / X (wire + remap from legacy Cmd*)
  ProtocolMenu, ConfirmProtocol           # legacy names; map to focus confirm when implemented
  CmdAttack, CmdGuard, CmdSkill, CmdItem, CmdFlee   # deprecate direct fire — focus list drives Submit
  CycleTarget                             # deferred; targeting uses MenuNavigate on roster
  ToggleLog, ToggleMap, Pause             # Esc → Pause when UI ships

Map
  Pan, Zoom, RecenterParty
  SetAutopilotDestination   # MVP2 — LMB on revealed walkable cell

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
