# Combat

Turn-based battles: readable **AGI turn order**, **3+3 core rows** plus **+1+1 auxiliary** slots for summons/guests.

Encounters **transition** from exploration FPV to a **battle arena** (fixed stratum backdrop, enemies on slot rig) — not in-world corridor combat ([combat scene](combat-scene.md), [ADR 013](../../decisions/013-combat-scene-rendering.md)).

## Battle layout

```
[ Navigator — off formation; Union + passives only ]

[ Enemies — up to 5 targets, front + back rows (MVP1) ([ADR 015](../../decisions/015-mvp1-combat.md)) ]

[ Core front ×3 ] [ Aux front ×1 ]   summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   summon or guest
```

- **Core (6):** guild party; always present in combat if alive.
- **Aux (0–2):** optional [summon or guest](summons-and-guests.md) per row.
- **Melee** without pierce targets **front row** (core + aux front) before back.
- **Ranged / spells** — per skill targeting rules.

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
3. **Turn phase** — each actor takes one action in AGI order. On a **core** turn, if [Union bar](union.md) is 100%, player may use **Union** instead of attack/guard/skill; **[Navigator](navigator.md)** executes; bar → 0% ([ADR 006](../../decisions/006-union-team-bar.md), [ADR 007](../../decisions/007-navigator-role.md)). Other actions charge the Union bar when below 100%.
4. **End of combat round** — status ticks, summon duration −1; optional FOE patrol tick ([ADR 005](../../decisions/005-foe-combat-patrol.md)); check wipe/victory; rebuild queue if fight continues.

**Speed Boost** / **Slow** modify effective AGI when building the queue ([combat-status-and-buffs](combat-status-and-buffs.md#stat-buffs--debuffs)).

## Commands (core party)

| Command | Notes |
|---------|-------|
| Attack | Weapon hit; target enemy slot |
| Guard | Damage reduction until next turn |
| Skill | Class skill; may **place summon** in aux slot |
| Item | Usable consumables |
| Flee | May fail; see [FOE flee](foe-encounters.md#flee-from-foe-fights-locked) for retreat cell rule |
| Union | **Navigator executes**; bar 100%; uses the acting **core** member’s AGI turn (`CombatCommand.Union` + skill id) |

## Commands (summon / guest)

| Unit | MVP1 control |
|------|----------------|
| **Summon** | **Scripted** — fixed `actionScript` each turn; no player menu ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **Guest** | Player commands by default; **NPC guest** = AI script |
| **Summon (later)** | Player control vs hybrid vs scripted — **decide later** ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |

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
| Repeat | FOEs respawn when party returns to hub and re-enters floor ([ADR 008](../../decisions/008-campaign-defaults.md)) |

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

PC: combat commands `1`–`5`, mouse targets, `U` Union at round start — [input bindings](input-bindings.md).

## UI requirements

- **Reactive feedback** — HUD animates on combat events (not static swaps only); see [§ UI motion & feedback](#ui-motion--feedback) and [tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)
- **Navigator** portrait + aura badges — [navigator](navigator.md)
- **Union bar** (team, 0–100%) — see [union](union.md)
- **Turn order strip** — see [§ Turn order strip](#turn-order-strip-agi-queue-ui) below
- **4+4 row layout** — six core portraits + two aux slots (empty aux hidden or dimmed)
- Aux label: Summon / Guest
- Command phase: one action per **player-controlled** core combatant; summons **auto-resolve** in MVP1
- Target selection with valid highlights
- Combat log
- Enemy weakness icons when identified
- Status icons + turns remaining on portraits — [status & buffs](combat-status-and-buffs.md#ui)

### UI motion & feedback

Every row below needs a **visible** reaction (DOTween or USS transition). Pair with combat log text; log alone is insufficient for MVP1.

**Blocking:** `CombatController` (or a small presentation gate) holds input until the row’s tweens finish — EO-style pacing ([tech notes — UI reactivity](../04-tech-notes.md#ui-reactivity)).

| Event | UI reaction (MVP1) | Blocks until done |
|-------|-------------------|-------------------|
| Turn advances | Turn strip: highlight **slides** or **pulses** to `Current`; previous slot eases to idle | Yes — next AGI turn / command |
| Damage / heal | Target portrait **flash** + HP/MP bar **lerp**; optional floating number near slot | Yes — next action on that beat |
| Status applied / cleansed | Icon **pop-in** or brief tint on portrait + queue icon | Yes |
| Death / KO | Portrait **grey + scale down** or slide out; strip slot removed on rebuild with short fade | Yes |
| Union bar change | Fill **lerps**; at 100% brief **glow** before Union phase | Yes — Union phase entry |
| Union phase | Navigator + participating cores **highlight** ([union](union.md)) | Yes — first AGI turn after Union |
| Valid targeting | Enemy/portrait **outline pulse** on valid slots | No — selection is interactive; pulse loops until pick |
| Summon auto-turn | Aux portrait highlight → VFX → log ([summons & guests](summons-and-guests.md)) | Yes — next queue entry |
| FOE join (MVP2) | New enemy chevron **slides in** on strip next round ([chain FOE](chain-foe-battle.md)) | Yes — next round start |
| Combat log line | Newest entry **fade/slide in**; scroll to bottom | Bundled with the beat above (same lock) |

Presenters implement motion; `CombatController` / `CombatScenePresenter` stay authoritative for rules.

### Turn order strip (AGI queue UI)

Combat must show a **horizontal strip** (left → right = soonest → latest) listing **every combatant in the current round’s AGI queue**:

| Included | Excluded |
|----------|----------|
| Living **core**, **aux**, and **enemies** in `TurnQueue.Ordered` | **Navigator** (Union only; separate portrait) |
| | Dead / KO combatants (removed when queue rebuilds) |

**Data:** `TurnQueue.Ordered` from `TurnQueueBuilder` at round start; `TurnQueue.Current` drives highlight. UI binds via `TurnOrderStripView.Bind(TurnQueue)` ([class design](../05-class-design-mvp1.md#view-controllers)).

**Visual rules (MVP1):**

- **Current actor:** strong highlight (frame glow / scale) with **animated handoff** when `Advance()` runs; strip does not scroll away from active slot during the turn.
- **Party vs enemy:** distinct frame or background tint; aux uses summon/guest frame ([summons & guests](summons-and-guests.md)).
- **Enemies:** portrait or silhouette + row hint (front/back); weakness icons stay on enemy row UI, not required on every queue icon.
- **Status:** control ailments (Sleep, etc.) show on the queue icon; skipped turns grey the slot ([status UI](combat-status-and-buffs.md#ui)).
- **Rebuild:** full strip refresh when the queue is rebuilt (start of round, after deaths, end of round). Mid-round inserts (e.g. FOE join MVP2) update on the **next** round ([chain FOE](chain-foe-battle.md#ui--presentation)).
- **Cinematics:** strip stays on screen, dimmed; never fully hidden ([combat presentation](combat-presentation.md#ui-during-cinematic)).

**Not in MVP1 UI:** speed buff/debuff reordering ([ADR 015](../../decisions/015-mvp1-combat.md)); strip order still reflects AGI at build time once those statuses ship.

**Acceptance:** player can answer “who acts next?” without reading the combat log — matches [vision](../00-vision.md) and [MVP1 spec](mvp1-spec.md) AGI queue UI.

## Related docs

- [MVP1 spec](../mvp1-spec.md)
- [Combat scene & enemy rendering](combat-scene.md)
- [Combat status & buffs](combat-status-and-buffs.md)
- [Navigator](navigator.md)
- [Union (team bar)](union.md)
- [Combat presentation](combat-presentation.md)
- [Party & classes](party-and-classes.md)
- [Summons & guests](summons-and-guests.md)
- [Character progression](character-progression.md)
- [03 — Dungeons & encounters](../03-content/dungeons-and-encounters.md)
