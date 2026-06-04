# Combat

Turn-based battles: readable **AGI turn order**, **3+3 core rows** plus **+1+1 auxiliary** slots for summons/guests.

Encounters **transition** from exploration FPV to a **battle arena** (fixed stratum backdrop, enemies on slot rig) — not in-world corridor combat ([combat scene](combat-scene.md), [ADR 013](../../decisions/013-combat-scene-rendering.md)).

## Battle layout

```
[ Navigator — off formation; Synchro Protocol + passives only ]

[ Enemies — up to 6 targets, front + back rows (**≤3** per row, MVP1) ([ADR 015](../../decisions/015-mvp1-combat.md)) ]

[ Core front ×3 ] [ Aux front ×1 ]   summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   summon or guest
```

- **Core (6):** guild party; always present in combat if alive.
- **Aux (0–2):** optional [summon or guest](summons-and-guests.md) per row.
- **Melee** without pierce targets **front row** (core + aux front) before back.
- **Ranged / spells** — per skill targeting rules.
- **Row collapse (locked MVP1):** when a front-row enemy dies, survivors **shift forward** (EO-style). Back-row-only remaining enemies become valid **melee** targets without pierce.
- **AllEnemies** skills hit **occupied enemy slots** only; pierce/back flags per skill ([mvp1-class-skills](../03-content/mvp1-class-skills.md)).
- **Status inflict:** resolve **damage first**, then roll bind/ailment if target still alive ([mvp1-class-skills § Locked](../03-content/mvp1-class-skills.md#locked-implementation-rules)).

## Turn structure — AGI order (EO-style)

**Not** strict "all party then all enemies."

### Combat round vs turn

| Term | Meaning |
|------|---------|
| **Turn** | One actor’s action when they reach their slot in the AGI queue |
| **Combat round** | Full cycle: every living combatant (party, aux, enemies) takes **one turn**; then end-of-round effects run |

FOE grid movement during battle ([ADR 005](../../decisions/005-foe-combat-patrol.md)) triggers **once per combat round**, not per individual turn.

### Round flow

1. Build **turn queue**: all living **core + aux + enemies** sorted by **AGI**.
2. Display queue icons (portraits; aux uses distinct frame).
3. **Command planning** — before AGI playback, player assigns **one command per living core**, then **one per living player summon** (and player guests without an AI script), in sequence. Highlight auto-advances to the next unassigned actor after each pick. Roster highlights the active `CommandTarget` (core or aux); queued slots show pending state. **Back** (`R` / `Esc`) pops the last queued command and returns highlight to that actor ([#61](https://github.com/miramocha/griddungeon-game/issues/61)). Summons **on the field at planning start** are included; a unit deployed during the **same** round’s AGI (e.g. first-turn `deploy_scout_drone`) plans on the **next** round. When every required actor has a command, combat **auto-commits** and enters turn phase ([game #58](https://github.com/miramocha/griddungeon-game/issues/58)).
4. **Turn phase** — each actor takes one action in **AGI order** (not assignment order). Living cores, summons, and player guests execute their **queued** commands on their queue slot (**no live command menu** during playback). **Dead combatants** in the pre-built queue are **skipped** immediately at turn start (no action, no step delay) until a living actor is current or the round ends ([#66](https://github.com/miramocha/griddungeon-game/pull/66)). Between resolved actions, `CombatController` waits **0.55s** by default (`ActionStepDelaySeconds`; **0** in Edit Mode tests) so HP/target UI can be read. On a **core** turn, if [Synchro Charge](synchro-protocol.md) is 100% and **unlocked**, player may use **Protocol** instead of attack/guard/skill; **[Navigator](navigator.md)** executes; charge → 0% ([ADR 006](../../decisions/006-union-team-bar.md), [ADR 007](../../decisions/007-navigator-role.md)). Other core actions **gain** charge when below 100% (summon actions do not). **S1 first FOE:** scripted tutorial — FOE **unbeatable** until Protocol finisher; **crisis AOE** (party to 1 HP) → unlock VN → **guided** `protocol_strike` → FOE kill → hub warp ([story events § S1 flow](story-events.md#s1-tutorial-flow-foe_alley_stalker), [synchro § S1 gating](synchro-protocol.md#s1-tutorial-gating-first-foe)).
5. **End of combat round** — status ticks, summon duration −1; optional FOE patrol tick ([ADR 005](../../decisions/005-foe-combat-patrol.md)); check wipe/victory; rebuild queue if fight continues.

### Command planning — back

During **command planning**, each pick is **confirmed** with **`Z`** (keyboard) or **LMB** (mouse) and writes to `PartyCommandBatch`. Per-command focus navigation is [ADR 026](../../decisions/026-combat-menu-focus-navigation.md). Optional **round-end** confirm after all cores are assigned is [#44](https://github.com/miramocha/griddungeon-game/issues/44) (separate).

| Player need | MVP1 spec | Status |
|-------------|-----------|--------|
| Step back one **mistaken** pick | **`X`** or **Back button** → LIFO remove last queued command; highlight returns to that core | [game #61](https://github.com/miramocha/griddungeon-game/issues/61) — rebind per ADR 026 |
| Jump to an earlier core without stepping back through picks | Roster LMB re-select that core, then re-pick | Roster re-select **not wired** ([#58](https://github.com/miramocha/griddungeon-game/issues/58) follow-up) — **no** roster keyboard |
| Cancel the **whole** round plan | Dedicated control + confirm dialog | Deferred to [#44](https://github.com/miramocha/griddungeon-game/issues/44) |

**Input:** Arrows or **`W`/`A`/`S`/`D`** move focus on command bar (WASD mirrors arrows in combat); **`Z`** confirms command; **`X`** / **Back button** = Back (LIFO or cancel targeting). **`Esc`** = pause when pause UI ships (no-op until then). **`R`** dropped ([input bindings](input-bindings.md), [ADR 026](../../decisions/026-combat-menu-focus-navigation.md)).

**UI:** Command bar **Back button**; enabled when targeting or when LIFO is available. Global hint: **Z Confirm · X Cancel · Esc Pause**. Roster **queued** styling clears when a command is popped.

### Command planning — targeting

After **Attack** or a **single-target** skill during command planning ([#60](https://github.com/miramocha/griddungeon-game/issues/60)):

1. Valid enemy (or ally, per `TargetingRule`) slots **highlight** on the roster (`ValidTargetCalculator`).
2. **Focus moves to the target list** (Path B, ADR 026); first valid slot highlighted; **arrow keys or `W`/`A`/`S`/`D`** move highlight; **`Z`** confirms `TargetId` and advances planning.
3. **LMB** on a valid slot confirms immediately (no **`Z`**).
4. **`X`** or **Back button** cancels targeting without queuing.
5. **No valid targets** — command panel shows “No valid targets”; player must pick another command or Back.

**Stale queued targets ([#65](https://github.com/miramocha/griddungeon-game/issues/65)):** If a queued `TargetId` points at a dead or invalid combatant during planning or before that action resolves, the roster shows **dashed stale styling** and tooltip *“Target down — will retarget”*. At **AGI playback**, `CombatTargeting.ResolveLivingTarget` retargets within the valid set or drops the action per rules.

**Living-target resolution:** Queued `TargetId` is resolved at AGI playback (including enemy `SingleEnemy` vs party rows). `CanTargetBack` on the skill gates back-row picks ([game #56](https://github.com/miramocha/griddungeon-game/issues/56) — full row-collapse rules still open).

**Speed Boost** / **Slow** modify effective AGI when building the queue ([combat-status-and-buffs](combat-status-and-buffs.md#stat-buffs--debuffs)).

## Commands (core party)

| Command | Notes |
|---------|-------|
| Attack | Weapon hit; target enemy slot |
| Guard | Damage reduction until next turn |
| Skill | Class skill; opens **use picker** (default tab **All**, type tabs per [ADR 035](../../decisions/035-skill-use-picker.md)); may **place summon** in aux slot |
| Item | Usable consumables |
| Flee | Queued in command planning like other commands; **resolves on that core’s AGI turn** (not instant). Success roll via `FleeCalculator` (see [§ Flee success](#flee-success-mvp1)); may fail (wasted turn). Retreat cell rule: [FOE flee](foe-encounters.md#flee-from-foe-fights-locked) |
| Protocol | **Navigator executes**; Synchro 100%; uses the acting **core** member’s AGI turn (`CombatCommand.Protocol` + skill id) |

## Commands (summon / guest)

| Unit | MVP1 control |
|------|----------------|
| **Summon** | **Player-controlled** — Attack / Guard + `SummonDefinition.skillIds`; queued in **command planning** before AGI ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **Guest** | Player guests without `actionScript` → same planning batch; **NPC guest** with script = AI on AGI turn |
| **Summon (later)** | Optional **stance hybrid** (AI from kit) |

## Commands (enemy)

- Attack, skill, debuff, buff allies, **summon adds** (may fill enemy aux or extra slots), flee (rare).

## Damage pipeline (MVP1)

Locked for MVP1 ([ADR 015](../../decisions/015-mvp1-combat.md)). Tune constants in data; structure unchanged.

```
hitChance = clamp( baseHit + attacker.AGI*0.5 - defender.AGI*0.3 + blindMod, 5, 95 )
if random(100) > hitChance → MISS

# Physical (Attack, slash/pierce skills)
raw = (skillPower + STR * 0.5) * offenseMult / defenseMult
mitigated = raw * (100 / (100 + defender.VIT))
damage = mitigated * slashRes * pierceRes   # 1.0 default; 1.5 weak, 0.5 resist

# Elemental (fire / ice / volt)
raw = (skillPower + TEC * 0.3) * magicMult
damage = raw * elementRes   # 1.5 weak, 0.5 resist, 2.0 null, 0.25 absorb

apply Guard (×0.5) and battle modifiers
HP -= max(1, floor(damage))   # minimum 1 on hit
roll on-hit status inflicts
```

| Tag | MVP1 |
|-----|------|
| Elements | fire, ice, volt |
| Physical tags | slash, pierce (on skills) |
| Heals | `skillPower + TEC * 0.4`, no hit roll |

Full rules: **[combat status & buffs](combat-status-and-buffs.md)**.

### Flee success (MVP1)

Resolved on the **acting core’s AGI turn** when `CombatCommand.Flee` was queued during planning ([game #66](https://github.com/miramocha/griddungeon-game/pull/66)).

```
successPercent = clamp( (1.5 − enemyAvgAgi / partyAvgAgi) × 100, 5, 95 )
roll ≤ successPercent → flee succeeds (subject to BattleState.FleeEnabled / retreat cell)
```

`FleeCalculator` in Core; dev **F4** / phase HUD may still call instant `SubmitFlee` for QA.

## Status, buffs & debuffs (summary)

| Category | Examples | When it matters |
|----------|----------|-----------------|
| **Control ailments** | Sleep, Panic, Paralysis (post-MVP1) | Turn start — skip or randomize action |
| **Limb binds** | Head / Arm / Leg | Block skills by `Body` tag; Attack blocked if Arm bind |
| **DoT** | Poison, Burn | End of combat round — HP tick |
| **Stat mods** | Offense/Defense/Magic/Speed Up & Down, Blind | Damage + AGI queue; refresh same ID, no stack |
| **Battle mods** | Guard, Charge | Until consumed or next turn |

**End of combat round:** regen → DoT ticks → duration −1 → expire ([combat-status-and-buffs](combat-status-and-buffs.md#timing-model)).

**Navigator:** no ailments ([navigator](navigator.md)). **Hospital** clears standard statuses between dives.

## FOE vs random fights

| | Random | FOE |
|---|--------|-----|
| Trigger | Step roll | Grid contact |
| Difficulty | Floor table | Designed spawn; higher XP/drops |
| Repeat | Per step roll only (no map entity) | FOEs respawn on hub return and re-entry ([ADR 008](../../decisions/008-campaign-defaults.md)) |

## FOE patrol & mid-battle join (MVP2)

**Not MVP1** ([ADR 015](../../decisions/015-mvp1-combat.md)). When [ADR 005](../../decisions/005-foe-combat-patrol.md) enabled on floor:

- Party frozen on fight-start cell; each **combat round** FOEs move **1 cell** on patrol.
- FOE on party cell → **[mid-battle join](chain-foe-battle.md)** ([ADR 010](../../decisions/010-chain-foe-battle.md)): **one FOE per round** joins current fight; first turn **next combat round**.
- No separate post-victory FOE fight for the same overlap.

Exploration patrol ([ADR 003](../../decisions/003-foe-step-patrol.md)) paused until battle ends.

## Victory / defeat

- **Victory:** XP to **core party only**; drops; quest progress.
- **Wipe:** GAME OVER → hub load; see [hub](hub-and-services.md).
- **Flee:** Return to exploration; summons end. **FOE fights:** party pushed **1 cell back** if retreat cell open; flee **disabled** if wall behind ([foe-encounters](foe-encounters.md), [ADR 011](../../decisions/011-foe-flee-retreat.md)).

## Presentation (spells & skills)

- **Most skills:** [fixed battle camera](combat-presentation.md) — same angle; optional slight zoom; fast resolve.
- **Cinematic skills:** scripted camera + animation (boss telegraphs, spectacle) — skippable.
- **Cinematic QTE skills (MVP2+):** same as cinematic + **timed button prompts** — bonus damage/effects on good timing; **base skill always lands** on miss.

See [combat presentation](combat-presentation.md).

## Input

PC: combat **menu focus** — arrows or **`W`/`A`/`S`/`D`**, **`Z`** confirm, **`X`** / **Back button** cancel/LIFO ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md)); **`Esc`** pause when UI ships; mouse one-click commands and LMB targets — [input bindings](input-bindings.md).

## UI requirements

- **Reactive feedback** — HUD animates on combat events (not static swaps only); see [§ UI motion & feedback](#ui-motion--feedback), [tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity), and [UI event contract](../04-dev/ui-event-contract.md#combat-phase) (integrator event list)
- **Skill** command — tabbed skill-use modal ([ADR 035](../../decisions/035-skill-use-picker.md), [custom skill picker UI](../04-dev/custom-skill-picker-ui.md)); then targeting when required ([#60](https://github.com/miramocha/griddungeon-game/issues/60))
- **Party / enemy plates** — formation roster slots ([custom party UI](../04-dev/custom-party-ui.md)); acting highlight on **party roster** during core command turns (not AGI strip)
- **Navigator** portrait + aura badges — [navigator](navigator.md)
- **Synchro Charge** (team, 0–100%) — see [synchro-protocol](synchro-protocol.md)
- **Turn order strip** — see [§ Turn order strip](#turn-order-strip-agi-queue-ui) below
- **4+4 row layout** — six core portraits + two aux slots (empty aux hidden or dimmed)
- Aux label: Summon / Guest
- **Command planning:** one queued action per living core before AGI playback; roster `CommandTarget` highlight + queued/pending styling; **focus navigator** on command bar + target list ([ADR 026](../../decisions/026-combat-menu-focus-navigation.md))
- **Turn phase:** cores and summons play **queued** commands on their AGI slot; no mid-playback summon menu ([ADR 016](../../decisions/016-summon-control-mvp1.md))
- **Target selection** during command planning — valid highlights + arrows/WASD/`Z` + LMB; stale-target affordance ([#60](https://github.com/miramocha/griddungeon-game/issues/60), [#65](https://github.com/miramocha/griddungeon-game/issues/65))
- Combat log
- Enemy weakness icons when identified
- Status icons + turns remaining on portraits — [status & buffs](combat-status-and-buffs.md#ui)

### UI motion & feedback

Every row below needs a **visible** reaction (DOTween or USS transition). Pair with combat log text; log alone is insufficient for MVP1.

**Blocking:** `CombatPresentationGate` — AGI playback waits until `CombatHudReactivePresenter` finishes mandatory beats ([#35](https://github.com/miramocha/griddungeon-game/pull/35)); EO-style pacing ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)).

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Turn advances | AI/auto: turn strip handoff to `Current`. **Player command:** acting highlight on **party roster** slot, not strip | Yes — next AGI turn / command |
| Damage / heal | Target portrait **flash** + HP/MP bar **lerp**; optional floating number near slot | Yes — next action on that beat |
| Status applied / cleansed | Icon **pop-in** or brief tint on portrait + queue icon | Yes |
| Death / KO | Portrait **grey + scale down** or slide out; strip slot removed on rebuild with short fade | Yes |
| Synchro Charge change | Meter fill **lerps**; at 100% brief **glow** before Protocol use | Yes — Protocol command on core turn |
| Protocol use | Navigator + participating cores **highlight** ([synchro-protocol](synchro-protocol.md)) | Yes — same core turn continues after resolve |
| Valid targeting | Enemy/portrait **outline pulse** on valid slots ([#60](https://github.com/miramocha/griddungeon-game/issues/60)) | No — selection is interactive; pulse loops until pick |
| Stale queued target | Dashed roster frame + tooltip *Target down — will retarget* ([#65](https://github.com/miramocha/griddungeon-game/issues/65)) | No — informational during planning / playback |
| Summon auto-turn | Aux portrait highlight → VFX → log ([summons & guests](summons-and-guests.md)) | Yes — next queue entry |
| FOE join (MVP2) | New enemy chevron **slides in** on strip next round ([chain FOE](chain-foe-battle.md)) | Yes — next round start |
| Combat log line | Newest entry **fade/slide in**; scroll to bottom | Bundled with the beat above (same lock) |

**Shipped presenters:** `CombatHudReactivePresenter` (log fade/slide, HP/Synchro lerp, hit/KO/status flashes, turn-strip handoff), `CombatHudLogView` (log scroll/format), `CombatTutorialHudRules` (Core — S1 stalker command gating). `CombatController` / `CombatScenePresenter` stay authoritative for rules.

### Turn order strip (AGI queue UI)

Combat must show a **horizontal strip** (left → right = soonest → latest) listing **every combatant in the current round’s AGI queue**:

| Included | Excluded |
|----------|----------|
| Living **core**, **aux**, and **enemies** in `TurnQueue.Ordered` | **Navigator** (Protocol only; separate portrait) |
| | Dead / KO at **queue rebuild** (round start/end); mid-round deaths **skip** turn without rebuild |

**Data:** `TurnQueue.Ordered` from `TurnQueueBuilder` at round start; `TurnQueue.Current` drives highlight. UI binds via `TurnOrderStripView.Bind(TurnQueue)` ([class design](../05-class-design-mvp1.md#view-controllers)).

**Visual rules (MVP1):**

- **Current actor (auto / AI turn):** turn strip shows strong highlight (frame glow / scale) with **animated handoff** when the queue advances; strip does not scroll away from active slot during the turn.
- **Player command phase (core turn):** strong highlight on the **acting core’s party roster slot** (formation row), **not** on the strip — strip stays informational only while the player picks Attack / Guard / Skill / etc. (#34 skeleton; full handoff beats in [combat presentation](combat-presentation.md)).
- **Party vs enemy:** distinct frame or background tint; aux uses summon/guest frame ([summons & guests](summons-and-guests.md)).
- **Enemies:** portrait or silhouette + row hint (front/back); weakness icons stay on enemy row UI, not required on every queue icon.
- **Status:** control ailments (Sleep, etc.) show on the queue icon; skipped turns grey the slot ([status UI](combat-status-and-buffs.md#ui)).
- **Rebuild:** full strip refresh when the queue is rebuilt (start of round, end of round). Mid-round deaths: strip may still show the slot until rebuild; turn advances via **skip dead** ([§ Round flow](#round-flow)). Mid-round inserts (e.g. FOE join MVP2) update on the **next** round ([chain FOE](chain-foe-battle.md#ui--presentation)).
- **Strip width / names:** wider plates; full names via USS ellipsis (no C# truncation) ([#66](https://github.com/miramocha/griddungeon-game/pull/66)).
- **Cinematics:** strip stays on screen, dimmed; never fully hidden ([combat presentation](combat-presentation.md#ui-during-cinematic)).

**Not in MVP1 UI:** speed buff/debuff reordering ([ADR 015](../../decisions/015-mvp1-combat.md)); strip order still reflects AGI at build time once those statuses ship.

**Acceptance:** player can answer “who acts next?” without reading the combat log — matches [vision](../00-vision.md) and [MVP1 spec](../mvp1-spec.md) AGI queue UI.

### Enemy roster UI (formation rows)

Combat HUD shows enemies in **two labeled rows** — **Front** and **Back** — not a single flat wrap list. The AGI turn-order strip stays a **flat** queue (no row grouping).

| UI area | Layout | Data |
|---------|--------|------|
| **Front row** | Up to **3** portrait cards, left → right | `BattleState.EnemySlots[0..2]` — occupied slots only (empty indices hidden) |
| **Back row** | Up to **3** portrait cards, left → right | `BattleState.EnemySlots[3..5]` — occupied slots only |
| **Row label** | Small heading per row (`Front` / `Back`) | Mirrors party row affordance; optional subtle row tint on cards |

**Slot index map** (shared by UI, arena rig, and VFX):

| Tactical row | Slot indices | Arena anchor |
|--------------|--------------|--------------|
| Front | `0`, `1`, `2` | `EnemySlot_0` … `EnemySlot_2` |
| Back | `3`, `4`, `5` | `EnemySlot_3` … `EnemySlot_5` |

Sparse authoring (e.g. two front, one back) keeps **index gaps** in `EnemySlots[]` — UI and arena show only **non-null** combatants at their index, not collapsed into a single row. Example: front at `0` and `2`, back at `4` → front row shows two cards with a visual gap or left-aligned pair per HUD style ([04-tech-notes § Combat HUD](../04-tech-notes.md#combat-hud-ui-toolkit)).

**MVP1 implementation:** `CombatHud` enemy panel → `enemy-roster-front` / `enemy-roster-back` containers; `CombatRosterView.BindEnemyFormation`. Party roster uses **Front** / **Back** rows (`party-roster-front`, `party-roster-back`) — one portrait card per occupied core slot (6 + aux later). Replace or reskin plates: [custom party UI](../04-dev/custom-party-ui.md#combat-party-roster).

## Related docs

- [MVP1 spec](../mvp1-spec.md)
- [Combat scene & enemy rendering](combat-scene.md)
- [Combat status & buffs](combat-status-and-buffs.md)
- [Navigator](navigator.md)
- [Synchro Protocol (team bar)](synchro-protocol.md)
- [Combat presentation](combat-presentation.md)
- [Party & classes](party-and-classes.md)
- [Summons & guests](summons-and-guests.md)
- [Character progression](character-progression.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
