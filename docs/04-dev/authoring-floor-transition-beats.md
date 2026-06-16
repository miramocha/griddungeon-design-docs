# Authoring floor transition beats (stairs vignette)

**Scope:** 3D **transition prefabs** played when the party changes exploration floor via stairs or hub stratum entry — **not** dungeon grid markers (`^` / `v` on `ExplorationFloor`). For layout stairs, see [Floor Editor](../02-systems/floor-editor.md) and [dungeons & encounters](../03-content/dungeons-and-encounters.md#map-legend-ascii-blockouts).

**Runtime spec:** [floor transition](../02-systems/floor-transition.md) · [ADR 032](../../decisions/032-floor-transition-vignette-mvp1.md)  
**Game repo paths:** `Assets/Scenes/Transitions/` · [Transitions/README](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scenes/Transitions/README.md)

---

## What you are authoring

Shipped default beat: **`stairs_default`** — black void, a threshold door prop, and two **Cinemachine 3** cameras. `FloorTransitionPresenter` instantiates the prefab during floor changes; `FloorTransitionCatalog` maps **beat id** (and optional floor keys) → prefab + safety timeout.

| Beat id | Typical trigger | Prefab |
|---------|-----------------|--------|
| `stairs_default` | B1F↔B2F↔B3F stairs (`TryChangeFloor`) | `stairs_default.prefab` |
| `hub_enter_stratum` | Hub → Enter Stratum 1 (`BeginHubEnterTransition`) | Same prefab (catalog row) |
| `hub_return_from_exploration` | B1F gate `^` → hub | Same prefab (optional row) |

Unique beats per floor pair can be added later; override with catalog `leaveFloorKey` / `enterFloorKey` when needed.

---

## Quick start (Unity, game repo)

1. Open **`griddungeon-game`** in Unity 6.
2. **GridDungeon → Floor Transition → Create Stairs Default Beat Prefab**  
   → `Assets/Scenes/Transitions/Prefabs/stairs_default.prefab` (+ materials under `Materials/`).
3. **GridDungeon → Floor Transition → Sync Default Beats (Catalog)**  
   → wires prefab on `Assets/Content/FloorTransition/FloorTransitionCatalog.asset`.
4. **GridDungeon → Scenes → Create Dev Bootstrap** if `FloorTransitionPresenter` or **`ScreenFade`** child refs are stale.
5. Play Mode: **F2** exploration → use stairs (**Interact** `Space` / `Z` on `^` or `v` cell).

Batch / CI (Editor closed):  
`FloorTransitionBeatPrefabCreator.CreateStairsDefaultBeatPrefabBatch` then save assets.

---

## Folder layout

```mermaid
flowchart TB
  root["Assets/Scenes/Transitions/"]
  root --> readme[README.md]
  root --> mats[Materials/]
  mats --> voidMat[TransitionVoid.mat]
  mats --> doorMat[TransitionDoor.mat]
  root --> prefabs[Prefabs/]
  prefabs --> stairs[stairs_default.prefab]
```

**Catalog (not under Transitions/):** `Assets/Content/FloorTransition/FloorTransitionCatalog.asset`

Transition prefabs are **referenced by the catalog**; they do **not** need a row in **Build Settings** (unlike FPV floor scenes — [floor art FPV](../02-systems/floor-art-fpv.md)).

---

## Prefab contract

Root GameObject must have **`FloorTransitionBeat`** (`GridDungeon.Runtime.Exploration.FloorTransition`).

```mermaid
flowchart TB
  root["stairs_default<br/>FloorTransitionBeat root"]
  root --> env["Environment/"]
  env --> backdrop[BlackBackdrop]
  env --> light["KeyLight optional"]
  root --> props[Props/]
  props --> door[ThresholdDoor]
  root --> cams[Cameras/]
  cams --> wide["CM_Wide CinemachineCamera"]
  cams --> thresh["CM_Threshold CinemachineCamera"]
```

| Rule | Why |
|------|-----|
| Prefab authored at origin | Presenter spawns at **`y = -100`** by default (`m_beatSpawnWorldY`) so beat + transition vcams stay under the exploration dungeon plane (`y = 0`) |
| **No colliders** on backdrop / door primitives | Beat is presentation-only |
| **Two+ `CinemachineCamera`** under root | Presenter sets priority **100+** on all child vcams |
| Look target = door / threshold | Wide + close shots share one `TrackingTarget` |
| Optional `PlayableDirector` + Timeline | Drive door motion and call signals (below) |

The menu **Create Stairs Default Beat Prefab** builds this hierarchy with placeholder cubes; swap meshes/materials on the prefab instance or variant.

---

## `FloorTransitionBeat` signals

Component on the prefab root:

| Field / API | Role |
|-------------|------|
| **`FloorTransitionBeatTimelineEnd`** | Optional sibling component — director `stopped` → `NotifyBeatEnd()` (see below) |
| **`m_autoScheduleSignals`** | Timer fallback on `FloorTransitionBeat` when no Timeline drives beat end |
| **`m_thresholdSeconds`** | Auto mid-beat `NotifyThreshold()` (default **1.5** s) when auto schedule runs |
| **`m_beatEndSeconds`** | Auto `NotifyBeatEnd()` only when **no** Timeline drives beat end (default **3** s) |
| **`NotifyThreshold()`** | Timeline Signal / animation event / auto timer |
| **`NotifyBeatEnd()`** | **Ends the door vignette** — presenter waits for this before second fade |

**Presenter timing (locked in code):** floor **commit + map load** run **after** `BeatEndFired` (or catalog `DurationMaxSeconds` timeout), **not** on `NotifyThreshold`.

### Timeline drives beat end (recommended)

Uses optional **`FloorTransitionBeatTimelineEnd`** so timer-only beats (`stairs_default` without Timeline) stay unchanged.

1. Add **`PlayableDirector`** on the beat root (or child) and assign a **Timeline** asset.
2. Add **`FloorTransitionBeatTimelineEnd`** on the same root as **`FloorTransitionBeat`** (references auto-fill from the hierarchy).
3. On Timeline end, **`PlayableDirector.stopped`** → **`NotifyBeatEnd()`**. No end-of-track Signal required.
4. **Auto schedule:** `FloorTransitionBeat` skips the beat-end timer when the timeline helper is active; optional **`m_thresholdSeconds`** still runs if **Auto Schedule Signals** is on. Turn auto off if threshold also comes from Timeline Signals.
5. Set catalog **`DurationMaxSeconds`** ≥ Timeline length (safety timeout if `stopped` never fires).
6. If **Play On Awake** is off, enable **Play On Start If Not Awake** on the timeline helper (default on).

You can still place a Timeline **Signal** calling `NotifyBeatEnd()` (redundant with `stopped`, harmless).

### Timer-only (placeholder prefab)

No Timeline asset → **Auto Schedule Signals** runs threshold + beat end from `m_thresholdSeconds` / `m_beatEndSeconds` (menu-generated `stairs_default` path).

**Catalog `DurationMaxSeconds`** must be ≥ real beat length (Sync menu uses **3.5** s for stairs / hub enter). If the beat never fires `BeatEndFired`, the presenter logs a warning and continues at the safety limit.

---

## Cinemachine

| Requirement | Detail |
|-------------|--------|
| Package | `com.unity.cinemachine` **3.x** (game manifest) |
| Session brain | **One** `CinemachineBrain` on main camera — **Create Dev Bootstrap** / `DevSceneComposition` |
| Beat cameras | `CinemachineCamera` children; presenter raises **Priority** to **100+** while beat lives |
| Exploration FPV | `ExplorationCameraRig` **disabled** during beat; re-attached at spawn **under black**, then final unfade |
| Brain lock | `ExplorationCameraSession.SetTransitionBrainLock` — brain stays on for whole beat |
| Party pose hide | `m_partyPoseRoot` or auto from `ExplorationCameraRig.PartyPose`; hides **PartyVisual** child when present |

Authoring tips:

- Start from generated **CM_Wide** / **CM_Threshold** positions; adjust FOV and local position on the prefab.
- For a single active shot, disable the unused vcam or blend via Timeline later.
- Do not add a second `CinemachineBrain` on the beat prefab.

---

## Catalog rows

Open **`FloorTransitionCatalog`** in the Inspector or rely on **Sync Default Beats (Catalog)**.

| Field | Meaning |
|-------|---------|
| **Beat Id** | `stairs_default`, `hub_enter_stratum`, `hub_return_from_exploration` ([`FloorTransitionBeatIds`](https://github.com/miramocha/griddungeon-game/blob/main/Assets/Scripts/Core/Exploration/FloorTransitionBeatIds.cs)) |
| **Leave Floor Key** | e.g. `s1_B1F` — empty = wildcard |
| **Enter Floor Key** | e.g. `s1_B2F` or `hub` — empty = wildcard |
| **Beat Prefab** | Root with `FloorTransitionBeat` |
| **Duration Max Seconds** | Safety timeout for `WaitForBeatEnd` |

Resolve order: most specific `(beatId, leave, enter)` wins; see `FloorTransitionCatalogResolve` tests in game repo.

**Fallback:** null prefab → fade-only transition (same commit/load sequence, no 3D beat).

---

## What the player sees (`stairs_default`)

Sequence implemented in `FloorTransitionPresenter` (vignette path):

```mermaid
sequenceDiagram
    participant P as FloorTransitionPresenter
    participant F as ScreenFade
    participant B as Beat prefab

    Note over P,F: Transition start, fade to black or snap opaque
    P->>P: Unload prior floor art under black
    P->>B: Spawn beat at y=-100
    Note over B: CM brain lock on
    P->>F: Fade from black, door visible
    B-->>P: BeatEndFired
    P->>F: Fade to black
    P->>B: Destroy beat
    Note over P: Brain lock off
    P->>P: Commit map and foes
    Note over P: Hub spawns party in commit delegate
    P->>P: Load destination floor art under black
    P->>P: Attach ExplorationCameraRig at spawn FPV
    P->>F: Fade in to exploration
```

**Hub enter (`hub_enter_stratum`):** `LeaveFloorKey` is empty — no extra fade-to at vignette start (already black). Party must be at entry cell **before** the final fade-in (`CommitHubEnterFloorSession`); `CompleteExplorationEnter` does **not** re-spawn from Hub.

Input and exploration HUD are suppressed for the whole transition (`ExplorationPresentationGate`).

---

## Authoring a new beat variant

1. **Duplicate** `stairs_default.prefab` → e.g. `stairs_b2_hatch.prefab`.
2. Edit props/cameras/Timeline on the duplicate; keep root **`FloorTransitionBeat`**.
3. Tune **`m_beatEndSeconds`** or Timeline so `NotifyBeatEnd()` matches the clip end.
4. Add or edit a row on **`FloorTransitionCatalog`**:
   - Set **Beat Id** (new constant in `FloorTransitionBeatIds` if code references it), or reuse `stairs_default` with specific **Leave** / **Enter** keys.
   - Assign **Beat Prefab** and **Duration Max Seconds**.
5. If a new beat id is used from C#, update `ExplorationPhaseController` / hub paths to pass that `beatId` on `FloorTransitionRequest` (today stairs use `FloorTransitionBeatIds.StairsDefault` only).
6. Manual QA (below).

Later: per-pair rows such as `leave=s1_B1F`, `enter=s1_B2F` without code changes, as long as the request still resolves the row (may require passing `beatId` + keys from caller).

---

## Screen fade (UITK)

Floor transitions use **`ScreenFadePresenter`** on a child **`ScreenFade`** under `Game` (UI Toolkit full-screen `backgroundColor`, sort order **10000**). Wired on `GameState` by Dev Bootstrap.

| Behavior | Detail |
|----------|--------|
| Alpha | `FadeTo` / `FadeFrom` lerp from **current** overlay alpha — no flash when already opaque |
| Stairs leave floor | `AcquireHudSuppress` (map panel fade out) then **`yield return FadeToColor()`** — not `SnapFadeOpaque` on the same frame (screen snap hides map tween). First-floor / no leave key still snaps opaque. |
| Vignette beat | After routine start fade, vignette path fades **from** black for door beat — **no** second fade-to before door when already black |
| Final reveal | FPV attached while opaque; **`ReleaseExplorationChromeForReveal`** (minimap may slide in) then **`FadeFromColor`** — see [gotchas § Map chrome vs floor transition](centralized-ui-gotchas.md#map-chrome-vs-floor-transition-screen-fade-explorationmapcoordinator) |
| Exploration HUD | `ExplorationPresentationGate.AcquireHudSuppress` during transition; `MapView` hides via `FadeTransition` + `map-view--faded` |

If fades do not appear, re-run **Create Dev Bootstrap** so `PanelSettings` and `ScreenFadePresenter` refs are assigned. Do not stack uGUI `Image` fades on the same HUD.

---

## Manual QA

| Step | Action | Expected |
|------|--------|----------|
| 1 | F2 B1F, walk to `v`, Interact | Fade → door vignette → fade → B2F FPV; no movement during beat |
| 2 | B2F↔B3F and reverse | Same default beat; spawn on paired stair cell |
| 3 | Hub → Enter Stratum | `hub_enter_stratum` row or same prefab |
| 4 | B1F gate `^` → hub | Transition or fade; phase → Hub |
| 5 | Spam Interact on stairs mid-beat | Second request ignored; no duplicate floor art |
| 6 | Clear **Beat Prefab** on catalog row | Fade-only still changes floor |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Black screen, no door | Beat prefab null / missing from catalog | Create prefab + **Sync Default Beats** |
| Door flashes, level never loads | `BeatEnd` never fires and `DurationMaxSeconds` too low | Raise **Duration Max**; fix Timeline / auto schedule |
| Stuck on door, old floor | Commit failed; check Console | Campaign gates (B1F `v` needs Act 3); save errors |
| Fade invisible | `ScreenFade` unwired | **Create Dev Bootstrap** |
| Door flashes during fade | Fade lerped from α0 while already black | Fixed in `ScreenFadePresenter` — update game repo if regressed |
| Camera snaps to spawn mid-fade | Party placed after fade-in | Hub: spawn in commit; rig attach before `FadeFromColor` on reveal |
| Party mesh visible during beat | `m_partyPoseRoot` unset | **Create Dev Bootstrap** or ensure `ExplorationCameraRig` on `PartyPose` (runtime resolves pose) |
| Door visible but FPV wrong | Art load after commit | Check `FloorArtCatalog` entry for `enterFloorKey` |
| No Cinemachine motion | Brain disabled mid-beat | Check transition brain lock; no `AfterSceneLoad` brain disable during vignette |
| No Cinemachine motion | Brain missing on main cam | Dev Bootstrap → `EnsureCinemachineBrain` |

---

## Related

- [Floor transition (system)](../02-systems/floor-transition.md)
- [Floor art FPV — transitions](../02-systems/floor-art-fpv.md#floor-transitions)
- [Hub and services](../02-systems/hub-and-services.md)
- Game epic [#114](https://github.com/miramocha/griddungeon-game/issues/114) · prefab [#116](https://github.com/miramocha/griddungeon-game/issues/116)
