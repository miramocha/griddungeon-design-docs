---
tags:
  - path/docs/02-systems
  - type/system
  - scope/required
  - status/draft
  - domain/synchro
---
# Navigator

**Scope:** [Required](../00-release-scope.md#required-first-playable)

**Party lead** who sits **outside** the 3+3 combat formation. They command [Synchro Protocol](synchro-protocol.md) skills and provide **passive buffs** to the active core six.

**Narrative:** The player **is** the active Navigator ([narrative POV](narrative-pov.md)) — *Amnesia*-style **blank state** at new game; Synchro / Protocol and role lore **unlock through play**, not upfront exposition.

## Narrative role at launch

| Topic | Locked direction |
|-------|------------------|
| **POV** | First-person Navigator on the **sideline** with the crew — story VN + guided coach share one voice ([narrative POV](narrative-pov.md)) |
| **Memory** | No self-knowledge at Act 1 start; first **named** mechanic beat = post-crisis Synchro unlock on B2F |
| **Cores** | Silent in scripted lines — player builds any six classes |
| **Display name** | `guild_handler` = data id; in-fiction the Navigator may not say “Sortie Lead” until hub/office beats teach it |

See [narrative POV — reveal pacing](narrative-pov.md#blank-state-locked) for S1 beat table.

## Role summary

| | Navigator | Core party (6) | Aux summon/guest |
|---|-----------|----------------|------------------|
| **Formation** | Off-formation | 3 front + 3 back | +1 front / +1 back |
| **AGI turns** | No | Yes | Yes (if living) |
| **Protocol skills** | **Executes** when Synchro 100% | **Participate** per skill rules | No |
| **Passive buffs** | **Grants** to core six | Receive | No at launch |
| **Exploration grid** | No | Yes (party blob) | No |
| **Swappable** | **Hub only** | Hub bench (core) | N/A |

```
[ Navigator — off formation, portrait + passives + Protocol command ]

[ Core front ×3 ] [ Aux front ×1 ]
[ Core back  ×3 ] [ Aux back  ×1 ]
```

## Active Navigator

- Exactly **one** Navigator is **active** per labyrinth dive (assigned at **Navigator Office** before entry).
- **Unlock pool:** Navigators are **not recruited** at Explorers Guild. New Navigators **unlock** as the campaign progresses; unlocked Navigators are listed at **Navigator Office**.
- **Switch:** **hub only** (Navigator Office) — assign active Navigator before entering or when returning to hub. **No** mid-dungeon switch (no camp/inn swap in labyrinth).

### How Navigators unlock

| Source | Example |
|--------|---------|
| **Stratum progress** | Beat Stratum 1 boss → unlock **Sync Relay** |
| **Side quests** | Rescue NPC → unlock **Wellness Lead** |
| **Events** | Story scene after floor gimmick → unlock **Route Analyst** |
| **Optional milestones** | 100% map on B2F, FOE codex entries → **Ledger Chief**, etc. |

- Each Navigator has an `unlockCondition` in data (flag, quest id, stratum id).
- **Starting Navigator:** one Navigator available from game start (tutorial default).
- Locked Navigators are visible at **Navigator Office** as **silhouettes + unlock hint** (optional UX).

## Passive buffs (auras)

While a Navigator is active, the **core six** receive that Navigator’s **aura** — always on in combat and exploration.

| Example Navigator | `navigator_id` | Aura (draft) | Notes |
|-------------------|----------------|--------------|-------|
| **Sortie Lead** | `guild_handler` | +5% Synchro Charge gain (launch starter) | Expedition flight lead; executes [Protocol](synchro-protocol.md) |
| **Route Analyst** | `route_analyst` | +5% accuracy to core | Course / grid planning — not combat targeting |
| **Wellness Lead** | `wellness_lead` | −5% MP cost on core heals | Crew care; pairs with **Medic** kits, not the `medic` class |
| **Sync Relay** | `sync_relay` | +3% Synchro Charge gain from core actions | Comms loop for team Synchro; stratum unlock candidate |
| **Ledger Chief** | `ledger_chief` | +8% Credits from battles | Post-sortie accounts / manifest payouts |

Draft naming: **soft sci-fi expedition flight** (≤2 words, non-battle). Same hub-lead layer as [party classes](party-and-classes.md) field jobs — do not reuse core `class_id` labels (`tactician`, `medic`, …).

- Auras stack only from **one** Navigator (no multi-navigator stack).
- **Fixed per Navigator** — no levels, tiers, or upgrades. New power only by **unlocking a different Navigator**.
- **Starter:** **Sortie Lead** (`guild_handler`) at new game; more unlock via strata / quests / events.

## Protocol execution

When [Synchro](synchro-protocol.md) is **100%**, a **core member** on their AGI turn may invoke a Protocol (`CombatCommand.Protocol`) — that core **spends their turn**. The **active Navigator** **executes** the skill off-formation (calls the protocol; does not take an AGI turn):

1. Synchro Charge must be **100%** on the invoking core’s turn.
2. Player picks a Protocol from the Navigator’s **kit** (`protocol_strike`, `protocol_mend` at launch; later includes `protocol_deploy` per [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)).
3. Navigator executes; living **core** members participate per skill min/max.
4. Bar → **0%**; invoking core’s turn ends; queue advances.

Navigator **does not** gain Synchro Charge themselves (no combat turns). Core six actions still fill the team pool.

## Combat targeting (locked)

Navigators are **never combat targets**:

- **Not targetable** by enemies — normal attacks, skills, and **boss** abilities.
- **No direct combat interaction** — no HP, no damage, no status, no heals aimed at Navigator.
- **No AGI turn** — enemies and allies do not “hit” or buff Navigator in the turn system.
- UI: Navigator portrait **without HP bar**; present for Protocol + aura only.

Bosses cannot bypass this with “hit all party” — those effects apply to **core (+ aux summons/guests)** only. A **navigator sortie summon** from Protocol Deploy is aux and **is** targetable; the off-formation Navigator is not ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)).

## Progression (simple)

Navigators do **not** progress like core party members:

- **No XP**, **no levels**, **no skill points**, **no aura tiers**
- **No equipment**
- Each Navigator is a **fixed package**: one aura + fixed Protocol skill list, defined in data
- **Only growth path:** unlock another Navigator with different aura/skills

Out of scope: Navigator leveling, trees, gear, or scaling auras.

### Later Protocol skills

| Skill | Summary | ADR |
|-------|---------|-----|
| **Protocol Deploy** (`protocol_deploy`) | Sortie **aux summon** in empty slot; player-controlled summon kit; Navigator name on portrait | [023](../../decisions/023-protocol-deploy-sortie-summon.md) |
| **Protocol Transform** (`protocol_transform`) | **Slot-replace** one living core with Navigator **transform profile**; hybrid commands; **Revert** / duration / HP→0 revert safe; label **profile + “via [Core]”** | [024](../../decisions/024-protocol-transform.md) |

Shared: **core** spends AGI turn at Synchro 100%; Navigator **executes** off-formation; **aura on**; **multiple** Protocols per battle when Synchro **recharges** — blocked only while sortie or transform is **active**.

**Same-fight Deploy + Transform** is uncommon: kit is fixed at hub for the whole dive; only possible if this Navigator’s data lists **both** skills ([synchro-protocol § Kit + hub lock](synchro-protocol.md#kit--hub-lock-practical)). Prefer **one** mode skill per Navigator in content.

## Hub — Navigator Office

Separate from **Explorers Guild** ([hub & services](hub-and-services.md)). Guild handles core six; Navigator Office handles party leads only.

| Action | Detail |
|--------|--------|
| **Browse** | All Navigators — unlocked (selectable) vs locked (silhouette + hint) |
| **Assign** | Set **active** Navigator for the next labyrinth dive |
| **Preview** | Aura summary on core six; list of Protocol skills in this Navigator’s kit |
| **Switch** | Change active Navigator among unlocked pool — **hub only** |

No recruitment, no skill points, no equipment — unlock + assign only.

### Presentation at Navigator Office (locked direction for explore)

Hub is **menu-driven** ([hub & services § Hub environment](hub-and-services.md#hub-environment-presentation)) — no avatar walk, no labyrinth HUD. Navigator Office uses the **same roster UX pattern as Explorers Guild**: **2D portraits** in a Toolkit panel, not the bottom-right **3D corner rig** used on expedition.

| Surface | What the player sees | Navigator 3D corner model? |
|---------|----------------------|----------------------------|
| **Hub root menu** | Service list over guild-town backdrop; later camera may pan to **Navigator lodge** when that row is focused | **No** — town is environment only |
| **Navigator Office screen** | Scrollable **portrait list** (unlocked selectable, locked silhouette + unlock hint), detail pane (name, aura text, Protocol kit list), **Assign active** | **No** — compare and pick from portraits |
| **Assign / focus feedback** | Portrait **glow**; aura preview **fade in** on core six preview strip ([hub service UI motion](hub-and-services.md#service-ui-motion)) | **No** |
| **Leave hub → stratum** | Phase transition fade; exploration HUD loads | **Yes** — corner model **fades in** with exploration phase ([§ Consider / explore](#consider--explore--navigator-3d-presence)) |
| **In labyrinth** | FPV + corner companion; combat keeps same anchor | **Yes** |

**Why portrait-based here (not corner 3D):**

- **Job of the screen** — roster management: scan many Navigators, read auras and Protocol lists, assign one for the **next dive**. Dense 2D rows match Guild core recruitment.
- **Fantasy split** — Office = **contract / briefing** (“who leads this sortie?”). Labyrinth = **field lead beside you** (corner model as expedition companion).
- **Layout** — Corner rig competes with hub service chrome and has no formation context; office already has a dedicated detail pane for the selected portrait.
- **Scope** — Launch ships office as portraits + motion only ([game #13](https://github.com/miramocha/griddungeon-game/issues/13)); corner 3D is explore and can land later without reopening office UX.

**Optional later office polish (still not corner rig):** when one Navigator row is focused, a **large bust or half-body 3D** in the office **detail pane only** (like a guild hall portrait frame) — supplementary to the list, not a second presentation system. Rejected for office: full-body corner widget, walkable Navigator avatar in the hub scene, or Deploy/Transform slot transitions (those are combat-only per [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md) / [024](../../decisions/024-protocol-transform.md)).

## UI

**Launch (locked):** Navigator **portrait + name** above or beside formation (not in front/back rows). Aura icons on core portraits (small badge from active Navigator). Protocol use: Navigator voice line / portrait pulse; skill picker shows **Navigator’s** Protocol list.

**Presentation explore:** [§ Consider / explore — Navigator 3D presence](#consider--explore--navigator-3d-presence) (corner model + Protocol transitions). Does **not** change launch portrait strip or [ADR 007](../../decisions/007-navigator-role.md) targeting rules.

## Launch content (locked)

Matches [synchro-protocol § Launch content](synchro-protocol.md#launch-scope) and [class design — content IDs](../03-content/content-ids.md#content-ids-locked).

| Navigator | `navigator_id` | Unlock | Aura at launch | Protocol kit |
|-----------|----------------|--------|-------------|--------------|
| **Sortie Lead** | `guild_handler` | Day one | +5% Synchro Charge gain (`synchroGainBonus = 0.05`) | `protocol_strike`, `protocol_mend` |

Additional Navigators unlock via strata/quests later.

## Launch scope

**Design (locked):**

- [x] One default Navigator (`guild_handler`) + aura documented
- [x] Launch Protocol kit: `protocol_strike`, `protocol_mend`
- [x] Not in formation rows or AGI queue (off-formation executor)

**Implementation (game — open):**

- [ ] Protocol picker when Synchro is 100% (production HUD — [game #19](https://github.com/miramocha/griddungeon-game/issues/19) / [#35](https://github.com/miramocha/griddungeon-game/issues/35))
- [ ] **Navigator Office:** pick active Navigator from **unlocked** pool ([game #13](https://github.com/miramocha/griddungeon-game/issues/13); later: starter + stratum unlock)

## Resolved decisions

- **Switch:** hub only
- **Targeting:** never — including bosses
- **Progression:** unlock-only — no XP, tiers, or equipment

---

## Consider / explore — Navigator 3D presence

**Open:** Design idea — **not locked**. Launch keeps portrait + strip UI ([§ UI](#ui)). Rules for Deploy / Transform stay in [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md) and [ADR 024](../../decisions/024-protocol-transform.md); this section is **how the Navigator is shown**, not who is targetable or which slot owns combat stats.

### Default — corner presence (exploration + combat)

| Phase | Presentation |
|-------|----------------|
| **Exploration** | Active Navigator **3D model** anchored **bottom-right** of the screen (HUD layer over FPV). Idle / react animations; does **not** walk on the dungeon grid ([role summary](#role-summary)). |
| **Combat** | Same **bottom-right** anchor while Navigator is **off-formation** (before / between / after mode skills). Coexists with launch **portrait strip** until a future HUD pass may fold them together. |
| **Hub** | **No corner model.** [Navigator Office](#hub--navigator-office) = **2D portraits** only; corner rig **spawns on enter stratum**, **despawns on return to hub**. |

One `NavigatorPresence` (or `NavigatorView`) rig: shared prefab, phase-aware camera/layer (screen-space corner vs slot-attached). **Hub office does not host this rig** — only `ExplorationPhaseController` / `CombatPhaseController` (or equivalent) enable it.

### Hub vs labyrinth (summary)

```
  HUB                          LABYRINTH
  ───                          ─────────
  Navigator Office             Exploration + Combat
  • Portrait list / detail     • Bottom-right 3D model (explore)
  • Assign active              • Same anchor in combat
  • No corner rig              • Protocol Deploy → aux slot (explore)
                               • Protocol Transform → core slot (explore)
         │ enter stratum
         └──────────────────────► corner model ON
         ◄──────────────────────┘ return hub → corner model OFF
```

See [§ Presentation at Navigator Office](#presentation-at-navigator-office-locked-direction-for-explore) for office screen breakdown.

### Protocol mode transitions (later skills)

When a core invokes **Protocol Deploy** or **Protocol Transform** at Synchro 100%, the corner model **transitions** into the relevant formation representation. The off-formation Navigator **entity** is unchanged for rules (no Navigator AGI turn; not a direct melee target — [ADR 007](../../decisions/007-navigator-role.md)).

| Protocol | Rules (locked) | Visual transition (idea) |
|----------|----------------|--------------------------|
| **Deploy** ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)) | Spawns **sortie summon** in empty **aux** slot; Navigator stays off-formation | Corner model **moves / dissolves / flies** into **aux slot** rig (arena anchor + combat UI frame). Portrait strip shows Navigator name on summon. |
| **Transform** ([ADR 024](../../decisions/024-protocol-transform.md)) | **Transform profile** replaces one **core** index; Navigator stays off-formation | Corner model transitions into that **core formation slot** (3+3 row / arena party side). UI keeps **“via [CoreName]”** label; corner may show dimmed placeholder or empty until revert. |

**End of mode:** On sortie dismiss / HP 0 recall, transform Revert / duration / HP→0 revert safe, or battle end — model **transitions back** to bottom-right corner (same beat as combat presentation handoff).

**Overlap:** Deploy sortie and Transform **cannot** be active together ([ADR 024](../../decisions/024-protocol-transform.md)); only one slot-attached representation at a time.

### Alignment with combat scene

- **Aux / core slots** in [combat scene](combat-scene.md) are where the transitioned model **lands** for battle presentation.
- **Launch Protocol** (`protocol_strike`, `protocol_mend`) — no slot transition; corner model optional even at launch if art budget allows (VFX-only pulse acceptable).

### Open questions (next pass)

| Question | Notes |
|----------|--------|
| Office detail-pane 3D bust? | Optional later; list portraits remain primary — [§ Presentation at Navigator Office](#presentation-at-navigator-office-locked-direction-for-explore) |
| One mesh vs sortie/transform variant? | Per-Navigator `battle_model` + optional `sortie_model` / `transform_model` in data. |
| Strip vs 3D authority | Until locked: **portraits + HP** remain source of truth for targeting; 3D is illustrative unless playtest proves otherwise. |
| Exploration corner blocks map chrome? | Layout pass with [mapping](mapping.md) side panel + bottom log strip. |

### Recommendation

Prototype corner idle in **exploration** first (cheap read: “party lead is here”). Add Deploy/Transform transitions when [ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md) / [024](../../decisions/024-protocol-transform.md) ship; playtest before replacing launch portrait-only Protocol UX.

## Related docs

- [Synchro Protocol (team bar)](synchro-protocol.md)
- [Party & classes](party-and-classes.md)
- [Combat](combat.md)
- [ADR 007 — Navigator role](../../decisions/007-navigator-role.md)
- [ADR 023 — Protocol Deploy sortie summon](../../decisions/023-protocol-deploy-sortie-summon.md)
- [ADR 024 — Protocol Transform](../../decisions/024-protocol-transform.md)
