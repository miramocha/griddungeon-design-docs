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
| **Strafe left** | `A` | Displacement |
| **Strafe right** | `D` | Displacement |
| **Turn left** | `Q` | No step events |
| **Turn right** | `E` | No step events |
| **Interact** | `Space` | Door, chest, stairs, gather |
| **Toggle map** | `M` | Side panel ↔ fullscreen map |
| **Party / menu** | `Tab` | Inventory, formation summary (exploration-safe) |
| **Pause** | `Esc` | Pause menu; confirm quit to hub |

**Arrow keys** duplicate `W/A/S/D` + `Q/E` (accessibility).

**Movement (W/A/S/D and arrow duplicates)** and **turn (Q/E and arrow duplicates)** use **hold** for repeat ([ADR 001](../../decisions/001-grid-movement.md)):

- While an explorer **lerp** is playing (durations per [ADR 018](../../decisions/018-exploration-animation-speed.md) preset; Normal: step ~0.28s, turn ~0.26s): **no** new commit of that action type and **no** buffered input.
- When the lerp **ends**, re-check `IsPressed` on held actions; if a movement key is still held, take **one** displacement (priority over turn); else if a turn key is still held, take **one** 90° turn.
- A tap during lerp only leads to another step/turn if the key is **still held** when the lerp finishes (no mid-lerp queue).
- **Turn** does not fire step events (no FOE tick, no random encounter).

**Settings (deferred):** Exploration animation speed — Slow / Normal / Fast / Very Fast ([ADR 018](../../decisions/018-exploration-animation-speed.md)); stored in player prefs when the settings UI ships.

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

### Protocol (core turn, Synchro 100%)

Only when **Synchro bar = 100%** on a **core** combatant’s turn ([synchro-protocol](synchro-protocol.md)).

| Action | Input | Notes |
|--------|-------|-------|
| **Open Protocol menu** | `U` | Lists Navigator Protocol skills |
| **Select Protocol skill** | `1`–`9` or mouse click | MVP1 dev HUD: `U` strike, `M` mend |
| **Confirm Protocol** | `Enter` | Resolve; bar → 0% |

### AGI turn phase (per actor)

When a **player-controlled** combatant’s turn is active (core or aux; not Navigator).

| Action | Keyboard | Notes |
|--------|----------|-------|
| **Attack** | `1` | Then mouse pick enemy |
| **Guard** | `2` | Self |
| **Skill** | `3` | Sub-menu or skill bar `1`–`8` |
| **Item** | `4` | Sub-menu |
| **Flee** | `5` | Confirm dialog optional |
| **Cycle target** | `Tab` | Next valid target (keyboard-only path) |
| **Confirm action** | `Enter` | Execute after target/skill chosen |
| **Cancel / back** | `Esc` | Clear sub-menu |

| Action | Mouse | Notes |
|--------|-------|-------|
| **Select target** | LMB on enemy/portrait | Valid slots highlighted |
| **Select skill** | LMB on skill icon | |

**Sub-menus:** `1`–`8` pick skill/item slot; `Esc` backs out.

### Combat UI (any time in fight)

| Action | Input | Notes |
|--------|-------|-------|
| **Toggle combat log** | `L` | Expand/collapse |
| **Toggle map** | `M` | Read-only floor map |
| **Pause** | `Esc` | Pause menu: Resume / Settings only — no abandon ([ADR 015](../../decisions/015-mvp1-combat.md)) |

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

Combat
  ProtocolMenu, ProtocolSkill1..9, ConfirmProtocol
  CmdAttack, CmdGuard, CmdSkill, CmdItem, CmdFlee
  CycleTarget, Confirm, Cancel
  QTEPrompt, SkipCinematic
  ToggleLog, ToggleMap, Pause

Map
  Pan, Zoom, RecenterParty

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
- [ADR 008 — Campaign defaults](../../decisions/008-campaign-defaults.md)
