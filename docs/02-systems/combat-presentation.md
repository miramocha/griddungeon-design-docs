# Combat Presentation (Spells & Skills)

How skills look and feel in battle — camera, animation, VFX, and **cinematic participation**. Combat runs on the **battle arena** (backdrop + enemy slots), not in dungeon FPV — see [combat scene](combat-scene.md) ([ADR 013](../../decisions/013-combat-scene-rendering.md)).

## Default: fixed camera

**Most spells and skills** use the standard **fixed battle camera**:

- **Three-quarter** fixed angle for the encounter (MVP1 — [ADR 015](../../decisions/015-mvp1-combat.md)).
- Camera **does not** cut, orbit, or change angle per cast.
- Optional **slight zoom** toward the primary enemy target on hit — subtle punch-in via **DOTween**, then ease back to default framing before the next action.
- No dramatic camera moves; zoom is short and repeatable (tuned per skill or global default).
- Feedback = character portrait flash, slot VFX, screen shake (light), combat log, numeric popups.
- Fast to resolve; keeps AGI pacing readable.

Applies to: basic attacks, common elemental spells, heals, buffs, most enemy skills.

---

## Exception: cinematic skills

**Some spells** use **dynamic animation and camera** — boss attacks, ultimates, key Protocol moments, rare party skills.

Cinematics are **sparse** (a few per stratum) so they stay special. Two profiles:

| Profile | Player role | Use when |
|---------|-------------|----------|
| **`Cinematic`** | Watch (optional skip) | Story beats, enemy telegraphs, first-time spectacle |
| **`CinematicQTE`** | **Button prompts** during sequence | Party ultimates, climax boss skills, high-impact Protocol |

**Design intent for QTE:** Make cinematics **meaningful**, not a passive cutscene. Input is **bonus**, not gate — the skill **always resolves** at base power; prompts reward timing with extra damage, crit chance, or a small rider effect (extra hit, buff tick, Synchro charge bump).

### QTE flow

```
Confirm skill → CinematicQTE starts (camera + Timeline)
  → Prompt 1..N appears on beat markers
  → Player hits prompt in window (or misses)
  → Sequence ends → compute QTE tier → apply skill at base + bonus
  → Restore UI / AGI queue
```

| Result | Rule |
|--------|------|
| **All prompts hit** | **Perfect** — max bonus (e.g. +25% damage or guaranteed crit on primary hit) |
| **Most hit** | **Good** — medium bonus |
| **Few / none** | **Base** — skill still fires at normal numbers; log “QTE missed” optional, no whiff |
| **Skip** | Base resolution immediately (see skip rules) |

**Rejected:** Failing QTE cancels the skill or wastes the turn — too punishing in AGI combat.

### Prompt types (MVP2+)

| Type | Input | Example |
|------|--------|---------|
| **Single press** | Shown key (`Space`, `1`–`5`) | One flash at climax frame |
| **Rhythm chain** | 2–4 presses on beats | Party ultimate wind-up |
| **Hold** | Hold `Space` until bar fills | Charge-style finisher (max 1.5s) |
| **Mouse confirm** | LMB on glowing target | Rare — strike weak point on boss model |

Prompts reuse [combat input](input-bindings.md#cinematic-qte) keys where possible; display icon matches binding.

### Enemy vs party

| Caster | QTE? | Skip? |
|--------|------|-------|
| **Party / Protocol** | Optional per skill (`CinematicQTE`) | Yes — `Esc` or `Space` hold after first clear |
| **Enemy / boss** | **No** player QTE (watch telegraph) | Yes — always skippable to base damage resolution |

Player reacts to **their** big moments; enemy cinematics are **readable warnings**, not reflex tests.

### Duration & pacing

- Target **3–8 seconds** per cinematic (QTE adds at most ~2s of active prompts).
- **Block** further commands until cinematic completes or is skipped.
- **One cinematic** at a time globally.
- AGI clock pauses during cinematic (turn does not “consume” extra rounds).

### Skip & accessibility

| Setting | Behavior |
|---------|----------|
| **First play** | Full cinematic + QTE prompts shown |
| **Repeat play** | Auto **skippable** after 0.5s (`Esc` / `Space`) |
| **Accessibility: Auto QTE** | Treat all prompts as Good tier (no input required) |
| **Accessibility: Skip all cinematics** | Jump to base resolution instantly |

Combat log always records **mechanical outcome** (damage, status) even if visuals skipped.

---

## Authoring (data-driven)

Each skill references a **presentation profile**. **Timing** for cinematics is authored on the Timeline ([ADR 027](../../decisions/027-combat-cinematic-timeline-events.md)); skill data holds **profile + asset id + QTE bonus numbers** only.

| Profile | Camera | Animation | QTE | MVP1 |
|---------|--------|-----------|-----|------|
| `Fixed` (default) | Same angle; optional target zoom | Simple cast + VFX | — | All skills |
| `Cinematic` | Scripted | Timeline / clip | None | Stub only |
| `CinematicQTE` | Scripted | Timeline + **markers** | 1–N prompts on Timeline | **MVP2** (1–2 skills) |

**Skill / SO fields (Unity content):**

| Field | `Fixed` | `Cinematic` | `CinematicQTE` |
|-------|---------|-------------|----------------|
| `presentation` | `Fixed` | `Cinematic` | `CinematicQTE` |
| `cinematicAssetId` | — | prefab / Timeline ref | same |
| `vfxPrefab` / `zoomToTarget` | optional | — | — |
| `qteBonus` (perfect / good / base) | — | — | multipliers only — **not** prompt times |

**Timeline prefab (`SkillCinematicPrefab`):**

- `PlayableDirector` → skill Timeline; length = `director.duration` (no duplicate seconds on `SkillDefinition`).
- Marker track **`Cinematic Beats`**: `CinematicQteOpenMarker` / `CinematicQteCloseMarker` at authored frames ([ADR 027 §4](../../decisions/027-combat-cinematic-timeline-events.md#4-mid-cinematic-beats--markers-vs-signals)).
- End of clip → `PlayableDirector.stopped` → apply rules + resume queue.

**Deprecated:** doc-only `qte_prompts[].at_sec` lists — do not ship in MVP2+ content; re-time prompts by moving markers in the Timeline editor.

---

## Combat flow integration

1. Player confirms skill + targets.
2. **`Fixed`** → VFX + optional zoom → apply on hit frame → restore camera.
3. **`Cinematic`** → `CinematicSkillPlayer` plays clip → on end → apply rules → resume queue.
4. **`CinematicQTE`** → play clip → `QTEController` listens for prompts → score tier → apply base skill + `qte_bonus` → resume queue.

**Damage application:** Single resolve at end (after QTE tier known). Do not apply partial damage mid-cinematic unless a skill explicitly tags `multi_hit_cinematic` (boss only, rare).

---

## UI during cinematic

| Element | Behavior |
|---------|----------|
| **Prompt HUD** | Large key icon + shrinking timing ring (center or lower-third) |
| **Tier flash** | Brief “Perfect!” / “Good!” on last prompt (party QTE only) |
| **Turn strip** | Dimmed, not hidden — player still sees order |
| **Skip hint** | `Esc — Skip` after repeat or 0.5s delay |

Fixed presentation must not obscure turn order or row HP. Full-screen VFX allowed briefly for `CinematicQTE` climax frame only.

### VFX anchor targets (`EnemySlot` rig)

`Fixed` and cinematic clips spawn hit VFX at **arena slot transforms**, not world grid cells. Indices match [combat scene § Enemy slots](combat-scene.md#enemy-slots) and [combat § Enemy roster UI](combat.md#enemy-roster-ui-formation-rows):

| Slot index | Tactical row | Transform name (convention) |
|------------|--------------|-----------------------------|
| `0`–`2` | Front | `EnemySlot_0` … `EnemySlot_2` |
| `3`–`5` | Back | `EnemySlot_3` … `EnemySlot_5` |

- **Primary target zoom** (`BattleCameraRig.NudgeZoomToTarget`) uses the **occupied** anchor for `Combatant.SlotIndex`.
- **Empty anchors** stay disabled/hidden — no VFX parent on vacant rig points.
- **Row collapse (Phase C):** when survivors shift index, presenters **re-parent** sprites and refresh UI on the new slot — VFX always follows current `SlotIndex`, not a fixed screen position.

---

## Tech sketch (Unity 6)

- `BattleCameraRig` — default pose; `NudgeZoomToTarget` for `Fixed`
- `SkillDefinition.presentation` → `Fixed | Cinematic | CinematicQTE`; `cinematicAssetId` when not `Fixed`
- `CinematicSkillPlayer` — `PlayableDirector.Play()` / `stopped`; `INotificationReceiver` for QTE markers ([ADR 027](../../decisions/027-combat-cinematic-timeline-events.md))
- `QTEController` — `OpenPrompt` / `ClosePrompt` / `CancelActivePrompts`; outputs `QTEResult` tier
- `CombatPresentationController` — cinematic lock; skip order: cancel QTE → `Stop()` → base resolve on `stopped`
- Exploration camera **unchanged** — combat scene only

---

## Scope

| Milestone | Deliverable |
|-----------|-------------|
| **MVP1** | `Fixed` only; cinematic + QTE **stubbed** (no prompts in shipping fights) |
| **MVP2** | 1 party `CinematicQTE` + 1 boss `Cinematic` (no QTE); pipeline + UI |
| **Later** | More skills; hold/mouse prompt types; Protocol cinematic QTE |

See [release scope](../00-release-scope.md). Optional in MVP2 alongside gather/fish — prioritize if combat spectacle is a milestone goal.

---

## Related docs

- [ADR 027 — Combat cinematic Timeline events](../../decisions/027-combat-cinematic-timeline-events.md)
- [Combat](combat.md)
- [Input bindings — cinematic QTE](input-bindings.md#cinematic-qte)
- [Synchro Protocol](synchro-protocol.md) — candidate for `CinematicQTE` finishers
- [04 — Tech notes](../04-tech-notes.md)
- [02 — Dungeon navigation](../02-dungeon-navigation.md)
