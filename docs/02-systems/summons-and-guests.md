# Summons & Guests (Auxiliary slots)

Combat formation extends the core **3+3 guild party** with **one auxiliary slot per row** — front and back — for **summons** or **guest** allies.

## Formation (combat only)

```
[ Navigator — off formation; see navigator.md ]

[ Enemy row ]

[ Core front ×3 ] [ Aux front ×1 ]   ← summon or guest
[ Core back  ×3 ] [ Aux back  ×1 ]   ← summon or guest
```

| Slot type | Count | Who |
|-----------|-------|-----|
| **Navigator** | 1 active | Party lead; Synchro Protocol + passives; **not** in 3+3 ([navigator](navigator.md)) |
| **Core** | 3 front + 3 back | Guild roster; persistent; explore as one party blob |
| **Aux front** | 1 | One **summon** or **guest** (not both) |
| **Aux back** | 1 | One **summon** or **guest** (not both) |

**Max in battle UI:** Navigator + up to 8 (6 core + 2 aux).

Auxiliary units **do not** appear on the exploration grid — only in combat.

## Summons

| Property | Rule |
|----------|------|
| **Source** | **Summoner class** deploy skills (MVP1+); post-MVP1 **Protocol Deploy** sortie ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)); rare items / boss mechanics |
| **Placement** | Occupies aux **front** or **back** per skill definition |
| **Duration** | Turns remaining, HP hits zero, or dismissed |
| **Commands (MVP1)** | **Player-controlled** — Attack / Guard + summon `skillIds` on summon AGI turn ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **Commands (later)** | Optional **stance hybrid** (AI picks from kit) |
| **AGI** | Summon has own AGI; enters turn queue; **waits for player** like core |
| **XP** | No XP to summons |
| **Death** | Disappears; no hospital revive |
| **Between fights** | Does not persist unless skill says otherwise (buff before next fight — rare) |

**Stacking:** One summon per aux slot. **`deploy_test_drone`:** if aux back occupied → **fail**, **no MP spent** ([mvp1-class-skills](../03-content/mvp1-class-skills.md#locked-implementation-rules)).

### Navigator sortie (Protocol Deploy — post-MVP1)

| Property | Rule |
|----------|------|
| **Source** | Protocol skill `protocol_deploy` — active Navigator executes; **not** a Summoner class skill |
| **Spawn** | Empty aux front or back only; fails if slot occupied |
| **Combatant** | `CombatantKind.Summon` — per-Navigator `SummonDefinition` (sortie kit); `linkedNavigatorId` in data |
| **Navigator** | Stays **off-formation** — aura on core six, not targetable ([ADR 007](../../decisions/007-navigator-role.md)) |
| **Sortie** | Targetable; AGI queue; **player-controlled** like other summons ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **Synchro** | Sortie actions do not charge bar; **no Protocol** while sortie is alive; after sortie ends, Synchro may recharge for another Protocol |
| **UI** | Aux frame type **Summon**; portrait label = **Navigator display name** |
| **End** | Battle end, sortie HP 0 (recall), duration, or dismiss action |

Does **not** violate “Navigator fills aux slot” — the **summon** occupies the slot; Navigator identity stays in the off-formation strip ([ADR 023](../../decisions/023-protocol-deploy-sortie-summon.md)).

### MVP1 summon kit (`test_drone`)

Player picks commands on each drone AGI turn ([ADR 016](../../decisions/016-summon-control-mvp1.md)). Data on `SummonDefinition`:

```yaml
summon_id: test_drone
duration_rounds: 3
aux_row: back
skill_ids: [volt_burst]   # plus implicit Attack / Guard
# action_script: unused for MVP1 player summons
```

| Command | Rule |
|---------|------|
| **Attack** | Standard melee/ranged attack action |
| **Guard** | Self guard |
| **`volt_burst`** | `SkillDefinition` — Elemental, SingleEnemy ([mvp1-class-skills](../03-content/mvp1-class-skills.md#summon-kit-test_drone)) |

**UI on summon turn:** highlight aux portrait in strip + roster; **command panel** active (same path as core); presentation lock per [#35](https://github.com/miramocha/griddungeon-game/issues/35) when shipped.

**Synchro Charge:** Summon actions do **not** gain Synchro Charge ([synchro-protocol](synchro-protocol.md)). **Protocol** not offered on summon turns.

## Guests

| Property | Rule |
|----------|------|
| **Source** | Quests, story beats, floor scripts ("ally joins this fight") |
| **Placement** | Designer assigns front or back aux for the encounter |
| **Duration** | One battle, one floor, or until script removes guest |
| **Commands** | Player-controlled by default; **NPC guest** flag = AI-controlled (cutscenes, escort) |
| **AGI** | Guest enters turn queue |
| **XP** | No XP to guests (avoid leveling NPCs) |
| **Death** | Guest downed = unavailable for rest of fight; story may fail quest or use "retreat" script |
| **Exploration** | Guest does not walk the grid with party |

## Targeting & row rules

- Aux slots count as **front** or **back** for melee reach and row skills.
- Enemy melee without pierce targets **front row** (core + aux front) before any back slot.
- **Vanguard**-style guard skills affect allies in same row including aux.
- If aux front is empty, behavior matches classic 3+3.

## UI

- Core slots: standard portraits (6).
- Aux slots: distinct frame (e.g. border color) labeled **Summon** / **Guest**; empty aux slot hidden or shown dimmed.
- Turn queue shows aux icons mixed with party by AGI.

## MVP1

| Phase | Scope |
|-------|--------|
| **MVP1** | Aux slots + one test summon — **player-controlled** ([ADR 016](../../decisions/016-summon-control-mvp1.md)) |
| **MVP1+** | One scripted **guest** on a quest fight |
| **Later** | Multiple summon skills, enemy summons, guest roster |

## Related docs

- [Party & classes](party-and-classes.md)
- [Combat](combat.md)
- [ADR 004 — Auxiliary slots](../../decisions/004-auxiliary-slots.md)
- [ADR 016 — Summon control MVP1](../../decisions/016-summon-control-mvp1.md)
- [ADR 023 — Protocol Deploy sortie summon](../../decisions/023-protocol-deploy-sortie-summon.md)
