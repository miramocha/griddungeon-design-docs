# Input Bindings (PC)

**Platform:** PC first ([ADR 008](../../decisions/008-campaign-defaults.md)). Keyboard + mouse primary; **gamepad deferred**.

Bindings use **Unity 6** + **Input System** (`com.unity.inputsystem`) action maps: `Exploration`, `Combat`, `UI`, `Map` ([ADR 012](../../decisions/012-unity-6-stack.md)).

## Design principles

- **Exploration:** grid actions on keyboard; no mouse movement in FPV.
- **Combat:** commands on keyboard; **mouse** for target/ally selection.
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

### Protocol (Synchro 100%)

Only when **Synchro Charge = 100%** and **unlocked** (`s1_synchro_unlocked`) ([synchro-protocol](synchro-protocol.md)). Hidden until mid–first-FOE unlock; tutorial phase may **force** Protocol only.

**MVP1 (no skill sub-menu):** one press queues (command planning) or resolves (AGI core turn) — **no** separate confirm step.

| Action | Input | Notes |
|--------|-------|-------|
| **Protocol** | `U` or `Enter` | Dev default: `protocol_strike`; bar spent on resolve during AGI playback |
| **Protocol** (mouse) | Click **Protocol** on command bar | Same as `U` |
| **Pick skill** | `1`–`9` | **Deferred (#35+)** — no Protocol skill list UI in MVP1 |

### Command planning (round start)

After the turn queue is built and **before** AGI playback ([combat § Command planning — back](combat.md#command-planning--back)). Player assigns one command per **living core** in sequence (highlight advances to the next unassigned core after each pick); combat auto-commits when all living cores are queued ([game #58](https://github.com/miramocha/griddungeon-game/issues/58)).

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Attack / Guard / Skill / Item / Flee** | `Z`/`X`/`C`/`V`/`B` | Same as AGI turn; frees `1`–`9` for Protocol / skill sub-menus |
| **Protocol** | `U` or `Enter` | One-shot queue for highlighted core (same as command bar click); not a confirm step |
| **Back** (last queued command) | `R` or `Esc` | Pops the **last** assignment (LIFO); highlight returns to that core; no-op when nothing queued — [game #61](https://github.com/miramocha/griddungeon-game/issues/61) |
| **Back** (mouse) | Click **Back** on command bar | Same as `R` / `Esc` |
| **Select core to plan** | LMB on roster | Re-select another core without stepping back — **not wired** (#58 follow-up); **no** Tab core-cycle during planning |

**Pause vs Back:** Combat `Pause` is reserved for pause menu ([ADR 015](../../decisions/015-mvp1-combat.md)) and is **not** wired in `CombatInputHandler` yet. During **command planning**, `R` and `Esc` map to **Back** only (not pause).

### AGI turn phase (per actor)

When a **player-controlled** combatant’s turn is active (core or aux; not Navigator). **Default flow:** living cores already queued during command planning — this section applies to **summon** control, **targeting** sub-steps, and legacy per-slot mode if [#44](https://github.com/miramocha/griddungeon-game/issues/44) optional confirm is OFF.

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Attack** | `Z` | Then mouse pick enemy |
| **Guard** | `X` | Self |
| **Skill** | `C` | Sub-menu or skill bar `1`–`8` |
| **Item** | `V` | Sub-menu |
| **Flee** | `B` | Confirm dialog optional |
| **Cycle target** | `Tab` | Next valid target (keyboard-only path) |
| **Confirm action** | `Space` | Execute after target/skill chosen (EO-style confirm) |
| **Cancel / back** | `R` or `Esc` | Clear sub-menu |

| Action | Mouse | Notes |
|--------|-------|-------|
| **Select target** | LMB on enemy/portrait | Valid slots highlighted |
| **Select skill** | LMB on skill icon | |

**Sub-menus:** `1`–`8` pick skill/item slot; `Esc` backs out.

**Implementation:** Targeting mode + mouse pick not wired yet — Attack resolves via `PickDefaultTarget` until [game #60](https://github.com/miramocha/griddungeon-game/issues/60). `Tab` / `Enter` confirm paths ship with #60.

### Combat UI (any time in fight)

| Action | Input | Notes |
|--------|-------|-------|
| **Toggle combat log** | `L` | Expand/collapse |
| **Toggle map** | `M` | Read-only floor map |
| **Pause** | `Esc` | **Turn phase / post-planning only** when pause UI ships ([ADR 015](../../decisions/015-mvp1-combat.md)). During **command planning**, `Esc` is **Back**, not pause. |

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

Standard PC UI:

| Action | Input |
|--------|-------|
| Navigate | Mouse, `Up`/`Down`, `Enter` |
| Back | `Esc` or mouse |
| Assign party / skills | Mouse at **Explorers Guild** |
| Assign Navigator | Mouse at **Navigator Office** |

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
  ProtocolMenu, ConfirmProtocol   # MVP1: both fire default Protocol; skill1..9 when picker ships (#35)
  CmdAttack, CmdGuard, CmdSkill, CmdItem, CmdFlee
  CycleTarget, Confirm, Cancel
  QTEPrompt, SkipCinematic
  ToggleLog, ToggleMap, Pause

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
