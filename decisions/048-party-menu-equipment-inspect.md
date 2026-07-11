---
tags:
  - path/decisions
  - type/adr
  - scope/required
  - domain/ui
  - domain/hub
---
# ADR 048 — Party menu equipment slot inspect (pose + bone camera)

**Status:** Accepted  
**Date:** 2026-07-09  
**Related:** [ADR 047](047-party-menu-3d-stage.md) (party menu 3D stage), [custom party UI § Equipment menu](../docs/04-dev/custom-party-ui.md#equipment-menu-party-pause)

## Context

Equipment pane lets player engage worn slots (weapon/head/body/legs/accessory) on `CharacterDetailView`. ADR 047 ships member orbit on the hex stage when the party floater is docked, but worn-slot focus was UI-only — no pose change, no floater retract, no per-slot camera framing.

## Decision

### Trigger

| Rule | Choice |
|------|--------|
| **When** | Player presses **Z** to engage worn slots on Equipment (`CharacterDetailView.IsSlotsEngaged`) |
| **Member** | Focused core on party floater must already be selected (WASD on floater before engage) |
| **Exit** | **X** disengage slots → floater re-docks, grid idle pose, head Look At orbit |

### Floater

While worn slots engaged: **retract** party floater (`ApplyPartyMenuFloaterDock(false)`) but **keep pinned member grid index** for stage session (do not `ClearMemberFocus` on coordinator).

### Pose (v1)

| Piece | Choice |
|-------|--------|
| **Clips** | `PartyMenuEquip_OHSword_Idle01`, `PartyMenuEquip_HeavySword_Idle01` under `Assets/Art/Characters/PartyMenu/Equipment/` |
| **Catalog** | `PartyMenuEquipPoseCatalog` SO — both clips authored |
| **Runtime v1** | **Always** OH sword idle for all five worn slots |
| **Future** | Map `EquipmentDefinition.WeaponType` (heavy/greatsword → HeavySword, sword → OHSword); TODO in catalog resolver |

Same `AnimatorOverrideController` path as grid idle (`PartyCharacterVisualPose.ApplyEquipInspect`). **Equip layer blend** (~2s `InOutBack`, weight-scaled) owned by `PartyMenuCharacterAnimatorOverrideHost` on each spawned visual — do not snap layer weight while an active blend tween runs.

### Focus motion (orbit + equip inspect)

| Piece | Choice |
|-------|--------|
| **Member root Z** | `PartyMenuEquipInspectMotion` slides focused visual root to formation center (`PartyMenuStageFormationLayout.FocusCharacterLocalZ`) on orbit focus and equip inspect |
| **Enter nudge** | Short scale punch on focus enter (`RootNudgeDurationSeconds` ~0.45s, `OutBack`) |
| **Equip blend timing** | `EquipInspectMotionDurationSeconds` = **2s** baseline for root-Z slide and orbit pivot motion (separate from Cinemachine brain blend) |
| **Defer** | Root-Z sync waits until equip pose applies successfully — avoids centering before idle clip binds |

### Equip picker floater (slot confirm)

| Rule | Choice |
|------|--------|
| **When** | **Z** on an engaged worn slot (`CharacterDetailView` slot focus) |
| **UI** | `PartyEquipmentPickerFloater` centralized service — sort **256**, bone-projected via `UiWorldOverlayAnchor` |
| **Not** | Party bag modal (`ItemListInventory`) — filtered rows for slot + class only |
| **Exit** | **X** closes picker; worn-slot engage stays active |

### Camera

Reuse **`CM_FormationOrbit`** — no third vcam for v1.

| Piece | Choice |
|-------|--------|
| **Look At** | Bone child transforms via `PartyMenuBoneLookTarget` per worn slot |
| **Bones** | Weapon → `RightLowerArm`; Head → `Head`; Body → `Spine` (fallback `Chest`); Legs → `LeftLowerLeg`; Accessory → `LeftHand` |
| **Framing** | `PartyMenuEquipInspectLayout` per-slot Z deltas + yaw flank offsets on orbit pivot; `PartyMenuStageOrbitRig.FocusEquipSlot` tweens yaw + height + Z |
| **VRM LookAt** | Off on inspected member while equip pose plays |
| **Session** | `PartyMenuStagePresenter` `m_equipInspectActive` keeps orbit when floater undocked |

### Authority

| Layer | Owner |
|-------|--------|
| Slot engage / W/S | `PartyEquipmentToolkitView`, `CharacterDetailView` |
| Equip picker floater | `PartyEquipmentPickerFloaterPresenter`, `PartyEquipmentPickerFloater` |
| Floater retract + stage sync | `PartyMenuOverlayView.SyncPartyMenuStageMemberFocus` |
| Equip inspect session | `PartyMenuStagePresenter` / `PartyMenuStage` facade |
| Pose + bone targets | `PartyCharacterVisualRegistry`, `PartyMenuEquipPoseCatalog`, `PartyCharacterVisualPose` |
| Animator override + equip blend | `PartyMenuCharacterAnimatorOverrideHost` |
| Root Z / scale motion | `PartyMenuEquipInspectMotion` |
| Player-build content bootstrap | `PartyMenuRuntimeContent` (`Resources/PartyMenu/PartyMenuRuntimeContent`) |
| Orbit tween | `PartyMenuStageOrbitRig` |

### Content paths

| Asset | Path |
|-------|------|
| Equip idle clips | `Assets/Art/Characters/PartyMenu/Equipment/PartyMenuEquip_*_Idle01.anim` |
| Equip catalog | `Assets/Content/PartyMenu/PartyMenuEquipPoseCatalog.asset` |
| Player-build bootstrap | `Assets/Resources/PartyMenu/PartyMenuRuntimeContent.asset` |
| Editor menu | `GridDungeon → Party Menu → Ensure Idle Clips + Pose Catalog` |

## Consequences

- Equipment inspect decouples floater dock from stage orbit (ADR 047 table updated in custom-party-ui).
- HeavySword clip is cataloged but unused until WeaponType content lands.
- Playtest may tune `PartyMenuEquipInspectLayout` Z deltas and yaw flank offsets per slot.

### Equip inspect camera tuning (v1)

| Slot | Z delta (closer) | Yaw flank |
|------|------------------|-----------|
| Head | `0.85` | left (`+55°`) |
| Body | `0.55` | right (`-55°`) |
| Legs | `0.5` | left (`+55°`) |
| Weapon / Accessory | unchanged | front (`0°`) |

## Out of scope (v1)

- Per-slot unique poses (non-weapon)
- WeaponType-driven clip selection
- Dedicated `CM_EquipInspect` vcam

## Related

- [Custom party UI — Equipment menu](../docs/04-dev/custom-party-ui.md#equipment-menu-party-pause)
- [ADR 047 — Party menu 3D stage](047-party-menu-3d-stage.md)
